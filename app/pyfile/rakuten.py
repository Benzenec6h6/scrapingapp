from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import sys
from time import sleep
from mysql import mysql_info
from account import account_info
from scraping import scrape_data

url = "https://member.rakuten-sec.co.jp"

class rakuten(scrape_data):
  def __init__(self, url):
    super().__init__(url)
    self.links=[]
    self.price=[]

  def add_link(self, link):
    self.links.extend(link)

  def add_price(self, price):
    if type(price) is list:
      self.price.extend(price)
    else:
      self.price.append(price)

  def access(self, id, passwd):
    #ログイン
    driver.get(self.url)
    sleep(2)
    username = driver.find_element(By.NAME, "loginid")
    username = username.send_keys(id)
    sleep(2)
    password = driver.find_element(By.NAME, "passwd")
    password = password.send_keys(passwd)
    sleep(1)
    login_btn = driver.find_element(By.ID, "login-btn")
    login_btn.click()
    #メニュー
    menu = driver.find_element(By.CSS_SELECTOR, "li.pcm-gl-g-header-nav__item.pcm-gl-g-header-nav__item--menu>button")
    menu.click()

    hoyu = driver.find_element(By.XPATH, "//*[@id='megaMenu']/div/div[1]/div[2]/div/div/div[1]/ul/li[1]/ul/li[1]/a")
    hoyu.click()
    
  def get_info(self):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    num = soup.select('td.align-C.R0')
    super().add_brand([i.getText().replace("\n", "").replace("\t", "") for i in num])
    link = soup.select('td.align-L.valign-M>a')
    super().add_company([i.getText().replace("\n", "").replace("\t", "") for i in link])
    self.add_link([self.url+i.get('href') for i in link])
    hoyu = soup.select('a.tooltip')
    super().add_stock([i.getText().replace("\n", "").replace("\t", "") for i in hoyu])

    for i in self.links:
        driver.get(i)
        dividend=driver.find_element(By.XPATH, "//*[@id='auto_update_field_info_jp_stock_price']/tbody/tr/td[1]/form[2]/div[2]/div[2]/table[2]/tbody/tr[1]/td[2]").text
        super().add_dividend(float(dividend.replace(",","")))
        p = driver.find_element(By.CLASS_NAME, "price-01").text
        self.add_price(float(p.replace(",", "")))

        link = driver.find_element(By.CLASS_NAME, "last-child")
        l = link.find_element(By.TAG_NAME, "a").get_attribute('href')
        driver.get(l)

        driver.switch_to.frame('J010101-011-1')
        if len(driver.find_elements(By.CLASS_NAME, "tbl-data-02")) > 0:
          yu = driver.find_elements(By.CLASS_NAME, "tbl-data-02")[1]
          super().add_yutai(yu.find_element(By.TAG_NAME, "tbody").text)
        else:
          super().add_yutai("情報なし")

    stock=super().get_stock()
    dividend=super().get_dividend()
    for i in range(len(self.price)):
      st = float(stock[i].replace(",", "").replace("株", ""))
      a = round((dividend[i] / self.price[i])*100, 2)
      super().add_profit(str(a)+"%")
      super().add_total(dividend[i]*st)

    driver.quit()

browser=sys.argv
id_pas=[]
r=mysql_info('rakuten')
for user in r.getID_passwd():
  id_pas.append(account_info(user[0],user[1],user[2],user[3]))

for user in id_pas:
  d=rakuten(url)
  driver=d.selenium_access(browser)
  d.access(user.id, user.passwd)
  driver.implicitly_wait(5)
  d.get_info()
  d.save_info(user.savename)