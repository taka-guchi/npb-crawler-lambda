import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import datetime
import csv
import boto3

def lambda_handler(event,context):
    s3 = boto3.resource('s3')

    # healessで動かすために必要なオプション
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')

    # ダウンロードするバイナリを指定
    options.binary_location = './bin/headless-chromium'

    driver = webdriver.Chrome(
        './bin/chromedriver',chrome_options=options)

    # サイト内のチームindexと対応するチーム名（頭文字）の辞書を作成
    dict_teams = {1:'G',2:'S',3:'DB',4:'D',5:'T',6:'C',
                  7:'L',8:'F',9:'M',11:'Bs',12:'H',376:'E'}

    for key, value in dict_teams.items():
        # チームごとにurlを作成
        url = ('http://baseballdata.jp/{index}/GResult.html'.format(index=key))

        # ブラウザでアクセス
        driver.get(url)
        # 「全て見る」リンクを押下して全データを表示
        driver.find_element_by_class_name('allshow').click()
        sleep(1)

        # HTMLの文字コードをUTF-8に変換して取得
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html,'html.parser')
        rows = soup.findAll('tr')

        # 現在年を取得
        this_year = datetime.date.today().year

        # CSVファイルの設定
        file_name = '/tmp/{year}_{team_capital}_match_results.csv'
        csv_file = open(file_name.format(year=this_year,team_capital=value),
                       'wt',newline='',encoding='utf-8')
        writer = csv.writer(csv_file)

        try:
            for row in rows:
                csv_row = []
                for cell in row.findAll("td"):
                    csv_row.append(cell.get_text().strip())
                writer.writerow(csv_row)
        finally:
            csv_file.close()

        sleep(1)

        # S3にアップロード
        bucket = s3.Bucket('npb-match-results')
        bucket.upload_file(file_name.format(year=this_year,team_capital=value),
                           '{year}/{year}_{team_capital}_match_results.csv'.format(year=this_year,team_capital=value))

        # ログ出力
        print('finish upload team={team_capital}'.format(team_capital=value))

    driver.close()
