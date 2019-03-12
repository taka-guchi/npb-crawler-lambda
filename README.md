# npb-crawler-lambda
* headless-chromiumを使用したAWSLambda関数(python)のデプロイパッケージ
  * [データで楽しむプロ野球](http://baseballdata.jp/"データで楽しむプロ野球")から取得した**当年の**試合結果サマリーをcsvファイルに出力する  
  * csvファイルをs3のバケットにアップロード

## 作業フォルダの作成
```
$ git clone https://github.com/takguchi/npb-crawler-lambda
$ cd npb-crawler-lambda
```

## headless-chromiumのダウンロード
* [serverless-chrome](https://github.com/adieuadieu/serverless-chrome/releases"serverless-chrome") というLambda上で動くheadless-chromiumを使う
* pythonで動くバージョン([v1.0.0-37](https://github.com/adieuadieu/serverless-chrome/releases/tag/v1.0.0-37"v1.0.0-37")) を入れる
* もしかしたら最新版でも動くようになってるかも([参照](https://github.com/adieuadieu/serverless-chrome/issues/133"参照"))
```
$ mkdir -p bin/
$ curl -SL https://github.com/adieuadieu/serverless-chrome/releases/download/v1.0.0-37/stable-headless-chromium-amazonlinux-2017-03.zip > headless-chromium.zip
$ unzip headless-chromium.zip -d bin/
$ rm headless-chromium.zip
```

## chromedriverのダウンロード
* 上でダウンロードしたheadless-chromiumに対応したchromedriverのバージョン[2.37](https://chromedriver.storage.googleapis.com/index.html?path=2.37/"chromedriver")を選んでダウンロード
```
$ curl -SL https://chromedriver.storage.googleapis.com/2.37/chromedriver_linux64.zip > chromedriver.zip
$ unzip chromedriver.zip -d bin/
$ rm chromedriver.zip
```

## Dockerイメージのビルド
```
$ docker build -t npb-crawler-lambda .
```

## Dockerイメージをコンテナとして実行
```
$ docker run -v "${PWD}":/var/task npb-crawler-lambda
```
