from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from time import sleep
from PIL import Image
import pyocr.builders
import os
import sys
import glob
import shutil
from mysql import mysql_info
from account import account_info
from scraping import scrape_data

url = "https://trade.matsui.co.jp/mgap/login"

class matsui(scrape_data):
    def __init__(self, url):
        super().__init__(url)
        #優待利回り
        self.yu_prof=[]
        #ocr
        self.tools = pyocr.get_available_tools()
        self.tool = self.tools[0]

    def add_yu_prof(self, yu_prof):
        if type(yu_prof) is list:
            self.yu_prof.extend(yu_prof)
        else:
            self.yu_prof.append(yu_prof)

    def add_margin(self, pil_img, top, right, bottom, left, color):
        width, height = pil_img.size
        new_width = width + right + left
        new_height = height + top + bottom
        result = Image.new(pil_img.mode, (new_width, new_height), color)
        result.paste(pil_img, (left, top))
        return result

    def access(self, id, passwd):
        driver.get(self.url)
        username = driver.find_element(By.ID, "login-id")
        username.send_keys(id)

        password = driver.find_element(By.ID, "login-password")
        password.send_keys(passwd)

        login_btn = driver.find_element(By.CLASS_NAME, "local-nav-login__button")
        login_btn.click()

        #広告対策
        try:
            WebDriverWait(driver, 5).until(lambda x: x.find_element(By.CSS_SELECTOR, "div#popup_deal>img")).click()
        except:
            pass
    
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CLASS_NAME, "btn-menu-spot-sell")).click()

    def get_info(self, user):
        number=0
        page=WebDriverWait(driver, 30).until(lambda x: x.find_elements(By.CSS_SELECTOR, "select#grid-paging-select>option"))
        for i in range(len(page)):
            #sleep(1)
            driver.implicitly_wait(60)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            super().add_company([i.getText() for i in soup.select('span.body-text')[0::2]])
            #str.translate()を試してみる
            super().add_brand(brand=[i.getText().replace("\xa0東証", "").replace("\xa0名証", "").replace("\xa0札証", "").replace("(単元未満)", "").strip() for i in soup.select('span.body-text')[1::2]])

            # 範囲を指定してスクリーンショットを撮る
            w = driver.execute_script('return document.body.scrollWidth')
            h = driver.execute_script('return document.body.scrollHeight')
            driver.set_window_size(w, h)
            png=WebDriverWait(driver, 30).until(lambda x: x.find_elements(By.CLASS_NAME, 'stockBalance'))

            # ファイルに保存
            for k in png:
                s=k.screenshot_as_png
                with open('stock/'+user+'/stock'+str(number)+'.png', 'wb') as f:
                    f.write(s)
                number+=1

            if i < len(page)-1:
                WebDriverWait(driver, 5).until(lambda x: x.find_element(By.CSS_SELECTOR, "a.next-page-btn")).click()

        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.XPATH, "//*[@id='common-header']/div[2]/ul[1]/li[10]")).click()
        WebDriverWait(driver, 30).until(lambda x: x.find_element(By.XPATH, "//*[@id='information-retrieval-top']/div/div[1]/ul[1]")).click()
        sleep(1)
        driver.switch_to.window(driver.window_handles[1])

        for i in super().get_brand():
            s = WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "input.form-control"))
            s.send_keys(i)
            WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "div.btn-default-green")).click()
            WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR, "ul.panel-tab > li:nth-child(1)")).click()
            sleep(1)
            html = driver.page_source

            soup = BeautifulSoup(html, 'html.parser')
            yutai=soup.select_one('div.value > div.value').get_text()
            profit=soup.select_one(".size-l > div:nth-child(2) > div.value").get_text()
            dividend=soup.select_one(".size-l > div:nth-child(3) > div.value").get_text()
            if dividend=="-円":
                super().add_dividend("0円")
            else:
                super().add_dividend(dividend)

            super().add_profit(profit)

            if yutai=="あり":
                sleep(1)
                WebDriverWait(driver, 30).until(lambda x: x.find_element(By.CSS_SELECTOR,"div.value.link-text")).click()
                sleep(1)
                html = driver.page_source
                soup = BeautifulSoup(html, 'html.parser')
                self.add_yu_prof(soup.select_one('div.shareholder-value>div.panel-bg:nth-child(2)>div.value').getText())
                table=soup.select_one('table.table')
                td=table.find_all('td')
                t=""
                for u in td:
                    t+=(u.text+"\n")
                super().add_yutai(t)
            else:
                self.add_yu_prof("0%")
                super().add_yutai("情報なし")

        driver.close()
        driver.quit()

    def picture(self, user):
        dir_path = "./stock/"+user
        file_list = os.listdir(dir_path)
        size = len(file_list)
        for i in range(size):
            img = Image.open("./stock/"+user+"/stock"+str(i)+".png")
            img = img.crop((80, 0, 135, 16))
            img =self.add_margin(img,5,10,0,0,(255,255,255))

            text = self.tool.image_to_string(
                img,
                lang="eng",
                builder=pyocr.builders.DigitBuilder(tesseract_layout=6)
            )
            super().add_stock(text.replace(".",""))

    def sum(self):
        dividend=super().get_dividend()
        stock=super().get_stock()
        for i, j in zip(stock, dividend):
            total=float(i.replace(",",""))*float(j.replace("円",""))
            super().add_total(total)

browser=sys.argv            
id_pas=[]
r=mysql_info('matsui')
for user in r.getID_passwd():
  id_pas.append(account_info(user[0],user[1],user[2],user[3]))
"""
for user in id_pas:
    d=matsui(url)
    driver=d.selenium_access(browser)
    d.access(user.id, user.passwd)
    d.get_info()
    d.picture()
    d.sum()
    d.save_info(user.savename)
    d.insert(d.yu_prof, user.savename)
    shutil.rmtree('stock')
    os.mkdir('stock')
"""
u=int(browser[2])
d=matsui(url)
driver=d.selenium_access(browser)
d.access(id_pas[u].id, id_pas[u].passwd)
d.get_info(browser[2])
d.picture(browser[2])
d.sum()
d.save_info(id_pas[u].savename)
d.insert(d.yu_prof, id_pas[u].savename)
shutil.rmtree('stock/'+browser[2])
os.mkdir('stock/'+browser[2])