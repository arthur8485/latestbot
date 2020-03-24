import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime
from emoji import emojize
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
import requests
from bs4 import BeautifulSoup
from time import sleep
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectionError

# 驗證 api
scope = ["https://spreadsheets.google.com/feeds",
         'https://www.googleapis.com/auth/spreadsheets',
         "https://www.googleapis.com/auth/drive.file",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
client = gspread.authorize(creds)

def nearest_shop(user_latitude, user_longtitude):

    sheet = client.open("telegram")
    worksheet = sheet.get_worksheet(1)
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    coordinate = []
    latitude = user_latitude
    longtitude = user_longtitude

    a = df.iloc[(df['latitude']-latitude).abs().argsort()[:1]]
    a_latitude1 = a.iloc[0][0]
    coordinate.append(a_latitude1)
    
    a_longtitude1 = a.iloc[0][1]
    coordinate.append(a_longtitude1)
    

    # 利用第一個座標找附近的
    b = df.iloc[(df['latitude']-longtitude).abs().argsort()[:1]]
    b_latitude1 = b.iloc[0][0]
    coordinate.append(b_latitude1)
    b_longtitude1 = b.iloc[0][1]
    coordinate.append(b_longtitude1)


    print(coordinate)
    return coordinate

def logs(context):
    # open sheet file
    sheet = client.open("telegram")
    data = sheet.get_worksheet(0)
    # get length of sheet
    len_data = len(data.get_all_records())
    # get current time
    now = datetime.datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")

    # update by len of sheet
    data.update_cell(len_data+2, 1, current_time)
    data.update_cell(len_data+2, 2, context)  # update context

    print('logs updated')

# [121.194136, 25.059711]

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

def predict_ID(*argu1, **argu2):
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


    df.insert(0, '期別', value=ID)
    ID = df.iloc[0,0]
    PreID = ID + 1

    #PreID = PreID.to_json(orient='values').strip('[]')



    content1 = "預測期別:       " + str(PreID)

    return content1

def get_today_month():
    get_today_ID = datetime.date.today().month
    print(get_today_ID)
    return get_today_ID

def Crawler():
    get_today_ID = 10000*datetime.date.today().year+ 100*datetime.date.today().month + datetime.date.today().day - 20192936
    today_month = datetime.date.today().month
    url = "https://www.taiwanlottery.com.tw/lotto/BINGOBINGO/drawing.aspx"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    res = requests_get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    VIWESTATE = soup.select_one('#__VIEWSTATE')['value']
    EVENTVALIDATION = soup.select_one('#__EVENTVALIDATION')['value']
    VIEWSTATEGENERATOR = soup.select_one('#__VIEWSTATEGENERATOR')['value']

    payload = { 
        '__EVENTTARGET': 'Calendar2', 
        '__EVENTARGUMENT': str(get_today_ID),  ## ID
        'DropDownList1': '2020/'+ str(today_month), ## 月份
        'DropDownList2': '0', ## 排序方式
        '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR, 
        '__VIEWSTATE': VIWESTATE, 
        '__EVENTVALIDATION': EVENTVALIDATION
    }
    response = requests_post(url, data=payload)
    soup = BeautifulSoup(response.text, 'lxml')
    table_rows = soup.select('.tableFull')[1].find_all('tr')

    ##爬下來資料合併DATAFRAME

    result = []
    i = 0
    for tr in table_rows:
        td = tr.find_all('td')
        row = [tr.text.strip() for tr in td if tr.text.strip()]
        if row and i >= 3:
            result.append(row)
        i+=1
    df = pd.DataFrame(result,columns={'0': '期別', '1': '獎號','2':'超級獎號','3':'猜大小', '4': '猜單雙'})
    df = df.rename(columns={'0': '期別', '1': '獎號','2':'超級獎號','3':'猜大小', '4': '猜單雙'})
    df1 = df.獎號.str.split(" ",expand=True)
    df1 = df1.drop([10], axis=1)
    df1['超級獎號']=df['超級獎號']
    df1['猜大小']=df['猜大小']
    df1['猜單雙']=df['猜單雙']
    df1['期別']=df['期別']
    cols = df1.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df1 = df1[cols]
    df = df.iloc[0,0]
    df1 = df1.drop(['期別', '超級獎號'], axis=1)
    
    df2 = pd.get_dummies(df1,prefix=['猜單雙'], columns = ['猜單雙'], drop_first=False)
    data = pd.get_dummies(df2,prefix=['猜大小'], columns = ['猜大小'], drop_first=False)
    
    # check  whether columns exist or not
    
    #if not exist insert column and values = 0
    try:
        data.insert(20, column='猜單雙_和',value=0)
        data.insert(21, column='猜單雙_單',value=0)
        data.insert(22, column='猜單雙_小單',value=0)
        data.insert(23, column='猜單雙_小雙',value=0)
        data.insert(24, column='猜單雙_雙',value=0)
        data.insert(25, column='猜大小_大',value=0)
        data.insert(26, column='猜大小_小',value=0)
        data.insert(27, column='猜大小_－',value=0)
        
    except:
        pass
    data = data.iloc[:18,:]
    
    for i in range(18):
        data.iloc[i,:] = pd.to_numeric(data.iloc[i,:])
    
        np1 = np.array(data).astype(int)
    
    return np1


def predict():
# read history winning number
    #data = pd.read_csv("D:\\python\\Chatbot\\GoBot\\number_prediction\\last.csv")

    sheet = client.open("telegram")
    worksheet = sheet.get_worksheet(2)
    df = worksheet.get_all_records()
    data = pd.DataFrame(df)
    scaler = StandardScaler().fit(data.values)

    to_predict = np.array(Crawler())
    scaled_to_predict = scaler.transform(to_predict)

    # read mdoel D:\python\Chatbot\GoBot\SQLite\RNN3.h5
    model_path = "RNN3.h5"
    new_model = tf.keras.models.load_model(model_path)

    scaled_predicted_output_2 = new_model.predict(np.array([scaled_to_predict]))
    b=[]
    a = scaler.inverse_transform(scaled_predicted_output_2).astype(int)[0]
    b.append(a)
    print(b)
    return b

def predict_number(*argu1,**argu2):
    
    b = predict()
    df=pd.DataFrame(b,columns=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20',
                                '猜單雙_和','猜單雙_單','猜單雙_小單','猜單雙_小雙','猜單雙_雙','猜大小_大','猜大小_小','猜大小_－'])

    df1 = df.iloc[:,:19]
    df2 = df.iloc[0,20:]

    print(df2)
    if df2.iloc[0]==1:
        a = "和"
        
    elif df2.iloc[1]==1:
        a="單"
        
    elif df2.iloc[2]==1:
        a="小單"
        
    elif df2.iloc[3]==1:
        a="小雙"
        
    elif df2.iloc[4]==1:
        a="雙"
    
    else:
        a="未開"
        
    if df2.iloc[5]==1:
        b="大"
        
    elif df2.iloc[6]==1:
        b="小"
        
    elif df2.iloc[5]==0 and df2.iloc[6]==0:
        b="－"

        
    point_right = emojize(":point_right:", use_aliases=True)                   
    df1 = df1.to_json(orient='values').strip('[]').strip(',"')
    
    content1 = point_right+" 預測單雙:       "+ str(a)
    content2 = point_right+" 預測大小:       "+ str(b)
    content3 = point_right+" 預測號碼:       "+"\n" + df1
    content4 = point_right+" "+predict_ID()
    content4 += '\n\n{}\n\n{}\n\n{}'.format(content3,content1, content2)
    print(content4)
    return content4

