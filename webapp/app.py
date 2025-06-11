import numpy as np
import pymysql
import socket
import threading
from crontab import CronTab
from flask import redirect
from flask import url_for
from flask import Flask,render_template,request
from flask_socketio import SocketIO

#インスタンス生成
app = Flask(__name__)

def getConnection():
  return pymysql.connect(
    host='completed-db-1',
    port=int(3306),
    db='pass_manage',
    user='root',
    passwd='root',
    charset='utf8',
  )

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/password/')
def password():
  conn = getConnection()
  cur = conn.cursor()
  sql = ('describe user;')
  cur.execute(sql)
  columns = cur.fetchall()
  sql =('select * from user order by company;')
  cur.execute(sql)
  datalist = cur.fetchall()

  cur.close()
  conn.close()
  return render_template('password.html',datalist=datalist,columns=columns)

@app.route('/add/',methods=['post','get'])
def add():
  text=request.form.getlist('add')
  if text[0]!="" and text[1]!="" and text[2]!="" and text[3]!="":
    conn = getConnection()
    cur = conn.cursor()
    #sql = 'insert into user (証券会社,ID,password,保存名) values (%s,%s,%s,%s);'
    sql = 'insert into user (company,ID,password,savename) values (%s,%s,%s,%s);'
    cur.execute(sql,(text[0],text[1],text[2],text[3]))
    cur.close()
    conn.commit()
    conn.close()
  return redirect(url_for("password"))

@app.route('/delete/',methods=['post','get'])
def delete():
  text = request.form.get('delete')
  conn = getConnection()
  cur = conn.cursor()
  sql = 'delete from user where ID= %s;'
  cur.execute(sql,text)
  cur.close()
  conn.commit()
  conn.close()
  return redirect(url_for("password"))

@app.route('/change/',methods=['post','get'])
def change():
  text=request.form.getlist('change')
  conn = getConnection()
  cur = conn.cursor()
  if text[0]=="証券会社" or text[0]=="company":
    #sql = 'UPDATE user SET 証券会社=%s WHERE 証券会社=%s;'
    sql = 'UPDATE user SET company=%s WHERE company=%s;'
    cur.execute(sql, (text[2],text[1]))
  elif text[0]=="ID":
    sql = 'UPDATE user SET ID=%s WHERE ID=%s;'
    cur.execute(sql, (text[2], text[1]))
  elif text[0]=="password":
    sql = 'UPDATE user SET password=%s WHERE password=%s;'
    cur.execute(sql, (text[2], text[1]))
  else:
    #sql = 'UPDATE user SET 保存名=%s WHERE 保存名=%s;'
    sql = 'UPDATE user SET savename=%s WHERE savename=%s;'
    cur.execute(sql, (text[2], text[1]))
  cur.close()
  conn.commit()
  conn.close()
  return redirect(url_for("password"))

@app.route('/regular/')
def regular():
  cron = CronTab(tabfile='set.tab')
  schedule=str(cron)
  sch=schedule.replace("python","").replace("/app/","").replace(".py","")
  return render_template('regular.html',sch=sch)

@app.route('/set/',methods=['post','get'])
def setter():
  text = request.form.getlist('set')
  t=int(len(text)/6)
  sch=np.reshape(text,[t,6])
  l=len(text)-1
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #s.setblocking(False)
  s.connect(("completed-selenium-chrome-1", 8000))
  for i in text:
    if text[l]!=i:
      i=i+' '
    s.send(i.encode("utf-8"))
  s.close()
  cron = CronTab()
  for i in sch:
    job=cron.new(command='python /app/'+i[5]+'.py')
    job.setall(i.tolist())
  cron.write('set.tab')
  return redirect(url_for("regular"))

@app.route('/manual/')
@app.route('/manual/<string:msg>')
def manual(msg=""):
  """
  if msg!="" or msg!="completed!":
    fin = threading.Thread(target=finish, name='thread1',daemon = True)
    fin.start()
    print(threading.active_count())
  """
  return render_template('manual.html',msg=msg)
"""
@app.route('/finish/')
def finish():
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #s.setblocking(False)
  s.connect(("completed-selenium-chrome-1", 8000))
  while True:
    msg=s.recv(1024)
    if msg.decode("utf-8")=="completed!":
      msg="completed!"
      s.close()
      return redirect(url_for("manual",msg=msg))

@app.route('/red/')
def red():
  man = threading.Thread(target=manual, name='thread0',daemon = True)
  man.start()
  fin = threading.Thread(target=finish, name='thread1',daemon = True)
  fin.start()
  print(threading.active_count())
"""
@app.route('/scraping/')
def scraping():
  return redirect('http://localhost:7900/?autoconnect=1&resize=scale&password=secret')

@app.route('/execution/',methods=['post','get'])
def execution():
  text = request.form.get('exe')
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  #s.setblocking(False)
  s.connect(("completed-selenium-chrome-1", 8000)) #クライアント側は相手ホスト名とポート番号を指定
  #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.send(text.encode("utf-8"))
  s.close()
  return redirect(url_for("manual",msg=text))

if __name__ == "__main__":
  #Webサーバ立ち上げ
  app.debug=True
  app.run(debug=True,host='0.0.0.0', threaded=True)
