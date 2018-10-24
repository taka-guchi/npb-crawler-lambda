import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import datetime
import csv
import boto3

def lambda_handler(event,context):
    s3 = boto3.resource('s3')
    BUCKET_NAME = 'npb-match-results'
    URL_TEMPLATE = 'http://baseballdata.jp/{index}/GResult.html'
    FILENAME_TEMPLATE = '/{directory}/{year}_{team_capital}_match_results.csv'

    # 現在年を取得
    this_year = datetime.date.today().year

    # headlessで動かすために必要なオプション
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    # バイナリを指定
    options.binary_location = './bin/headless-chromium'

    # ブラウザの起動
    driver = webdriver.Chrome('./bin/chromedriver',chrome_options=options)

    # サイト内のチームindexと対応するチーム名（頭文字）の辞書を作成
    dict_teams = {1:'G',2:'S',3:'DB',4:'D',5:'T',6:'C',
                  7:'L',8:'F',9:'M',11:'Bs',12:'H',376:'E'}

    for key, value in dict_teams.items():
        # チームごとにurlを作成してスクレイプ
        url = (URL_TEMPLATE.format(index=key))
        screpe(url)

    driver.close()

 def scrape(rul):
     # CSVファイルの設定
    csv_file = open(FILENAME_TEMPLATE.format(year=this_year,team_capital=value),
                   'wt',newline='',encoding='utf-8')
    writer = csv.writer(csv_file)

    try:
        # ブラウザでアクセス
        driver.get(url)
        # 「全て見る」リンクを押下して全データを表示
        driver.find_element_by_class_name('allshow').click()
        sleep(1)

        # HTMLの文字コードをUTF-8に変換して取得
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html,'html.parser')

        # csvファイルへの書き出し
        for row in soup.findAll('tr'):
            csv_row = []
            for cell in row.findAll("td"):
                csv_row.append(cell.get_text().strip())
            writer.writerow(csv_row)

        # S3へアップロード
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.upload_file(FILENAME_TEMPLATE.format(directory='tmp',year=this_year,team_capital=value),
                           FILENAME_TEMPLATE.format(directory=this_year,year=this_year,team_capital=value))

        print('finish upload team={team_capital}'.format(team_capital=value))

    except Exception as e:
       print('error_message:{message}'.format(message=e))

    finally:
       csv_file.close()

    sleep(1)
