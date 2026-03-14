# Niconico Music Bot

ニコニコ動画の動画・マイリスト・シリーズを Discord で再生できる音楽 Bot です。

---

## 特徴

- **ニコニコ専用設計** — 単体動画・マイリスト・シリーズのすべての URL に対応
- **低メモリ動作** — 常駐時のメモリ使用量は約 100〜150MB。無料枠でDiscordBotを動せる環境でも安定動作
- **ストリーミング再生** — 音声をダウンロードせず yt-dlp → FFmpeg へ直接パイプするため、ディスクを使わない
- **自動パッケージ管理** — 初回起動時に必要なパッケージを自動インストール。`requirements.txt` のアップロードが不要
- **VC 自動退出** — ボイスチャンネルに誰もいなくなると自動で退出し、メモリを解放
- **ログイン対応** — `.env` にニコニコアカウントを設定することで、ログイン必須コンテンツ（デバイス規制の動画）も再生可能（サブアカウントの使用を強く推奨します）
- **エラー耐性** — 削除済み・視聴制限動画は自動スキップしてキューを継続。VC 接続失敗時は最大3回リトライ

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

## 注意事項

- **Bot はボイスチャンネルに参加した状態**で `!play` を実行してください
- プレミアム会員限定・削除済みの動画は自動でスキップされます
- ボイスチャンネルに誰もいなくなると Bot は自動で退出します
- VC への接続に失敗した場合は、もう一度 `!play` を試してください
