# 教你如何透過Line 定時自動傳送即時股價的通知
<span style="color:red;">**重點提示：本程式僅限玉山證券富果帳戶**</span>

(非業配，但好像除了永豐/ 富果沒有其他券商提供即時股價Python API了?)

### 0. 匯入套件、決定要爬哪些股票

```python
import requests
from fugle_realtime import HttpClient
import pandas as pd
import numpy as np

portfolio_list = ['1336','4977','4551','2408','3653','3289','3443','6533']
```

### 1. 爬取即時股價
- 透過 Fugle Api 來實現，首先要取得金鑰，取得方式詳見這裡: https://developer.fugle.tw
- 建立一個函數，並且變數是前面的股票代號 list

```python
def fugle_get_stock_price(portfolio):
```

### 1-1. 首先建立一個空的DafaFrame，接下來填入資料用

- 欄位包含...股票代號、股票名稱、日期、即時股價更新時間、即時股價、昨日股價、股價變動%數
- 指定股票代號欄位為導入的變數 (股票代號 list)

```python
  stock_price_dataframe = pd.DataFrame(columns=['ticker', 
                                                'stock_name',
                                                'date',
                                                'update_time', 
                                                'price', 
                                                'yesterday_price', 
                                                'price_change'])
  stock_price_dataframe['ticker'] = portfolio
```
### 1-2. 開始爬取即時股價資訊
- 先設定你的金鑰

```python
  api_client = HttpClient(api_token = [填入你申請的富果金鑰])
```

開爬！
- 用for loop 依序 run 過股票代號 list
- 依序取得...股票名稱、昨日股價、即時股價、日期、即時股價更新時間
- 然後填入 DafaFrame 相對應的欄位
- 利用昨日股價、即時股價計算報酬率

```python

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
```

### 2. 將數據整理成 Line 訊息

### 3. 利用 Line_notify 傳送通知


### 4. 實現定時自動通知
