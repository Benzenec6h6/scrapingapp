from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import os
import sys
import glob
import pandas as pd
import datetime

class scrape_data:
  def __init__(self, url):
    self.url=url
    self.brand = []
    self.company = []
    self.profit = []
    self.stock = []
    self.dividend = []
    self.total = []
    self.yutai = []
    self.df=pd.DataFrame()

  def add_brand(self, brand):
    if type(brand) is list:
      self.brand.extend(brand)
    else:
      self.brand.append(brand)  

  def get_brand(self):
    return self.brand

  def add_company(self, company):
    if type(company) is list:
      self.company.extend(company)
    else:
      self.company.append(company)

  def add_profit(self, profit):
    if type(profit) is list:
      self.profit.extend(profit)
    else:
      self.profit.append(profit)

  def get_profit(self):
    return self.profit

  def add_stock(self, stock):
    if type(stock) is list:
      self.stock.extend(stock)
    else:
      self.stock.append(stock)

  def get_stock(self):
    return self.stock

  def add_dividend(self, dividend):
    if type(dividend) is list:
      self.dividend.extend(dividend)
    else:
      self.dividend.append(dividend)

  def get_dividend(self):
    return self.dividend

  def add_total(self, total):
    if type(total) is list:
      self.total.extend(total)
    else:
      self.total.append(total)

  def add_yutai(self, yutai):
    if type(yutai) is list:
      self.yutai.extend(yutai)
    else:
      self.yutai.append(yutai)

  def selenium_access(self, browser):
    if browser[1] == "1":
      options = webdriver.ChromeOptions()
    elif browser[1]=="2":
      options = webdriver.FirefoxOptions()
    else:
      print("error")
      
    HOST_NAME = os.environ['HUB_HOST']
    return webdriver.Remote(
      #command_executor = os.environ["SELENIUM_URL"],
      command_executor=f'http://{HOST_NAME}:4444/wd/hub',
      options = options
    )

  def save_info(self, savename):
    dt=datetime.datetime.today()
    today=dt.strftime('%Y/%m/%d')
    self.df['銘柄コード']=self.brand
    self.df['社名']=self.company
    self.df['配当利回り']=self.profit
    self.df['保有数']=self.stock
    self.df['配当']=self.dividend
    self.df['合計']=self.total   
    self.df['優待']=self.yutai
    self.df.set_index('銘柄コード',inplace=True)
    self.df.to_csv('csv/'+savename+today.replace("/","-")+'.csv')
  
  def insert(self, item, savename):
    dt=datetime.datetime.today()
    today=dt.strftime('%Y/%m/%d')
    self.df.insert(2, '優待利回り', item)
    self.df.to_csv('csv/'+savename+today.replace("/","-")+'.csv')
