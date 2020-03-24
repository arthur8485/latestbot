from emoji import emojize
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from time import sleep
import os
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError
import json


def requests_get(*args1, **args2):
    i = 3
    while i >= 0:
        try:
            return requests.get(*args1, **args2)
        except (ConnectionError, ReadTimeout) as error:
            print(error)
            print('retry one more time after 60s', i, 'times left')
            sleep(60)
        i -= 1
    return pd.DataFrame()


def requests_post(*args1, **args2):
    i = 3
    while i >= 0:
        try:
            return requests.post(*args1, **args2)
        except (ConnectionError, ReadTimeout) as error:
            print(error)
            print('retry one more time after 60s', i, 'times left')
            sleep(60)
        i -= 1
    return pd.DataFrame()


def latest_number(*argu1, **argu2):
    url = "https://www.taiwanlottery.com.tw/lotto/BINGOBINGO/drawing.aspx"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    try:
        res = requests_get(url, headers=headers)
        soup = BeautifulSoup(res.text, 'html.parser')
    except:
        print('**WARRN: requests cannot get html')
    ID = soup.find('span', attrs={'id': 'lblBBDrawTerm'})
    table_rows = soup.select('td', attrs={'class': 'tdA_3'})
    ID = int(ID.text)

    result = []
    i = 0
    for div in table_rows:
        td = div.find_all('div')
        row = [div.text.strip() for div in td if div.text.strip()]
        if row and i >= 1:
            result.append(row)
        i += 1
    df = pd.DataFrame(result, index=None)
   # df = df.drop(df.columns[0], axis=1)
    df = df.drop([1, 2, 3])
    df = df.drop([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,
                  13, 14, 15, 16, 17, 18, 19, 20], axis=1)

    df.insert(0, '期別', value=ID)
    df1 = df['期別']
    df1 = df1.to_json(orient='values').strip('[]')
    df = df.drop(columns=['期別'])

    df = df.to_json(orient='values').strip('[]').strip(',"')
    point_right = emojize(":point_right:", use_aliases=True)     
    content1 = point_right+" 期別:   " + df1
    content2 = point_right+" 開獎號碼: "+df
    content3 = ""
    content3 += '{}\n\n{}'.format(content1, content2)
    return content3


