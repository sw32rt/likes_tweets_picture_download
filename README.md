# likes_tweets_picture_download

twitterでいいねした画像付きツイートの画像を./downloadsにダウンロードします。

1.twitter APIのトークンを発行します。BEARERトークンのみ使用するのでそれ以外はいりません。

2.token_template.jsonをtoken.jsonにリネームします。

2.token.jsonの"BEARER_TOKEN"に発行したトークンを張り付けます。
  ***注意*** TOKENの書かれたtoken.jsonは第三者に見られないようにしてください。公開リポジトリにpushする等しないようにお気を付けください。

3.token.jsonの"USER_NAME"に@を抜いたtwitterアカウントID(=username)を張り付けます。

4.実行します。./downloadsに画像が保存されていれば成功です。


ソースコード綺麗ではないのでプルリクくれると嬉しいです。
