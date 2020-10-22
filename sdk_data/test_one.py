import pymysql


HOST = '172.18.0.30' #if "MOBSF_DOCKER" in os.environ else '127.0.0.1'
PORT = 3306
USER = 'root'
PASSWD = '123456'
DB = 'mobsf'
CHARSET = 'utf8'
conn = pymysql.connect(
     host=HOST,
     port=PORT,
     user=USER,
     passwd=PASSWD,
     db=DB,
     charset=CHARSET
 )
cursor = conn.cursor()

count=0
a=1
with open('./sdk_data/staticanalyzer_so_and_sdk.sql','r') as f:
    for row in f.readlines():
        cursor.execute(row)
        a+=1
conn.commit()
conn.close()
