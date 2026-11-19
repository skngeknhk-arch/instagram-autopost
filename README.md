# Instagram 自動投稿（1日1回）

毎日 19:07（日本時間）ごろ、GitHub Actions が `state.json` の順番で次の品番を1件投稿します。
画像はその品番フォルダの全画像（最大10枚、カルーセル）、文章は `posts.json` の caption です。
一巡したら自動でランダムに並べ直します。

## ファイル
- `posts.json` … 品番・キャプション・画像ファイル名（品番ランダムリスト_改訂案.xlsx から作成）
- `state.json` … 投稿順と進み具合、直近60件の投稿履歴（投稿のたびに自動更新）
- `images/<品番>/` … 投稿画像
- `post.py` … 投稿スクリプト
- `.github/workflows/post.yml` … 毎日の実行設定（時刻は cron 行で変更）

## 初回設定
1. GitHub で **Public** リポジトリ `instagram-autopost` を作成（画像URLを Instagram が取りに行くため公開が必要）
2. このフォルダの中身をアップロード（GitHub Desktop 推奨。Web画面のアップロードは1回100ファイルまで）
3. リポジトリの Settings → Secrets and variables → Actions → New repository secret で2つ登録
   - `IG_ACCESS_TOKEN` … Instagram 投稿権限つきアクセストークン
   - `IG_USER_ID` … Instagram ビジネスアカウントのID（数字）
4. Actions タブ → Instagram daily post → Run workflow（dry_run=1）で、投稿予定の内容が表示されるか確認
5. dry_run=0 で1回手動実行し、実際に投稿されるか確認。以降は毎日自動

## 止めたいとき
Actions タブ → Instagram daily post → 右上「…」→ Disable workflow

## 商品を追加・キャプションを直すとき
`posts.json` を編集して保存（GitHub上で直接編集可）。画像は `images/<品番>/` に追加。順番には自動で組み込まれます。
