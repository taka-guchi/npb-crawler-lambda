import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import datetime
import csv
import boto3

BUCKET_NAME = 'npb-match-result'
URL_TEMPLATE = 'http://baseballdata.jp/{index}/GResult.html'
FILENAME_TEMPLATE = '{directory}/{year}_{team_capital}_match_results.csv'
THIS_YEAR = datetime.date.today().year

def lambda_handler(event,context):
    s3 = boto3.resource('s3')

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
        scrape(driver,url,value,s3)
        sleep(1)

    driver.close()

def scrape(driver,url,value,s3):
    # CSVファイルの準備
    csv_file = open(FILENAME_TEMPLATE.format(directory='/tmp',year=THIS_YEAR,team_capital=value),
                    'wt',newline='',encoding='utf-8')
    writer = csv.writer(csv_file)

    try:
        # ブラウザでアクセス
        driver.get(url)
        # スクレイピング対象trのクラス名
        # => 「全て見る」リンク押下後はクラス名が空になるため変数で保持して可変にする
        tr_class = 'deftr'
        # 「全て見る」リンクが画面に存在すれば押下して全データを表示する
        link_all_show = driver.find_elements(By.XPATH, "//div[@class='allshow']")
        if len(link_all_show) > 0:
            driver.find_element_by_class_name('allshow').click()
            tr_class = ''
            sleep(1)

        # HTMLの文字コードをUTF-8に変換して取得
        html = driver.page_source.encode('utf-8')
        soup = BeautifulSoup(html,'html.parser')

        # csvファイルへの書き出し
        for row in soup.findAll('tr', class_=tr_class):
            csv_row = []
            for cell in row.findAll('th', class_='pnm'):
                csv_row.append(cell.get_text().strip())
            for cell in row.findAll('td', bgcolor=''):
                csv_row.append(cell.get_text().strip())
            # 空行は無視する
            if csv_row:
                writer.writerow(csv_row)
        # 明示的にcsvファイルを閉じなければ、書き込み後のファイルがアップロードできない
        csv_file.close()

        # S3へアップロード
        bucket = s3.Bucket(BUCKET_NAME)
        bucket.upload_file(FILENAME_TEMPLATE.format(directory='/tmp',year=THIS_YEAR,team_capital=value),
                           FILENAME_TEMPLATE.format(directory=THIS_YEAR,year=THIS_YEAR,team_capital=value))

        print('finish upload team={team_capital}'.format(team_capital=value))

    except Exception as e:
       print('error_message:{message}'.format(message=e))

    finally:
       csv_file.close()
