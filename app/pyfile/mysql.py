import pymysql

class mysql_info:
    def __init__(self, securities):
        self.securities=securities

    def getConnection(self):
        return pymysql.connect(
            host='completed-db-1',
            port=int(3306),
            db='pass_manage',
            user='root',
            passwd='root',
            charset='utf8',
        )

    def getID_passwd(self):
        conn = self.getConnection()
        cur = conn.cursor()
        sql = ('select * from users where company=%s;')
        cur.execute(sql,self.securities)
        id_pas = cur.fetchall()
        cur.close()
        conn.close()
        return id_pas	
        