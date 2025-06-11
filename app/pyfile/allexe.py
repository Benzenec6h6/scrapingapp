from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pymysql
import subprocess
import os
import glob

comp=["SBI","matsui","gmoclick","rakuten"]

def getConnection():
  return pymysql.connect(
    host='completed-db-1',
    port=int(3306),
    db='pass_manage',
    user='root',
    passwd='root',
    charset='utf8',
  )

def delete(name):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
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
    SCOPES = ["https://www.googleapis.com/auth/drive"]
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

for i in comp:
    c=i+".py"
    subprocess.run(["python",c])
    names=callsavename(i)
    for name in names:
        delete(name[0])
        upload(name[0])
        file_path=glob.glob('/app/csv/'+name[0]+'*.csv')
            for i in file_path:
                os.remove(i)
    print(i)