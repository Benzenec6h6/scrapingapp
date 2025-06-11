from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import re
import sys
from time import sleep
from mysql import mysql_info
from account import account_info
from scraping import scrape_data

url = "https://sec-sso.click-sec.com/loginweb/sso-redirect?s=01p=08"

class gmoclick(scrape_data):
    def __init__(self, url):
        super().__init__(url)
        self.links=[]

    def add_link(self, link):
        if type(link) is list:
            self.links.extend(link)
        else:
            self.links.append(link)

    def access(self, id, passwd):
        driver.get(self.url)
        driver.implicitly_wait(10)
        username = driver.find_element(By.NAME, "j_username")
        username = username.send_keys(id)

        password = driver.find_element(By.NAME, "j_password")
        password = password.send_keys(passwd)

        login_btn = driver.find_element(By.NAME, "LoginForm")
        login_btn.click()
        #メニュー
        kabusiki = driver.find_element(By.CLASS_NAME, "js-kabu")
        driver.get(kabusiki.get_attribute("href"))
        hoyu = driver.find_element(By.ID, "kabuSubMenuGenPosition")
        driver.get(hoyu.get_attribute("href"))

    def get_info(self):
        company=[]
        l=[]

        ul=driver.find_element(By.CLASS_NAME, "m-pagination-01")
        li=ul.find_elements(By.TAG_NAME, "li")

        for i in range(len(li)-2):
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            link = soup.select('tbody.is-alternate>tr.is-selectable>td.col-02>a')
            self.add_link([i.get('href') for i in link])
            for j in link:
                l=j.select('span')
                company.extend([i.getText() for i in l])
            stock = soup.select('tbody.is-alternate>tr.is-selectable>td.col-03>div:nth-child(1)')
            super().add_stock([i.getText().replace("\n", "") for i in stock])
            if i < len(li)-3:
                driver.find_element(By.ID, "nextJumpPage").click()
                sleep(1)
            else:
                break
        
        for i in range(0,len(company),2):
            super().add_company(company[i])
            super().add_brand(company[i+1])
        
        dividend=[]
        for i in self.links:
            driver.get(i)
            driver.set_page_load_timeout(5)
            sleep(1)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            profit = soup.select_one('td#probableDividendYield').getText().replace("\n", "")
            super().add_profit(profit)
            dividend = soup.select_one('td#dpsYear').getText().replace("\n", "").strip()
            super().add_dividend(dividend)

            yutaiLink=soup.select_one("a#yutaiLink.btn.is-disabled")
            if yutaiLink:
                super().add_yutai("情報なし")
            else:
                yutaiLink=driver.find_element(By.ID, "yutaiLink")
                yutaiLink.click()
                sleep(0.5)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                tbody=soup.select_one('table.m-table-03>tbody').get_text()
                super().add_yutai(tbody)

        dividend = super().get_dividend()
        stock = [float(i.replace('株', '').replace(',', '')) for i in super().get_stock()]
        for i, j in zip(dividend, stock):
          i=re.search(r'\d+',i)
          if i!=None:
            i=i.group()
            d=float(i)
            super().add_total(d*j)
          else:
            super().add_total(0)
        
        driver.quit()

browser = sys.argv
id_pas=[]
r=mysql_info('gmoclick')
for user in r.getID_passwd():
  id_pas.append(account_info(user[0],user[1],user[2],user[3]))

for user in id_pas:
  d=gmoclick(url)
  driver=d.selenium_access(browser)
  d.access(user.id, user.passwd)
  driver.implicitly_wait(5)
  d.get_info()
  d.save_info(user.savename)