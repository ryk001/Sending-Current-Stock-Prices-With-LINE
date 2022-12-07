import requests
from fugle_realtime import HttpClient
import pandas as pd
import numpy as np
import os

# 匯入關注清單
portfolio_watchlist = open('portfolio_watchlist.txt', 'r').read().strip().split(',')
lis
print(portfolio_watchlist)

# secret token
FUGLE_API_TOKEN = os.environ['FUGLE_API_TOKEN']
LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']

def fugle_get_stock_price(portfolio):
  stock_price_dataframe = pd.DataFrame(columns=['ticker', 
                                                'stock_name',
                                                'date',
                                                'update_time', 
                                                'price', 
                                                'yesterday_price', 
                                                'price_change'])
  stock_price_dataframe['ticker'] = portfolio

  # Fugle API 金鑰
  api_client = HttpClient(api_token = FUGLE_API_TOKEN)
  
  for i in range(len(portfolio)):
    
    # 富果 API 讚! (再次強調非業配)
    meta_data = api_client.intraday.meta(symbolId=portfolio[i])
    price_data = api_client.intraday.chart(symbolId=portfolio[i])
    
    # 股票名稱 & 昨日股價
    stock_name = str(meta_data['data']['meta']['nameZhTw'])
    yesterday_price = float(meta_data['data']['meta']['previousClose'])
    
    # 即時股價 & 日期 & 即時股價更新時間
    price = float(price_data['data']['chart']['c'][-1])
    date = price_data['data']['info']['lastUpdatedAt'][5:7]+'/'+price_data['data']['info']['lastUpdatedAt'][8:10]
    update_time = price_data['data']['info']['lastUpdatedAt'][11:19]

    # 把數據塞進 DafaFrame 欄位
    stock_price_dataframe['stock_name'][i] = stock_name
    stock_price_dataframe['date'][i] = date
    stock_price_dataframe['update_time'][i] = update_time
    stock_price_dataframe['yesterday_price'][i] = yesterday_price
    stock_price_dataframe['price'][i] = price

  # 計算報酬率
  stock_price_dataframe['price_change'] = ((stock_price_dataframe['price']/stock_price_dataframe['yesterday_price']-1)*100).astype('float').round(decimals = 2)
  
  return stock_price_dataframe

def generate_message(stock_price_dataframe):
  # 標題: 價格播報/ 日期/ 時間
  message = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  
  # 細項: 股票名稱/ 即時股價/ 漲跌%
  for i in range(len(stock_price_dataframe)):
    message += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  
  return message


def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code

stock_price_dataframe = fugle_get_stock_price(portfolio_watchlist)
message = generate_message(stock_price_dataframe)
lineNotifyMessage(LINE_NOTIFY_TOKEN, message)

