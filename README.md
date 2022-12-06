# 教你如何透過Line 定時自動傳送即時股價的通知
<span style="color:red;">**重點提示：本程式僅限玉山證券富果帳戶**</span>

(非業配，但好像除了永豐/ 富果沒有其他券商提供即時股價Python API了?)

### 1. 爬取即時股價
這部分透過 fugle api 來實現，首先要取得金鑰，取得方式詳見這裡: https://developer.fugle.tw

```python
# 先匯入套件，必須的必
import requests
from fugle_realtime import HttpClient
import pandas as pd
import numpy as np

# 這些是我們要取得即時報價的股票
portfolio_list = ['1336','4977','4551','2408','3653','3289','3443','6533']

# generate message
def price_info_string(portfolio):
  ```
1-2. 首先建立一個空的DafaFrame，裡頭的欄位包含...

股票代號、股票名稱、日期、即時股價更新時間、即時股價、昨日股價、股價變動%數

```python
  # raw dataframe
  stock_price_dataframe = pd.DataFrame(columns=['ticker', 
                                                'stock_name',
                                                'date',
                                                'update_time', 
                                                'price', 
                                                'yesterday_price', 
                                                'price_change'])
  stock_price_dataframe['ticker'] = portfolio
  
  # fetch data from fugle
  api_client = HttpClient(api_token='f1a2c13bfff979a50e60b9692e8a6a7e')
  for i in range(len(portfolio)):
    
    # stock name & yesterday price
    meta_data = api_client.intraday.meta(symbolId=portfolio[i])
    stock_name = str(meta_data['data']['meta']['nameZhTw'])
    yesterday_price = float(meta_data['data']['meta']['previousClose'])
    
    # get price at the moment & date & time
    price_data = api_client.intraday.chart(symbolId=portfolio[i])
    price = float(price_data['data']['chart']['c'][-1])
    date = price_data['data']['info']['lastUpdatedAt'][5:7]+'/'+price_data['data']['info']['lastUpdatedAt'][8:10]
    update_time = price_data['data']['info']['lastUpdatedAt'][11:19]

    # put data in dataframe
    stock_price_dataframe['stock_name'][i] = stock_name
    stock_price_dataframe['date'][i] = date
    stock_price_dataframe['update_time'][i] = update_time
    stock_price_dataframe['yesterday_price'][i] = yesterday_price
    stock_price_dataframe['price'][i] = price

  # calculate price change
  stock_price_dataframe['price_change'] = ((stock_price_dataframe['price']/stock_price_dataframe['yesterday_price']-1)*100).astype('float').round(decimals = 2)

  # price info string
  msg = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  for i in range(len(stock_price_dataframe)):
    msg += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  msg += '\n'+'[Beta Version 1]'
  
  return msg
```

> import pandas
> for i in range

### 2. 利用 Line_notify 傳送通知


### 3. 實現定時自動通知
