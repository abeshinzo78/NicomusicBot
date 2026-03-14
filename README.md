# Niconico Music Bot

ニコニコ動画の動画・マイリスト・シリーズを Discord で再生できる音楽 Bot です。

---

## 特徴

- **ニコニコ専用設計** — 単体動画・マイリスト・シリーズのすべての URL に対応
- **低メモリ動作** — 常駐時のメモリ使用量は約 100〜150MB。無料枠でDiscordBotを動かす環境でも安定動作
- **ストリーミング再生** — 音声をダウンロードせず yt-dlp → FFmpeg へ直接パイプするため、ディスクを使わない
- **自動パッケージ管理** — 初回起動時に必要なパッケージを自動インストール。`requirements.txt` のアップロードが不要
- **VC 自動退出** — ボイスチャンネルに誰もいなくなると自動で退出し、メモリを解放
- **ログイン対応** — `.env` にニコニコアカウントを設定することで、ログイン必須コンテンツ（デバイス規制の動画）も再生可能（サブアカウントの使用を強く推奨します）
- **エラー耐性** — 削除済み・視聴制限動画は自動スキップしてキューを継続。VC 接続失敗時は最大3回リトライ

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/abeshinzo78/nicomusicbot)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/abeshinzo78/nicomusicbot)


---

## コマンド一覧

### 🎵 再生する

```
!play <URL>
```

ニコニコ動画の URL を指定して再生します。
マイリストやシリーズの URL を指定すると、全曲をまとめてキューに追加します。

**例:**
```
!play https://www.nicovideo.jp/watch/sm12345678
!play https://www.nicovideo.jp/mylist/12345678
!play https://www.nicovideo.jp/series/12345678
```

> ボイスチャンネルに参加した状態で実行してください。

---

### ⏭️ 次の曲にスキップする

```
!skip
```

現在再生中の曲をスキップして、次の曲を再生します。

---

### 📋 キューを確認する

```
!queue
```

現在再生中の曲と、次に再生される曲の一覧を表示します。
タイトルをクリックするとニコニコ動画のページに飛べます。

**表示例:**
```
▶️ 再生中: 曲のタイトル

📋 キュー (3 件):
  1. 次の曲
  2. その次の曲
  3. さらにその次の曲
```

---

### ⏹️ 停止して退出する

```
!stop
```

再生を停止し、キューをクリアして Bot がボイスチャンネルから退出します。

---

## 技術仕様

### 使用ライブラリ

| ライブラリ | バージョン | 用途 |
|---|---|---|
| discord.py | 2.3.0 以上 | Discord Bot フレームワーク |
| yt-dlp | 2024.1.0 以上 | ニコニコ動画の情報取得・音声抽出 |
| PyNaCl | 1.5.0 以上 | 音声暗号化（discord.py の音声機能に必須） |
| python-dotenv | 1.0.0 以上 | `.env` ファイルの読み込み |
| FFmpeg | システム依存 | 音声デコード・ストリーミング |

### アーキテクチャ

```
!play URL
  └─ fetch_entries()        yt-dlp subprocess で動画情報を取得（--flat-playlist）
       └─ asyncio.Queue     エントリを軽量化（4フィールドのみ）してキューに積む
            └─ play_next()  キューから1件取り出し
                 └─ yt-dlp subprocess  音声を stdout にパイプ出力
                      └─ FFmpegPCMAudio(pipe=True)  Discord VC にストリーミング
```

### メモリ最適化の仕組み

- **yt-dlp をモジュールとしてインポートしない** — subprocess 経由で呼び出すことで、yt-dlp のモジュール常駐（約 20MB）を回避
- **エントリの軽量化** — yt-dlp が返す巨大な dict から `id` / `title` / `webpage_url` / `url` の4フィールドのみを保持
- **ストリーミング再生** — 音声をディスクに保存せず yt-dlp → FFmpeg へ直接パイプするため、ファイルキャッシュが発生しない
- **停止時にメモリ解放** — `!stop` および自動退出時に yt-dlp プロセスを強制終了し、`gc.collect()` でガベージコレクションを実行
- **パッケージの遅延インストール** — 未導入時のみ pip を実行し、再起動のたびに pip が走るコストを排除

### 対応 URL

| 種別 | URL 形式 |
|---|---|
| 単体動画 | `https://www.nicovideo.jp/watch/smXXXXXXXX` |
| マイリスト | `https://www.nicovideo.jp/mylist/XXXXXXXX` |
| シリーズ | `https://www.nicovideo.jp/series/XXXXXXXX` |

### エラーハンドリング

- 削除済み・視聴制限動画 → 自動スキップしてキューを継続
- VC 接続失敗 → 3秒間隔で最大3回リトライ
- URL 解決失敗 → ユーザーにメッセージを送信してスキップ

---

## セットアップ

### 1. Discord Bot の作成

1. [Discord Developer Portal](https://discord.com/developers/applications) を開く
2. **New Application** でアプリを作成
3. **Bot** タブ → `Token` をコピーしておく
4. **Privileged Gateway Intents** で以下を **ON** にする
   - `MESSAGE CONTENT INTENT`
   - `SERVER MEMBERS INTENT`

### 2. Bot をサーバーへ招待

1. **OAuth2 → URL Generator** を開く
2. `SCOPES` で `bot` にチェック
3. `BOT PERMISSIONS` で以下にチェック
   - `Send Messages` / `Read Message History`
   - `Connect` / `Speak` / `Use Voice Activity`
4. 生成された URL をブラウザで開き、サーバーを選択して招待

### 3. `.env` ファイルを作成

`main.py` と同じフォルダに `.env` を作成します：

```
DISCORD_TOKEN=取得したBotトークン

# ログイン必須コンテンツを再生する場合（省略可）
NICONICO_USER=ニコニコのメールアドレス
NICONICO_PASS=ニコニコのパスワード
```

### 4. 起動

`main.py` と `.env` をサーバーにアップロードして実行するだけです。
初回起動時に `discord.py`、`yt-dlp`、`PyNaCl` を自動インストールします。

> FFmpeg がサーバーにインストールされている必要があります。

---

# LICENCE

Unlicense license　なんで自由に改造して遊んでください。インターネットは自由な空間です。

## 注意事項

- **Bot はボイスチャンネルに参加した状態**で `!play` を実行してください
- プレミアム会員限定・削除済みの動画は自動でスキップされます
- ボイスチャンネルに誰もいなくなると Bot は自動で退出します
- VC への接続に失敗した場合は、もう一度 `!play` を試してください
