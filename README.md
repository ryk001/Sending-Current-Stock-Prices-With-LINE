# 透過 Python + GitHub 定時自動傳送即時股價 Line 通知
<span style="color:red;">**重點提示：本程式僅限玉山證券富果帳戶**</span>

(非業配，但好像除了永豐/ 富果沒有其他券商提供即時股價 Python API 了?)

## 前情提要
通過這篇教學，你將可以學到
- 如何透過富果 API 爬取即時股價
- 如何透過 Python 傳送 Line 訊息通知
- 如何透過 GitHub 的 Actions 功能實現自動化、定時執行
- 整合以上三者，將得到一個 **定時自動傳送即時股價 Line 通知機器人!!!**

廢話不多說，我們馬上開始吧!

## 0. 基本設置
- 匯入套件
- 填寫要關注的股票代號
  - 前往編輯 `portfolio_watchlist.txt` 文件
  - 按照文件內相同格式輸入要接收通知的股票代號
- 設定各種金鑰
  - Fugle API 的金鑰，申請方式請參考: https://developer.fugle.tw
  - LINE Notify API 的金鑰，申請方式請參考: https://notify-bot.line.me/zh_TW
  - 這個 `os.environ[' ']` 是啥?! 放心，到了 "5. 實現定時自動通知" 會講解

```python
import requests
from fugle_realtime import HttpClient
import pandas as pd
import numpy as np

# 超級韭菜投資組合
portfolio_list = ['2330','2317','2609','3037','3034']

# TOKEN
FUGLE_API_TOKEN = os.environ['FUGLE_API_TOKEN']
LINE_NOTIFY_TOKEN = os.environ['LINE_NOTIFY_TOKEN']
```

## 1. 爬取即時股價
- 建立一個函數，並且變數是前面的股票代號 list

```python
def fugle_get_stock_price(portfolio):
```

### 1-1. 建立一個空的 DafaFrame
- 用來寫入從 API 獲取的資料
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
- 用 for loop 依序 run 過股票代號 list
- 依序取得 股票名稱、昨日股價、即時股價、日期、即時股價更新時間
- 填入 DafaFrame 相對應的欄位
- 利用昨日股價、即時股價計算報酬率
- 最後吐出填好的 DafaFrame

```python
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
```

## 2. 將數據整理成 Line 訊息
這部分就...自由發揮啦~

Line 訊息粗體字、斜體字、紅字等等輸入方法參考: https://finance.ettoday.net/news/1911692

```python
def generate_message(stock_price_dataframe):
  # 標題: 價格播報/ 日期/ 時間
  message = '*價格播報*'+'\n'+'```'+stock_price_dataframe.date[0]+' '+stock_price_dataframe.update_time[0]+'```\n'
  
  # 細項: 股票名稱/ 即時股價/ 漲跌%
  for i in range(len(stock_price_dataframe)):
    message += stock_price_dataframe.stock_name[i] + (6 - len(stock_price_dataframe.stock_name[i]))*'  ' + str(stock_price_dataframe.price[i]) + (6 - len(str(stock_price_dataframe.price[i])))*'  ' +'( _' + str(stock_price_dataframe.price_change[i]) + '%_ )' + '\n'
  
  return message
```

## 3. 利用 LINE Notify 傳送通知

```python
def lineNotifyMessage(token, msg):
    headers = {
        "Authorization": "Bearer " + token, 
        "Content-Type" : "application/x-www-form-urlencoded"
    }

    payload = {'message': msg }
    r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
    return r.status_code
```

## 4. 成果展示

```python
stock_price_dataframe = fugle_get_stock_price(portfolio_list)
message = generate_message(stock_price_dataframe)
lineNotifyMessage(LINE_NOTIFY_TOKEN, message)
```
![run](https://s2.loli.net/2022/12/06/QgBqkdvthirKUD7.png)

(由於在非開盤時間傳送通知，所以會得到最後收盤價)

## 5. 實現定時自動通知

這部分的透過 GitHub 的 Actions 功能實現，

詳細來說是我們是用一個 yml 檔案 來和 Actions 功能互動，

然後這個 yml 檔案再來驅動我們的 .py 檔。

### 5.1 複製這個專案到自己的帳號
- 项目地址：[github/Sending-Current-Stock-Prices-With-Line](https://github.com/ryk001/Sending-Current-Stock-Prices-With-Line.git)
- 點擊右上角 Fork 專案至自己的帳號底下

![run](https://s2.loli.net/2022/12/06/1ta8qHFNBWjQuUb.png)

### 5.2 添加 Fugle, LINE 金鑰到 Secrets
(如果不設置 Secrets 的話所有人都可以傳 Line 給你，也可以用你的富果金鑰來爬蟲😂)
- 回到專案頁面，依次點擊`Settings`-->`Secrets`-->`New secret`

![run](https://s2.loli.net/2022/12/07/7lvh9u3ayXZkIAm.png)

- 建立一個名為`FUGLE_API_TOKEN`的 secret，裡面填上玉山富果 API 的金鑰
- 再建立一個名為`LINE_NOTIFY_TOKEN`的 secret，裡面填上 LINE Notify 的金鑰
- **secret 必須按照以上格式填寫!!!**


### 5.3 設定yml文件
- 主要是設定 Cron 的部分，這裡預設了每個週間的開盤時間 9:00~13:30 內，整點、30 分傳送股價通知一次
- 詳細的 Cron 設定方式和語法，可以參考: https://crontab.guru/#

```yml
on:
  schedule:
  # scheduled at every 30min during trading hours, (UTC+8), weekdays
    - cron: "0,30 1,2,3,4,5 * * 1,2,3,4,5"
  workflow_dispatch:
```

此外可以看到，在這邊我們提到了剛剛建立的 Secrets，

相當於把 Secrets 內的字串導入了我們的 yml 檔，

呼應了最一開頭 .py 檔裡面的設定金鑰的部分，

`os.environ[' ']` 就是為了引用 Secrets 的變數。

(可以回頭看看 Step 0.)

```yml
env:
  ACTIONS_ALLOW_UNSECURE_COMMANDS: true
  FUGLE_API_TOKEN: ${{ secrets.FUGLE_API_TOKEN }}
  LINE_NOTIFY_TOKEN: ${{ secrets.LINE_NOTIFY_TOKEN }}
```

### 5.4 啟用 Actions

Actions 默認是關閉狀態，在 Fork 之後需要先手動執行一次，成功運行才會被激活。

返回項目主頁面，點擊上方的`Actions`，再點擊右側的`Sending-Current-Stock-Prices-With-Line`，再點擊`Run workflow`

![run](https://s2.loli.net/2022/12/07/jQufzoTSVdcbsn2.png)

運行成功後，就大功告成啦! 可以回家睏霸數錢了(並沒有)

## 結語/ 注意事項

感謝你看完這麼詳細(冗長)的文章，希望有幫助到你提升投資績效，有任何疑問與建議歡迎交流，我們下次見!!!

注意事項
- 約每 60 天 Actions 會重設一次，要記得上 GitHub 重新手動 Run
- GitHub 的 Actions 功能會延遲 5~30 分鐘，若有更可靠的自動化方法歡迎交流😍
- 小弟不才，第一次寫 GitHub，若有什麼指教請大力一點
