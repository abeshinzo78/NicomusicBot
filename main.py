import subprocess
import sys

# ── パッケージ確認・インストール（未導入時のみ）────────────────────────────────
def _ensure_packages():
    try:
        import discord, nacl, dotenv  # noqa: F401
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q",
            "--break-system-packages", "--no-cache-dir",
            "discord.py>=2.3.0", "yt-dlp>=2024.1.0", "PyNaCl>=1.5.0", "python-dotenv>=1.0.0"])

_ensure_packages()

import asyncio
import gc
import json
import logging
import os
import time

from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands

# ── ロギング ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── FFmpeg オプション ─────────────────────────────────────────────────────────
FFMPEG_OPTIONS = {"options": "-vn"}


# ── レート制限対応 send ───────────────────────────────────────────────────────
async def safe_send(target, content: str) -> None:
    """429 を受けたとき指数バックオフでリトライする send ラッパー"""
    for attempt in range(4):
        try:
            await target.send(content)
            return
        except discord.errors.HTTPException as e:
            if e.status == 429 and attempt < 3:
                wait = 10 * (2 ** attempt)  # 10 → 20 → 40 秒
                log.warning("送信レート制限。%d 秒後にリトライ (%d/3)", wait, attempt + 1)
                await asyncio.sleep(wait)
            else:
                log.error("メッセージ送信失敗: %s", e)
                return

# ── 状態管理 ──────────────────────────────────────────────────────────────────
class GuildState:
    """ギルドごとの再生状態を保持する"""
    def __init__(self):
        self.queue: asyncio.Queue[dict] = asyncio.Queue()
        self.current: dict | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.ytdlp_proc: subprocess.Popen | None = None
        self._play_next_lock = asyncio.Lock()
        self._generation = 0

    def kill_ytdlp(self):
        """再生中の yt-dlp プロセスを終了する"""
        if self.ytdlp_proc and self.ytdlp_proc.poll() is None:
            self.ytdlp_proc.kill()
            self.ytdlp_proc.wait()
        self.ytdlp_proc = None


_states: dict[int, GuildState] = {}


def get_state(guild_id: int) -> GuildState:
    if guild_id not in _states:
        _states[guild_id] = GuildState()
    return _states[guild_id]


# ── 音声ロジック ──────────────────────────────────────────────────────────────
def _slim(entry: dict) -> dict:
    """必要なフィールドだけ残して dict を軽量化する"""
    return {k: entry[k] for k in ("id", "title", "url") if entry.get(k)}


async def _run_ytdlp_json(args: list) -> list[dict]:
    """yt-dlp を実行して JSON 出力をパースして返す"""
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp", *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    stdout, _ = await proc.communicate()
    entries = []
    for line in stdout.splitlines():
        try:
            entries.append(_slim(json.loads(line)))
        except json.JSONDecodeError:
            continue
    return entries


async def fetch_entries(url: str) -> list[dict]:
    """yt-dlp subprocess で URL からエントリ一覧を取得する"""
    auth_args = []
    if os.environ.get("NICONICO_USER"):
        auth_args = ["--username", os.environ["NICONICO_USER"],
                     "--password", os.environ["NICONICO_PASS"]]

    base_args = ["--dump-json", "-q", "--ignore-errors", *auth_args]

    # まずプレイリスト向けの高速取得を試みる
    entries = await _run_ytdlp_json([*base_args, "--flat-playlist", url])

    # 単体動画では --flat-playlist が何も返さない場合があるので再試行
    if not entries:
        entries = await _run_ytdlp_json([*base_args, url])

    if len(entries) > 1:
        log.info("プレイリスト検出: %d 件", len(entries))
    return entries


_VIDEO_ID_PREFIXES = ("sm", "nm", "so", "ax", "yo", "nl", "ig", "na", "cw", "zb", "z9")


def normalize_niconico_url(url: str) -> str:
    """様々な形式のニコニコ URL・ID を正規化する"""
    url = url.strip()

    # https://nico.ms/... → スキーム除去して nico.ms/ で再処理
    if url.startswith("https://nico.ms/") or url.startswith("http://nico.ms/"):
        url = url.split("://", 1)[1]

    # sm1234 / nm1234 など ID のみ
    if url.startswith(_VIDEO_ID_PREFIXES):
        return f"https://www.nicovideo.jp/watch/{url}"

    # nico.ms/sm1234 → 単体動画
    # nico.ms/mylist/1234 → マイリスト
    if url.startswith("nico.ms/"):
        path = url[len("nico.ms/"):]
        if path.startswith(_VIDEO_ID_PREFIXES):
            return f"https://www.nicovideo.jp/watch/{path}"
        return f"https://www.nicovideo.jp/{path}"

    # sp.nicovideo.jp → www に統一
    url = url.replace("://sp.nicovideo.jp", "://www.nicovideo.jp")
    if url.startswith("sp.nicovideo.jp"):
        return "https://www." + url[len("sp."):]

    # スキームなし (nicovideo.jp/... または www.nicovideo.jp/...)
    if not url.startswith("http"):
        if url.startswith("nicovideo.jp"):
            return "https://www." + url
        return "https://" + url

    # スキームあり・www なし (https://nicovideo.jp/...) → www 付きに統一
    if url.startswith("https://nicovideo.jp") or url.startswith("http://nicovideo.jp"):
        url = url.replace("://nicovideo.jp", "://www.nicovideo.jp", 1)

    return url


def make_video_url(entry: dict) -> str | None:
    """エントリから動画の URL を組み立てる（id を最優先して個別動画を確実に取得）"""
    video_url = entry.get("id") or entry.get("url") or entry.get("webpage_url")
    if not video_url:
        return None
    return normalize_niconico_url(video_url)


async def play_next(state: GuildState, channel: discord.TextChannel) -> None:
    """キューから次の曲を再生する"""
    async with state._play_next_lock:
        # !stop で state が破棄されていたら何もしない
        if _states.get(channel.guild.id) is not state:
            return
        if state.voice_client is None or not state.voice_client.is_connected():
            return
        if state.voice_client.is_playing():
            return
        if state.queue.empty():
            state.current = None
            log.info("キューが空になりました")
            return

        entry = await state.queue.get()
        video_url = make_video_url(entry)

        if video_url is None:
            title = entry.get("title") or entry.get("id") or "不明"
            await safe_send(channel, f"⚠️ `{title}` の URL が取得できませんでした。スキップします。")
            asyncio.ensure_future(play_next(state, channel))
            return

        # タイトルが未取得（flat-playlist でスキップされた場合）なら個別に取得する
        title = entry.get("title")
        if not title:
            meta = await _run_ytdlp_json(["--dump-json", "-q", "--no-playlist", video_url])
            if meta:
                title = meta[0].get("title")
                entry["title"] = title
        title = title or entry.get("id") or "不明"

        log.info("再生開始: %s", title)
        state.current = entry
        state._generation += 1
        gen = state._generation
        started_at = time.monotonic()

        loop = asyncio.get_event_loop()

        def after_play(err):
            # 古い世代の callback なら無視
            if state._generation != gen:
                return
            # 3秒未満で終了した場合はストリームエラーとみなして停止
            elapsed = time.monotonic() - started_at
            if elapsed < 3:
                log.warning("再生が %.1f秒で終了 - ストリームエラーの可能性があります", elapsed)
                return
            if err:
                log.error("再生エラー: %s", err)
            asyncio.run_coroutine_threadsafe(play_next(state, channel), loop)

        # yt-dlp をパイプして FFmpeg に直接渡す
        auth_args = []
        if os.environ.get("NICONICO_USER"):
            auth_args = ["--username", os.environ["NICONICO_USER"],
                         "--password", os.environ["NICONICO_PASS"]]

        state.kill_ytdlp()
        ytdlp_proc = subprocess.Popen(
            ["yt-dlp", "-q", "-f", "bestaudio[abr<=128]/bestaudio",
             "--no-playlist", "-o", "-", *auth_args, video_url],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
        )
        state.ytdlp_proc = ytdlp_proc
        source = discord.FFmpegPCMAudio(ytdlp_proc.stdout, pipe=True, **FFMPEG_OPTIONS)
        state.voice_client.play(source, after=after_play)
        await safe_send(channel, f"▶️ 再生中: **[{title}]({video_url})**")


# ── Bot セットアップ ───────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

_proxy = os.environ.get("DISCORD_PROXY") or None
bot = commands.Bot(command_prefix="!", intents=intents, max_messages=100, proxy=_proxy)


@bot.event
async def on_ready():
    log.info("ログイン完了: %s (ID: %s)", bot.user, bot.user.id)


# ── コマンド ──────────────────────────────────────────────────────────────────
@bot.command(name="play")
async def cmd_play(ctx: commands.Context, url: str):
    """!play <URL>  ─ 単体動画 / マイリスト / シリーズを再生"""
    if ctx.author.voice is None:
        await safe_send(ctx, "ボイスチャンネルに参加してから実行してください。")
        return

    state = get_state(ctx.guild.id)

    vc = ctx.author.voice.channel
    if state.voice_client is None or not state.voice_client.is_connected():
        for attempt in range(1, 4):
            try:
                state.voice_client = await vc.connect(timeout=20, reconnect=False)
                break
            except Exception as e:
                log.warning("VC 接続失敗 (試行 %d/3): %s", attempt, e)
                if attempt == 3:
                    await safe_send(ctx, "⚠️ ボイスチャンネルへの接続に失敗しました。もう一度 `!play` を試してください。")
                    return
                await asyncio.sleep(2)
    elif state.voice_client.channel != vc:
        await state.voice_client.move_to(vc)

    url = normalize_niconico_url(url)
    entries = await fetch_entries(url)

    if not entries:
        await safe_send(ctx, "⚠️ 動画が見つかりませんでした。URL を確認してください。")
        return

    for entry in entries:
        await state.queue.put(entry)

    if len(entries) > 1:
        await safe_send(ctx, f"✅ {len(entries)} 件をキューに追加しました。")

    if not state.voice_client.is_playing() and not state.voice_client.is_paused():
        await play_next(state, ctx.channel)


@bot.command(name="skip")
async def cmd_skip(ctx: commands.Context):
    """!skip  ─ 現在の曲をスキップ"""
    state = get_state(ctx.guild.id)
    if state.voice_client and state.voice_client.is_playing():
        state.voice_client.stop()
        await safe_send(ctx, "⏭️ スキップしました。")
    else:
        await safe_send(ctx, "現在再生中の曲はありません。")


@bot.command(name="queue")
async def cmd_queue(ctx: commands.Context):
    """!queue  ─ キューの内容を表示"""
    state = get_state(ctx.guild.id)
    items = list(state.queue._queue)

    lines = []
    if state.current:
        cur = state.current
        cur_url = make_video_url(cur) or ""
        cur_title = cur.get("title") or cur.get("id") or "不明"
        lines.append(f"▶️ 再生中: **[{cur_title}]({cur_url})**" if cur_url else f"▶️ 再生中: **{cur_title}**")
    if items:
        lines.append(f"\n📋 キュー ({len(items)} 件):")
        for i, entry in enumerate(items[:10], 1):
            t = entry.get("title") or entry.get("id") or "不明"
            u = make_video_url(entry)
            lines.append(f"  {i}. [{t}]({u})" if u else f"  {i}. {t}")
        if len(items) > 10:
            lines.append(f"  … 他 {len(items) - 10} 件")
    else:
        lines.append("キューは空です。")

    await safe_send(ctx, "\n".join(lines))


@bot.command(name="stop")
async def cmd_stop(ctx: commands.Context):
    """!stop  ─ 再生停止・キュークリア・切断"""
    state = get_state(ctx.guild.id)
    while not state.queue.empty():
        state.queue.get_nowait()
    state.current = None
    state.kill_ytdlp()

    if state.voice_client:
        state.voice_client.stop()
        await state.voice_client.disconnect()
        state.voice_client = None

    _states.pop(ctx.guild.id, None)
    gc.collect()
    await safe_send(ctx, "⏹️ 停止してボイスチャンネルから切断しました。")


# ── 自動切断（ボイスチャンネルが空になったとき）──────────────────────────────
@bot.event
async def on_voice_state_update(
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState,
):
    if member.bot:
        return

    state = get_state(member.guild.id)
    vc = state.voice_client
    if vc is None or not vc.is_connected():
        return

    non_bot_members = [m for m in vc.channel.members if not m.bot]
    if len(non_bot_members) == 0:
        log.info("ボイスチャンネルが空になったため切断します")
        state.kill_ytdlp()
        vc.stop()
        await vc.disconnect()
        _states.pop(member.guild.id, None)
        gc.collect()


# ── エントリポイント ───────────────────────────────────────────────────────────
async def _wait_for_discord_api(token: str) -> None:
    """bot.start() を呼ぶ前に Discord API の疎通確認を行い、レート制限中なら待機する"""
    import aiohttp
    url = "https://discord.com/api/v10/users/@me"
    headers = {"Authorization": f"Bot {token}"}
    timeout = aiohttp.ClientTimeout(total=10)
    for attempt in range(1, 6):
        try:
            async with aiohttp.ClientSession() as sess:
                async with sess.get(url, headers=headers, timeout=timeout, proxy=_proxy) as r:
                    if r.status != 429:
                        return
            wait = 60 * attempt
            log.warning("レート制限中。%d 秒後に再試行します (試行 %d/5)", wait, attempt)
            await asyncio.sleep(wait)
        except Exception as e:
            log.warning("API 疎通確認スキップ: %s", e)
            return


async def main():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(".env ファイルに DISCORD_TOKEN が設定されていません")
    await _wait_for_discord_api(token)
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
