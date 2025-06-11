from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
import re
import sys
from mysql import mysql_info
from account import account_info
from scraping import scrape_data

url = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETlgR001Control&_PageID=WPLETlgR001Rlgn50&_DataStoreID=DSWPLETlgR001Control&_ActionID=login&getFlg=on"

class SBI(scrape_data):
  def __init__(self, url):
    super().__init__(url)

  def access(self, id, passwd):
    driver.get(self.url)
    #driver.implicitly_wait(10)

    username = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "user_id"))
    username.send_keys(id)

    password = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "user_password"))
    password.send_keys(passwd)

    login_btn = WebDriverWait(driver, 30).until(lambda y: y.find_element(By.NAME, "ACT_loginHome"))
    login_btn.click()

    WebDriverWait(driver, 30).until(lambda y: y.find_element(By.XPATH, "//*[@id='link02M']/ul/li[3]/a")).click()

  def get_info(self):  
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    super().add_company([name.getText() for name in soup.select('td.mtext>a')[2::2]])
    num=[]
    num = [i.parent.text for i in soup.select('td.mtext>a')[2::2]]
    for i in num:
        super().add_brand(re.findall(r"^\d{4}", i))
    hold = soup.find_all('tr', attrs={'bgcolor': '#eaf4e8'})

    for h in hold:
        super().add_stock(h.find('td').text)

    for j in super().get_brand():
        name=WebDriverWait(driver, 30).until(lambda y: y.find_element(By.ID, "top_stock_sec"))
        name.send_keys(j)
        WebDriverWait(driver, 30).until(lambda y: y.find_element(By.CSS_SELECTOR, "#srchK > a")).click()
        sleep(3)
        if len(driver.find_elements(By.ID, "posElem_190"))>0:
          WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")))
          html = driver.page_source
          soup = BeautifulSoup(html, 'html.parser')
          super().add_profit(soup.select_one('#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(2)>p').text)
          super().add_dividend(soup.select_one('#posElem_190>table>tbody>tr:nth-child(3)>td:nth-child(4)>p').text)
        else:
          WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(2)>p")))
          html = driver.page_source
          soup = BeautifulSoup(html, 'html.parser')
          super().add_profit(soup.select_one('#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(2)>p').text)
          super().add_dividend(soup.select_one('#posElem_19-1>table>tbody>tr:nth-child(3)>td:nth-child(4)>p').text)
        
        try:
            WebDriverWait(driver, 30).until(lambda y: y.find_element(By.CSS_SELECTOR, "td:nth-child(8)>span>a")).click()
            driver.implicitly_wait(60)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            yu=""
            y = soup.find('table', attrs={'summary': '優待内容'}).find('tbody').select("p.fm01")
            for j in y:
                yu+=j.text+'\n'
            super().add_yutai(yu.strip())
        except:
            super().add_yutai("情報無し")

    driver.quit()

  def calc(self):
    div = []
    d=[]
    s = [float(h.replace(',', '')) for h in super().get_stock()]

    for i in super().get_dividend():
        st0 = [float(d) for d in re.findall(r"(\d+(?:\.\d+)?)", i)]
        try:
            div.append([st0[0], st0[1]])
        except:
            div.append(st0[0])
    
    for i in range(len(div)):
        try:
            super().add_total(str(div[i][0] * s[i])+"~"+str(div[i][1] * s[i]))
        except:
            super().add_total(str(div[i] * s[i]))

browser=sys.argv            
id_pas=[]
r=mysql_info('SBI')
for user in r.getID_passwd():
  id_pas.append(account_info(user[0],user[1],user[2],user[3]))
  
"""
for user in id_pas:
  d=SBI(url)
  driver=d.selenium_access(browser)
  d.access(user.id, user.passwd)
  d.get_info()
  d.calc()
  d.save_info(user.savename)
"""

u=int(browser[2])
d=SBI(url)
driver=d.selenium_access(browser)
d.access(id_pas[u].id, id_pas[u].passwd)
d.get_info()
d.calc()
d.save_info(id_pas[u].savename)
