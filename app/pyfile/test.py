from selenium import webdriver
import os
import json
import time
 
# コンテナに登録した環境変数の設定
#browser=int(input("chrome is 1,firefox is 2 input 1 or 2"))
browser = sys.argv
if browser[1] == "1":
    BROWSER_NAME = "chrome"
elif browser[1]=="2":
    BROWSER_NAME = "firefox"
else:
    print("error")

#BROWSER_NAME = os.environ['BROWSER_NAME']
HOST_NAME = os.environ['HUB_HOST']
 
# テストするブラウザごとにwebdriverのオプションを設定
if BROWSER_NAME == "chrome":
    options = webdriver.ChromeOptions()
else:
    options = webdriver.FirefoxOptions()
print(BROWSER_NAME)
 
# 画面を表示しないのであれば、ヘッドレスオプションを付ける
#options.add_argument('--headless')
#options.add_argument('--window-size=1280,1024')
 
# Selenium hub Serverに接続する
with webdriver.Remote(
    command_executor=f'http://{HOST_NAME}:4444/wd/hub',
    options=options,
) as driver:
    # ブラウザを操作する
    driver.get('https://www.google.com/')
    time.sleep(10)
 