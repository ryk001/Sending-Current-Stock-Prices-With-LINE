# 教你如何透過 LINE Notify 定時自動傳送即時股價通知
<span style="color:red;">**重點提示：本程式僅限玉山證券富果帳戶**</span>

(非業配，但好像除了永豐/ 富果沒有其他券商提供即時股價Python API了?)

### 0. 匯入套件、決定要爬哪些股票 (超級韭菜投資組合)

```python
import requests
from fugle_realtime import HttpClient
import pandas as pd
import numpy as np

portfolio_list = ['2330','2317','2609','3037','3034']
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
  api_client = HttpClient(api_token = '填入你申請的富果金鑰')
```

### 1-3. 開爬！
- 用for loop 依序 run 過股票代號 list
- 依序取得...股票名稱、昨日股價、即時股價、日期、即時股價更新時間
- 然後填入 DafaFrame 相對應的欄位
- 利用昨日股價、即時股價計算報酬率
- 最後吐出填好的 DafaFrame

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
  
  return stock_price_dataframe
```

### 2. 將數據整理成 Line 訊息
這部分就...自由發揮啦~

```python
def generate_message(stock_price_dataframe):
  # price info string
  msg = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  for i in range(len(stock_price_dataframe)):
    msg += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  
  return msg
```

### 3. 利用 LINE Notify 傳送通知
這部分要先申請到 LINE Notify 金鑰，申請方式請參閱: https://notify-bot.line.me/zh_TW

```python
def generate_message(stock_price_dataframe):
  # price info string
  msg = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  for i in range(len(stock_price_dataframe)):
    msg += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  
  return msg
```

### 4. 上述所有步驟一氣呵成!

```python
def generate_message(stock_price_dataframe):
  # price info string
  msg = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  for i in range(len(stock_price_dataframe)):
    msg += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  
  return msg
```

### 5. 實現定時自動通知
