# Niconico Music Bot

ニコニコ動画の単体動画・マイリスト・シリーズ・投稿者動画一覧・タグ検索結果を Discord のボイスチャンネルで再生する音楽 Bot です。
音声ファイルを一切ダウンロードせず、yt-dlp → FFmpeg → Discord VC へのパイプラインでリアルタイムにストリーミングします。

[![zread](https://img.shields.io/badge/Ask_Zread-_.svg?style=flat&color=00b0aa&labelColor=000000&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTQuOTYxNTYgMS42MDAxSDIuMjQxNTZDMS44ODgxIDEuNjAwMSAxLjYwMTU2IDEuODg2NjQgMS42MDE1NiAyLjI0MDFWNC45NjAxQzEuNjAxNTYgNS4zMTM1NiAxLjg4ODEgNS42MDAxIDIuMjQxNTYgNS42MDAxSDQuOTYxNTZDNS4zMTUwMiA1LjYwMDEgNS42MDE1NiA1LjMxMzU2IDUuNjAxNTYgNC45NjAxVjIuMjQwMUM1LjYwMTU2IDEuODg2NjQgNS4zMTUwMiAxLjYwMDEgNC45NjE1NiAxLjYwMDFaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00Ljk2MTU2IDEwLjM5OTlIMi4yNDE1NkMxLjg4ODEgMTAuMzk5OSAxLjYwMTU2IDEwLjY4NjQgMS42MDE1NiAxMS4wMzk5VjEzLjc1OTlDMS42MDE1NiAxNC4xMTM0IDEuODg4MSAxNC4zOTk5IDIuMjQxNTYgMTQuMzk5OUg0Ljk2MTU2QzUuMzE1MDIgMTQuMzk5OSA1LjYwMTU2IDE0LjExMzQgNS42MDE1NiAxMy43NTk5VjExLjAzOTlDNS42MDE1NiAxMC42ODY0IDUuMzE1MDIgMTAuMzk5OSA0Ljk2MTU2IDEwLjM5OTlaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik0xMy43NTg0IDEuNjAwMUgxMS4wMzg0QzEwLjY4NSAxLjYwMDEgMTAuMzk4NCAxLjg4NjY0IDEwLjM5ODQgMi4yNDAxVjQuOTYwMUMxMC4zOTg0IDUuMzEzNTYgMTAuNjg1IDUuNjAwMSAxMS4wMzg0IDUuNjAwMUgxMy43NTg0QzE0LjExMTkgNS42MDAxIDE0LjM5ODQgNS4zMTM1NiAxNC4zOTg0IDQuOTYwMVYyLjI0MDFDMTQuMzk4NCAxLjg4NjY0IDE0LjExMTkgMS42MDAxIDEzLjc1ODQgMS42MDAxWiIgZmlsbD0iI2ZmZiIvPgo8cGF0aCBkPSJNNCAxMkwxMiA0TDQgMTJaIiBmaWxsPSIjZmZmIi8%2BCjxwYXRoIGQ9Ik00IDEyTDEyIDQiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSIxLjUiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIvPgo8L3N2Zz4K&logoColor=ffffff)](https://zread.ai/abeshinzo78/nicomusicbot)

[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/abeshinzo78/nicomusicbot)

---

## 目次

> **Botの使い方** [コマンド一覧](#コマンド一覧) 

> **内部アーキテクチャ** | [概要](#アーキテクチャ概要) | [データ取得](#データ取得パイプライン) | [音声再生](#音声再生パイプライン) | [URL 正規化](#url-正規化) | [状態管理](#状態管理) | [レート制限](#レート制限とリトライ) | [音量制御](#音量制御) | [メモリ最適化](#メモリ最適化)

> **利用ガイド** | [ファイル構成](#ファイル構成) | [セットアップ](#セットアップ) | [LICENSE](#LICENSE)|[注意事項](#注意事項制限事項)

---


## コマンド一覧

| コマンド | 説明 | VC 必須 |
|---|---|---|
| `!play <URL>` | 単体動画 / マイリスト / シリーズ / 投稿者動画一覧を再生 | はい |
| `!tag <タグ名\|URL> [件数]` | タグ検索結果をキューに追加（デフォルト 30 件、最大 100 件） | はい |
| `!skip` | 現在の曲をスキップして次の曲を再生 | いいえ |
| `!queue` | 再生中の曲とキューの内容を表示（先頭 10 件 + 残件数） | いいえ |
| `!stop` | 再生停止・キュークリア・VC 切断・メモリ解放 | いいえ |
| `!volume [0-300]` | 音量の表示 / 設定（100% 超は増幅） | いいえ |
| `!mute` | ミュートのトグル（音量を退避して 0% に / 退避から復元） | いいえ |

### !play の対応 URL

| 種別 | 入力例 |
|---|---|
| 単体動画 | `https://www.nicovideo.jp/watch/sm9` |
| マイリスト | `https://www.nicovideo.jp/mylist/12345` |
| シリーズ | `https://www.nicovideo.jp/series/12345` |
| 投稿者の動画一覧 | `https://www.nicovideo.jp/user/12345/video` |
| 動画 ID のみ | `sm9` / `nm1234` |
| nico.ms 短縮 | `nico.ms/sm9` / `https://nico.ms/mylist/12345` |
| スマートフォン URL | `https://sp.nicovideo.jp/watch/sm9` |

### !tag の入力形式

| 入力例 | 解釈 |
|---|---|
| `!tag ボーカロイド` | タグ「ボーカロイド」で検索、最新 30 件 |
| `!tag ボーカロイド 10` | 最新 10 件に絞る |
| `!tag https://www.nicovideo.jp/tag/ボーカロイド` | URL からタグ名を自動抽出 |
| `!tag https://www.nicovideo.jp/tag/%E3%83%9C%E3%83%BC%E3%82%AB%E3%83%AD%E3%82%A4%E3%83%89` | URLエンコード済みでも可 |

---

## アーキテクチャ概要

Bot は **データ取得** と **音声再生** の 2 つのパイプラインで構成されます。

### データ取得パイプライン

```
!play <URL>
 |
 +--> normalize_niconico_url()    ... URL の形式差異を吸収
 |      www / sp / nico.ms / ID       (正規 URL に統一)
 |
 +--> fetch_entries()             ... yt-dlp subprocess
        (1) --flat-playlist         で高速取得
        (2) 空なら通常取得          にフォールバック
        (3) _slim()                 で 3 フィールドに圧縮
              |
              +-------+
                      |
!tag <タグ名>          |
 |                    |
 +--> _search_by_tag()            ... Snapshot Search API v2
        HTTP GET / 認証不要           (タグ完全一致, 投稿日時降順, 最大100件)
              |                   |
              +-------+-----------+
                      |
                      v
              asyncio.Queue に enqueue
              dict = { id, title, url }
```

### 音声再生パイプライン

```
play_next()  <-- キューから 1 件 dequeue
 |
 +-- タイトルが空 or 動画ID形式(smXXXX)?
 |    YES --> yt-dlp --dump-json で個別にメタデータ再取得
 |
 +-- yt-dlp subprocess
 |    -f bestaudio[abr<=128]/bestaudio
 |    --no-playlist -o -
 |    stdout にバイト列を出力
 |         |
 |         | pipe
 |         v
 |    FFmpegPCMAudio(pipe=True)    ... 生バイト列を PCM にデコード
 |         |
 |         v
 |    PCMVolumeTransformer         ... ソフトウェア音量 (0~300%)
 |         |
 |         v
 |    Discord VoiceClient          ... VC にリアルタイム送信
 |
 +-- 再生完了
      after_play() callback
       --> play_next() を再スケジュール (キューが空になるまでループ)
```


### 使用ライブラリ

| ライブラリ | バージョン | 用途 |
|---|---|---|
| discord.py | >= 2.3.0 | Discord Bot フレームワーク・音声送信 |
| yt-dlp | >= 2024.1.0 | ニコニコ動画の情報取得・音声バイト列の抽出 |
| PyNaCl | >= 1.5.0 | 音声暗号化（discord.py の Voice 機能が内部で使用） |
| python-dotenv | >= 1.0.0 | `.env` ファイルの読み込み |
| aiohttp | discord.py に同梱 | タグ検索 API 呼び出し・Discord API 疎通確認 |
| FFmpeg | システム依存 | 音声のデコード・PCM 変換 |

---

## データ取得パイプライン

Bot は入力の種類に応じて2つの異なるバックエンドからデータを取得します。

### 1. yt-dlp による動画・プレイリスト取得（`!play`）

単体動画・マイリスト・シリーズ・投稿者動画一覧には **yt-dlp** を subprocess として起動します。
yt-dlp を Python モジュールとしてインポートせず subprocess で呼び出す理由は、モジュール常駐による約 20MB のメモリ消費を回避するためです。

#### 取得の流れ

```
fetch_entries(url)
  │
  ├─ (1) yt-dlp --dump-json --flat-playlist <url>
  │       プレイリスト系 URL → エントリ一覧が JSON Lines で返る
  │       単体動画 URL → 何も返らないことがある
  │
  ├─ (2) 結果が空の場合 → yt-dlp --dump-json <url>
  │       --flat-playlist なしで再取得（単体動画フォールバック）
  │
  └─ 各行の JSON を _slim() で { id, title, url } の 3 フィールドに圧縮
```

#### `--flat-playlist` とは

通常 yt-dlp がプレイリストを処理する場合、各動画の詳細ページに1件ずつアクセスしてメタデータ（再生数・コメント数・サムネイルなど）を取得します。`--flat-playlist` はこれをスキップし、プレイリストの目次ページから得られる最小限の情報（動画 ID とタイトル）のみを返します。

- 利点：100 件のプレイリストが通常数分かかるところを数秒で取得できる
- 欠点：タイトルが動画 ID（`smXXXX`）のままになる場合がある

タイトルが ID のままだった場合は、`play_next()` で再生直前に個別メタデータ取得を行います（後述）。

#### 対応する URL と各入力の内部処理

| 種別 | 入力例 | 内部処理 |
|---|---|---|
| 単体動画 | `https://www.nicovideo.jp/watch/sm9` | `--flat-playlist` が空 → 通常取得にフォールバック |
| マイリスト | `https://www.nicovideo.jp/mylist/12345` | `--flat-playlist` でエントリ一覧を一括取得 |
| シリーズ | `https://www.nicovideo.jp/series/12345` | 同上 |
| 投稿者の動画一覧 | `https://www.nicovideo.jp/user/12345/video` | 同上（動画数に上限なし。数百〜数千件の場合あり） |

#### ニコニコ認証

`.env` に `NICONICO_USER` / `NICONICO_PASS` が設定されている場合、yt-dlp に `--username` / `--password` を渡します。これにより、ログイン必須コンテンツ（一部の限定公開動画）も再生可能になります。

---

### 2. Niconico Snapshot Search API によるタグ検索（`!tag`）

yt-dlp はニコニコのタグページ（`/tag/...`）をプレイリストとして認識しません。これは yt-dlp のニコニコ対応がマイリスト・シリーズ・ユーザー動画などの「プレイリスト型 URL」に限定されているためです。

そこでタグ検索には **ニコニコデータ村（Niconico Data Village）が提供するスナップショット検索 API v2** を直接使用しています。

#### API 仕様

```
GET https://snapshot.search.nicovideo.jp/api/v2/snapshot/video/contents/search
```

| パラメータ | 値 | 説明 |
|---|---|---|
| `q` | タグ名の文字列 | 検索クエリ |
| `targets` | `tags` | 検索対象をタグに限定（`tags` = タグ名完全一致） |
| `fields` | `contentId,title` | レスポンスに含めるフィールド |
| `_sort` | `-startTime` | ソート順（`-` = 降順、`startTime` = 投稿日時） |
| `_limit` | `1`〜`100` | 取得件数（デフォルト 30、最大 100） |
| `_context` | `NiconicoBotSearch` | API 利用元の識別子（任意文字列、利用規約で推奨） |

#### レスポンス例

```json
{
  "meta": { "status": 200, "totalCount": 42 },
  "data": [
    { "contentId": "sm12345678", "title": "動画タイトル" },
    { "contentId": "sm87654321", "title": "別の動画" }
  ]
}
```

`contentId` は動画 ID（`smXXXX`）で、これを `{ id: "sm12345678", title: "動画タイトル" }` の dict に変換してキューに積みます。

#### タグ URL の自動解析

`!tag` にタグページの URL が渡された場合は、パスからタグ名を自動抽出します。

```
入力: https://www.nicovideo.jp/tag/%E3%83%9C%E3%83%BC%E3%82%AB%E3%83%AD%E3%82%A4%E3%83%89
  ↓ "/tag/" で分割 → "%E3%83%9C%E3%83%BC%E3%82%AB%E3%83%AD%E3%82%A4%E3%83%89"
  ↓ "?" で分割（クエリパラメータ除去）
  ↓ urllib.parse.unquote()
  → "ボーカロイド"
```

Discord がメッセージ中の URL を `<...>` で囲むケースがあるため、前後の `<>` を先に strip してから解析します。

#### yt-dlp ではなく Snapshot Search API を使う理由

| 比較項目 | yt-dlp | Snapshot Search API |
|---|---|---|
| タグページ対応 | 非対応（プレイリストとして認識しない） | 公式 API で対応 |
| 認証 | 不要〜場合により必要 | 常に不要 |
| 件数制限 | 制御不可 | `_limit` で 1〜100 件を指定可能 |
| ソート | 制御不可 | 投稿日時・再生数など複数キーから選択可能 |
| レスポンス速度 | HTML スクレイピングのため遅い | REST API のため高速（< 1 秒） |

---

## 音声再生パイプライン

### play_next() の処理フロー

`play_next()` はキューから 1 件取り出し、以下の手順で再生を開始します。

```
play_next(state, channel)
  │
  ├─ 1. ガード条件チェック
  │     - _states にこの GuildState がまだ存在するか（!stop で破棄されていないか）
  │     - VoiceClient が接続中か
  │     - 既に再生中でないか
  │     - キューが空でないか
  │
  ├─ 2. キューから entry を dequeue
  │
  ├─ 3. make_video_url(entry) で動画 URL を組み立て
  │     entry["id"]（最優先）→ entry["url"] → entry["webpage_url"] の順にフォールバック
  │     normalize_niconico_url() で正規化
  │     URL が組み立てられなければスキップして再帰
  │
  ├─ 4. タイトル解決
  │     title が空 or _is_video_id(title) が True の場合
  │     → yt-dlp --dump-json --no-playlist <url> で個別にメタデータを再取得
  │     _is_video_id(): "sm" / "nm" / "so" 等のプレフィックス + 数字のみで構成される文字列を検出
  │
  ├─ 5. generation カウンタをインクリメント（後述の競合防止に使用）
  │
  ├─ 6. yt-dlp subprocess を起動
  │     yt-dlp -q -f "bestaudio[abr<=128]/bestaudio" --no-playlist -o - <url>
  │     stdout = PIPE, stderr = DEVNULL
  │     → stdout からバイト列が流れ出す
  │
  ├─ 7. FFmpegPCMAudio(pipe=True) で stdout をラップ
  │     FFmpeg が生の音声バイト列を 48kHz 16bit stereo PCM にデコード
  │
  ├─ 8. PCMVolumeTransformer でさらにラップ（初期音量 = state.volume）
  │
  └─ 9. voice_client.play(source, after=after_play) で再生開始
```

### after_play() コールバック

再生が終了すると FFmpeg のスレッドから `after_play()` が呼ばれます。

```
after_play(err)
  │
  ├─ generation が変わっていたら → 無視（!skip 等で世代が進んだ古い callback）
  │
  ├─ 再生時間が 3 秒未満 → ストリームエラーとみなして停止（無限ループ防止）
  │
  └─ 正常終了 → asyncio.run_coroutine_threadsafe() で play_next() をスケジュール
```

#### generation カウンタの役割

`!skip` で曲をスキップすると `voice_client.stop()` が呼ばれ、前の曲の `after_play()` が発火します。
このとき generation を比較することで、「古い曲の callback で意図せず play_next() が二重に呼ばれる」問題を防止しています。

#### 3 秒ルール

ニコニコ動画で削除済み・視聴制限の動画にアクセスした場合、yt-dlp は空のストリームを返すか即座にエラー終了します。この場合 FFmpeg も即座に終了するため `after_play()` が呼ばれます。3 秒未満の再生を検出した場合はストリームエラーとみなしてキューの処理を停止し、無限ループ（dequeue → 即終了 → dequeue → …）を防止します。

### 音声フォーマット選択

```
-f "bestaudio[abr<=128]/bestaudio"
```

ABR（平均ビットレート）128kbps 以下の最良音声を優先選択し、なければ任意の最良音声を使用します。128kbps 以上の音声は Discord Voice の仕様上意味がなく、帯域とメモリを無駄に消費するため上限を設けています。

---

## URL 正規化

`normalize_niconico_url()` はユーザーが入力した多様な形式のニコニコ URL を `https://www.nicovideo.jp/...` の正規形に統一します。

| 入力例 | 変換後 |
|---|---|
| `sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `nm1234` | `https://www.nicovideo.jp/watch/nm1234` |
| `nico.ms/sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `https://nico.ms/sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `https://nico.ms/mylist/12345` | `https://www.nicovideo.jp/mylist/12345` |
| `https://sp.nicovideo.jp/watch/sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `sp.nicovideo.jp/watch/sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `nicovideo.jp/watch/sm9` | `https://www.nicovideo.jp/watch/sm9` |
| `https://nicovideo.jp/watch/sm9` | `https://www.nicovideo.jp/watch/sm9` |

#### 認識する動画 ID プレフィックス

`sm`, `nm`, `so`, `ax`, `yo`, `nl`, `ig`, `na`, `cw`, `zb`, `z9`

これらの 2 文字プレフィックス + 数字のみで構成される文字列が入力された場合、動画 ID と判定して `https://www.nicovideo.jp/watch/` を付与します。

---

## 状態管理

### GuildState

ギルド（Discord サーバー）ごとに 1 つの `GuildState` インスタンスが生成され、`_states: dict[int, GuildState]` に保持されます。

| フィールド | 型 | 説明 |
|---|---|---|
| `queue` | `asyncio.Queue[dict]` | 再生待ちキュー。各要素は `{ id, title, url }` の dict |
| `current` | `dict \| None` | 現在再生中のエントリ |
| `voice_client` | `VoiceClient \| None` | Discord VC への接続 |
| `ytdlp_proc` | `Popen \| None` | 再生中の yt-dlp 子プロセス |
| `_play_next_lock` | `asyncio.Lock` | play_next() の排他制御（二重再生防止） |
| `_generation` | `int` | after_play callback の世代管理 |
| `volume` | `float` | 現在の音量（0.0〜3.0、デフォルト 1.0 = 100%） |
| `_saved_volume` | `float \| None` | ミュート前の音量（ミュート解除時に復元） |

### ライフサイクル

```
get_state(guild_id)    ← 初回アクセス時に GuildState を生成
       ↓
  !play / !tag で queue に追加 → play_next() で順次再生
       ↓
  !stop  or  VC が空になる
       ↓
  _states.pop(guild_id)   ← GuildState を破棄
  gc.collect()             ← ガベージコレクション強制実行
```

---

## レート制限とリトライ

### Discord メッセージ送信（safe_send）

Discord API から `429 Too Many Requests` が返された場合、**指数バックオフ**でリトライします。

```
試行 1: 即時送信
試行 2: 10 秒待機後にリトライ
試行 3: 20 秒待機後にリトライ
試行 4: 40 秒待機後にリトライ
```

最大 4 回試行し、それでも失敗した場合はログにエラーを記録して諦めます。

### Discord API 疎通確認（_wait_for_discord_api）

`bot.start()` を呼ぶ前に `GET /api/v10/users/@me` で疎通を確認します。
429 が返された場合は 60 秒 → 120 秒 → 180 秒 → 240 秒 → 300 秒と段階的に待機して再試行します（最大 5 回）。

### VC 接続リトライ

ボイスチャンネルへの接続が例外で失敗した場合、2 秒間隔で最大 3 回リトライします。

---

## 音量制御

音量は `discord.PCMVolumeTransformer` によるソフトウェア制御で実現しています。

### !volume

- 引数なし → 現在の音量を表示
- 引数あり（0〜300）→ `state.volume` を更新し、再生中であれば `source.volume` にも即時反映
- 100% を超える値（101〜300%）は PCM サンプルを増幅するため、音割れの可能性あり

### !mute

- トグル動作：ミュート ↔ ミュート解除
- ミュート時：`state._saved_volume` に現在の音量を退避してから `volume = 0.0` に設定
- ミュート解除時：`_saved_volume` から復元（退避がなければ 100% にリセット）
- VC に参加していなくても実行可能。次の再生から反映される

---

## メモリ最適化

このBotは 200MB 制限の KEITO Cloud で安定動作するため、以下の最適化を行っています。

| 手法 | 削減効果 | 詳細 |
|---|---|---|
| yt-dlp subprocess 方式 | 約 20MB 削減 | モジュールインポートではなく subprocess で呼び出し、使用後にプロセス終了 |
| エントリ軽量化 | 数 MB 削減 | yt-dlp の巨大な dict（50+ フィールド）から 3 フィールドのみ保持 |
| ストリーミング再生 | ディスク 0、メモリ微量 | stdout パイプで逐次処理。音声データをバッファに蓄積しない |
| 停止時のクリーンアップ | 全量回収 | yt-dlp プロセス kill → GuildState 破棄 → gc.collect() |
| 遅延パッケージインストール | 起動時間削減 | 未導入時のみ pip を実行。既にインストール済みなら何もしない |

---

## ファイル構成

```
niconicomusicBOT/
├── main.py          フル機能版（KEITO Cloud API 監視・プロキシ対応を含む）
├──LICENSE           Unlicense license 
└── README.md        本ドキュメント
```


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

以下の URL の `CLIENT_ID` を自分の Bot の Application ID に置き換えてブラウザで開きます：

```
https://discord.com/oauth2/authorize?client_id=CLIENT_ID&scope=bot&permissions=3145728
```

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

## LICENSE

Unlicense license　なんで自由に改造して遊んでください。インターネットは自由な空間です。

## 注意事項・制限事項

- `!play` / `!tag` はボイスチャンネルに参加した状態で実行してください
- `!volume` / `!mute` / `!skip` / `!queue` / `!stop` はボイスチャンネル外からも実行できます
- プレミアム会員限定・削除済みの動画は自動でスキップされます
- 投稿者動画一覧は全件キューに積まれます（数百〜数千件になる場合あり）
- タグ検索は完全一致です。部分一致やキーワード検索には対応していません
- 音量 101〜300% は PCM を増幅するため、音割れが発生する可能性があります
- ボイスチャンネルに誰もいなくなると Bot は自動で退出し、メモリを解放します
- VC への接続に失敗した場合は、もう一度 `!play` を試してください
- `.env` にはパスワード等が含まれるため、Git にアップロードしないよう注意してください
