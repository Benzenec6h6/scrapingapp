#server
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from urllib.parse import parse_qs, urlparse
from time import sleep
import numpy as np
import socket
import pymysql
import subprocess
from crontab import CronTab
import os
import glob

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("0.0.0.0", 8000))  # サーバ側は"0.0.0.0"とポート番号を指定
s.listen(5)
SCOPES = ["https://www.googleapis.com/auth/drive"]
text="completed!"
email="rp3ppsrcpf58icls71take@gmail.com"

def getConnection():
  return pymysql.connect(
    host='completed-db-1',
    port=int(3306),
    db='pass_manage',
    user='root',
    passwd='root',
    charset='utf8',
  )

auth_url=None
def new_auth():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        #tokenの有効期限が切れたら更新
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob'
            )
            current_url = flow.authorization_url()[0]
            res: dict[str, list[str]] = parse_qs(urlparse(current_url).query)
            if "redirect_uri" in res.keys():
                auth_url = str(current_url)

            driver = webdriver.Remote(
                command_executor = os.environ["SELENIUM_URL"],
                options = webdriver.ChromeOptions()
                #options.add_argument("--user-data-dir=./Default")
                #options.add_argument("--profile-directory=Default")
            )
            driver.get(auth_url)
            sleep(3)
            username = driver.find_element(By.ID, "identifierId")
            username.send_keys(email)
            sleep(30)
            #creds = flow.run_local_server(open_browser=False)
            #creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        """
        with open("token.json", "w") as token:
            token.write(creds.to_json())
        """

def delete(name):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # Google Drive APIクライアントを作成
    service = build('drive', 'v3', credentials=creds)

    file = service.files().list(
        q="'1qSiPOJ5fRYYVrEp2Uq604ualYme6Ko1R' in parents and mimeType='text/csv' and trashed = false",
        pageSize = 30,
        fields = "nextPageToken, files(id, name)"
    ).execute()

    items = file.get("files", [])

    for item in items:
        if name in item['name']:
            print(f"{item['name']} ({item['id']})")
            file = service.files().delete(
                fileId=item['id']
            ).execute()

def upload(name):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Google Drive APIクライアントを作成
    drive_service = build('drive', 'v3', credentials=creds)

    # アップロードするファイルの情報
    file_path = glob.glob('./csv/'+name+'*.csv')

    for f in file_path:
        file_name = os.path.basename(f)
        file_metadata = {
            'name': file_name,
            'mimeType': 'text/csv',
            'parents': ['1qSiPOJ5fRYYVrEp2Uq604ualYme6Ko1R'],  # ファイルID(ドライブURIの’folders/’に続く値)
        }

        # ファイルをアップロード
        media = MediaFileUpload(f, mimetype='application/csv')
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True  # ポイント！
            ).execute()

        print(f'File ID: {file.get("id")}')

def callsavename(name):
  conn = getConnection()
  cur = conn.cursor()
  sql = ('select savename from user where company=%s;')
  cur.execute(sql,name)
  savename = cur.fetchall()
  return savename

while True:
    try:
        # データ受信
        client, addr = s.accept()
        data = client.recv(4096) #ここでデータ受け取り
        if data.decode("utf-8")=="rakuten":
            #subprocess.run(["python","rakuten.py"])
            names=callsavename('rakuten')
            for name in names:
                new_auth()
                delete(name[0])
                upload(name[0])
                #file_path=glob.glob('/app/csv/'+name[0]+'*.csv')
                #for i in file_path:
                    #os.remove(i)
            client.send(text.encode("utf-8"))
            print("rakuten")
        elif data.decode("utf-8")=="gmoclick":
            subprocess.run(["python","gmoclick.py"])
            names=callsavename('gmoclick')
            for name in names:
                delete(name[0])
                upload(name[0])
                file_path=glob.glob('/app/csv/'+name[0]+'*.csv')
                for i in file_path:
                    os.remove(i)
            client.send(text.encode("utf-8"))
            print("gmoclick")
        elif data.decode("utf-8")=="matsui":
            subprocess.run(["python","matsui.py"])
            names=callsavename('matsui')
            for name in names:
                delete(name[0])
                upload(name[0])
                file_path=glob.glob('/app/csv/'+name[0]+'*.csv')
                for i in file_path:
                    os.remove(i)
            client.send(text.encode("utf-8")) 
            print("matsui")
        elif data.decode("utf-8")=="SBI":
            subprocess.run(["python","SBI.py"])
            names=callsavename('SBI')
            for name in names:
                delete(name[0])
                upload(name[0])
                file_path=glob.glob('/app/csv/'+name[0]+'*.csv')
                for i in file_path:
                    os.remove(i)
            client.send(text.encode("utf-8")) 
            print("SBI")
        else:
            sch=data.decode("utf-8")
            sch=sch.split(" ")
            t=int(len(sch)/6)
            print(sch)
            sch=np.reshape(sch,[t,6])
            cron = CronTab()
            for i in sch:
              job=cron.new(command='python /app/'+i[5]+'.py')
              job.setall(i.tolist())
            cron.write('/etc/cron.d/set.tab')
            print(sch)
    except Exception as e:
        error=str(e)
        client.send(error.encode("utf-8"))
        print(error)

#cron -l
#/etc/init.d/cron restart
