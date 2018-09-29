# lambda-headless-chrome
* headless-chromeを使用したlambda関数(python)のデプロイパッケージ

## 作業フォルダの作成
```
$ git clone https://github.com/takguchi/lambda-headless-chrome
$ cd lambda-headless-chrome
```

## lambda_function.py 作成
* 今回は以下を実行するlambda_function.py を作成
  * [データで楽しむプロ野球](http://baseballdata.jp/"データで楽しむプロ野球")から取得した試合結果サマリーをcsvファイルに出力する  
  * csvファイルをs3のバケット(バケット名：'npb-match-results')にアップロード

## serverless-chromiumのダウンロード
```
$ mkdir -p bin/
$ curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
$ unzip headless-chromium.zip -d bin/
$ rm headless-chromium.zip
```

## chromedriverのダウンロード
```
$ curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
$ unzip chromedriver.zip -d bin/
$ rm chromedriver.zip
```

## Dockerイメージのビルド
```
$ docker build -t lambda_headless_chrome .
```

## Dockerイメージをコンテナとして実行
```
$ docker run -v "${PWD}":/var/task lambda_headless_chrome
```
