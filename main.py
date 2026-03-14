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

# ── 状態管理 ──────────────────────────────────────────────────────────────────
class GuildState:
    """ギルドごとの再生状態を保持する"""
    def __init__(self):
        self.queue: asyncio.Queue[dict] = asyncio.Queue()
        self.current: dict | None = None
        self.voice_client: discord.VoiceClient | None = None
        self.ytdlp_proc: subprocess.Popen | None = None
        self._play_next_lock = asyncio.Lock()

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
    return {k: entry[k] for k in ("id", "title", "webpage_url", "url") if entry.get(k)}


async def fetch_entries(url: str) -> list[dict]:
    """yt-dlp subprocess で URL からエントリ一覧を取得する"""
    auth_args = []
    if os.environ.get("NICONICO_USER"):
        auth_args = ["--username", os.environ["NICONICO_USER"],
                     "--password", os.environ["NICONICO_PASS"]]

    proc = await asyncio.create_subprocess_exec(
        "yt-dlp", "--dump-json", "--flat-playlist", "-q", "--ignore-errors", *auth_args, url,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
    )
    stdout, _ = await proc.communicate()

    entries = []
    for line in stdout.splitlines():
        try:
            entry = json.loads(line)
            entries.append(_slim(entry))
        except json.JSONDecodeError:
            continue

    if len(entries) > 1:
        log.info("プレイリスト検出: %d 件", len(entries))
    return entries


def make_video_url(entry: dict) -> str | None:
    """エントリから動画の URL を組み立てる"""
    video_url = entry.get("webpage_url") or entry.get("url") or entry.get("id")
    if not video_url:
        return None
    if not video_url.startswith("http"):
        video_url = f"https://www.nicovideo.jp/watch/{video_url}"
    return video_url


async def play_next(state: GuildState, channel: discord.TextChannel) -> None:
    """キューから次の曲を再生する"""
    async with state._play_next_lock:
        if state.voice_client is None or not state.voice_client.is_connected():
            return
        if state.queue.empty():
            state.current = None
            log.info("キューが空になりました")
            return

        entry = await state.queue.get()
        title = entry.get("title") or entry.get("id") or "不明"
        video_url = make_video_url(entry)

        if video_url is None:
            await channel.send(f"⚠️ `{title}` の URL が取得できませんでした。スキップします。")
            asyncio.ensure_future(play_next(state, channel))
            return

        log.info("再生開始: %s", title)
        state.current = entry

        loop = asyncio.get_event_loop()

        def after_play(err):
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
        await channel.send(f"▶️ 再生中: **[{title}]({video_url})**")


# ── Bot セットアップ ───────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    log.info("ログイン完了: %s (ID: %s)", bot.user, bot.user.id)


# ── コマンド ──────────────────────────────────────────────────────────────────
@bot.command(name="play")
async def cmd_play(ctx: commands.Context, url: str):
    """!play <URL>  ─ 単体動画 / マイリスト / シリーズを再生"""
    if ctx.author.voice is None:
        await ctx.send("ボイスチャンネルに参加してから実行してください。")
        return

    state = get_state(ctx.guild.id)

    vc = ctx.author.voice.channel
    if state.voice_client is None or not state.voice_client.is_connected():
        for attempt in range(1, 4):
            try:
                state.voice_client = await vc.connect(timeout=60, reconnect=True)
                break
            except Exception as e:
                log.warning("VC 接続失敗 (試行 %d/3): %s", attempt, e)
                if attempt == 3:
                    await ctx.send("⚠️ ボイスチャンネルへの接続に失敗しました。もう一度 `!play` を試してください。")
                    return
                await asyncio.sleep(3)
    elif state.voice_client.channel != vc:
        await state.voice_client.move_to(vc)

    await ctx.send(f"🔍 取得中: {url}")
    entries = await fetch_entries(url)

    if not entries:
        await ctx.send("⚠️ 動画が見つかりませんでした。URL を確認してください。")
        return

    for entry in entries:
        await state.queue.put(entry)

    await ctx.send(f"✅ {len(entries)} 件をキューに追加しました。")

    if not state.voice_client.is_playing() and not state.voice_client.is_paused():
        await play_next(state, ctx.channel)


@bot.command(name="skip")
async def cmd_skip(ctx: commands.Context):
    """!skip  ─ 現在の曲をスキップ"""
    state = get_state(ctx.guild.id)
    if state.voice_client and state.voice_client.is_playing():
        state.voice_client.stop()
        await ctx.send("⏭️ スキップしました。")
    else:
        await ctx.send("現在再生中の曲はありません。")


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
            lines.append(f"  {i}. {entry.get('title', entry.get('id', '不明'))}")
        if len(items) > 10:
            lines.append(f"  … 他 {len(items) - 10} 件")
    else:
        lines.append("キューは空です。")

    await ctx.send("\n".join(lines))


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
    await ctx.send("⏹️ 停止してボイスチャンネルから切断しました。")


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
if __name__ == "__main__":
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(".env ファイルに DISCORD_TOKEN が設定されていません")
    bot.run(token, log_handler=None)
