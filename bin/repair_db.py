import time, sys, os
import shutil
import pymysql, sqlite3
import zipfile
from configparser import ConfigParser

# stop mysqld with command "mysqladmin shutdown -uroot -prootpass"
# 1.
# delete files in data folders except ibdata1 and my.ini
# 2.
# delete files in data folder ibdata1 and other files except my.ini
# execute once and if succeed copy original file ibdata1
# else 
#  

if os.name !=  'nt':
    print ("This program is running under Windows")
    sys.exit()


MYSQL_VERSION = "10.4.12"

a_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
# a_dir = "E:/COSILAN/TLSS_0.95/bin"
for i in range(10):
    # print (i, a_dir)
    if os.path.isdir(a_dir+"\\Mariadb"):
        break
    a_dir = os.path.dirname(a_dir)
# print (a_dir)
if (i==9) :
    print ("Error, cannot define ROOT_DIR, place program on the folder has mariadb")
    for t in range(10):
        print (10-t)
        time.sleep(1)
    sys.exit()
_ROOT_DIR = a_dir
# _ROOT_DIR = os.path.dirname( os.path.dirname(os.path.abspath(sys.argv[0])) )

print (_ROOT_DIR)

_ROOT_PASSWORD="rootpass"
bk_str = ""


def getMysqlPort():
    if os.name !='nt':
        return 3306
    c_sec = False
    with open (_ROOT_DIR + "/MariaDB/data/my.ini", "r") as f:
        body = f.read()

    for line in body.splitlines():
        if not line.strip()  or line.strip()[0] == '#':
            continue
        if line.strip()[0] == "[" :
            c_sec = True if line.strip() == "[mysqld]" else False

        if c_sec and line.strip().startswith("port"):
            mysql_port = int(line.split("=")[1].strip())
            return mysql_port
    return False

def runMysql(st) :
    global _ROOT_DIR
    global _ROOT_PASSWORD
    os.chdir(_ROOT_DIR + "/MariaDB/bin")
    if st == 'stop':
        a = os.popen("mysqladmin shutdown -uroot -p%s" %_ROOT_PASSWORD)
    elif st == 'start':
        a = os.popen("RunHiddenConsole.exe mysqld.exe")
    elif st=='basedir':
        a = os.popen('mysqladmin -uroot -prootpass variables | findstr basedir')
        p = a.read()
        if p.find("error: 'Can't connect to MySQL server") >0:
            return False

        for tab in p.split('|'):
            if tab.strip() and os.path.isdir(tab.strip()):
                return tab.strip()

        return False
    
    if st == 'start' or st == 'stop':
        p = a.read()
        print(p)

    a = os.popen("mysqladmin ping -uroot -p%s" %_ROOT_PASSWORD)
    p = a.read()
    if p.find("mysqld is alive") >=0:
        return True
    
    return False

def checkMysql():
    global _ROOT_DIR
    global _ROOT_PASSWORD
    os.chdir(_ROOT_DIR + "/MariaDB/bin")
    a = os.popen("mysqlcheck -r mysql tables_priv -u root -p%s" %_ROOT_PASSWORD)
    p = a.read()
    print(p)
    a = os.popen("mysqlcheck -u root -p%s --auto-repair -c --all-databases" %_ROOT_PASSWORD)
    p = a.read()
    print(p)
    a = os.popen("mysqlcheck -u root -p%s --auto-repair -c --all-databases" %_ROOT_PASSWORD)
    p = a.read()
    print(p)
    

def deleteUnessaryFiles():
    global _ROOT_DIR
    
    print ("delete unnessary files")
    for a,b,c in os.walk(_ROOT_DIR + "/Mariadb/data/"):
        if a.endswith("/data/"):
            files = c

    for file in files:
        if file == 'ibdata1' or file == 'my.ini' or  file == "mysql.ibd":
            continue
        fname = _ROOT_DIR+"/Mariadb/data/"+file
        os.unlink(fname)
        print(fname,"  deleted")


def mysqlINI():
    global _ROOT_DIR
    with open(_ROOT_DIR + "/DB_BACKUP/my.ini.bk", "r") as f:
        body = f.read()

    body_n = ""
    for line in body.splitlines():
        if line.strip().find("innodb_force_recovery")>=0:
            body_n += "innodb_force_recovery = 1\n"
            continue
        if not line.strip() or line.strip()[0] == '#':
            print (line)
            continue
        body_n += line.strip()+"\n"

    with open(_ROOT_DIR + "/Mariadb/data/my2.ini", "w") as f:
        f.write(body_n)

    # shutil.copy(_ROOT_DIR + "/DB_BACKUP/my.ini.bk", _ROOT_DIR + "/Mariadb/data/my.ini")

def addCtuerRight():
    host=''
    user='root'
    password = _ROOT_PASSWORD
    charset = 'utf8'
    port = getMysqlPort()
    dbcon = pymysql.connect(host=host, user=str(user), password=str(password),  charset=charset, port=port)
    cur = dbcon.cursor()
    arr_user = ['ct_user', 'admin', 'rt_user']
    for user in arr_user:
        sq = "select user from mysql.user where user='%s'" %user
        cur.execute(sq)
        rs = cur.fetchall()
        if rs:
            if user=='admin':
                sq = "GRANT ALL PRIVILEGES ON *.* TO 'admin'@'localhost';"
                cur.execute(sq)
            elif user == 'ct_user':
                sq =  "GRANT insert, select, update, delete, alter ON common.* TO 'ct_user'@'localhost';"
                cur.execute(sq)
                sq = "GRANT insert, select, update, delete, alter ON cnt_demo.* TO 'ct_user'@'localhost';"
                cur.execute(sq)
            elif user=='rt_user':
                sq = "GRANT select ON common.* TO 'rt_user'@'%';"
                cur.execute(sq)
                sq = "GRANT select ON cnt_demo.* TO 'rt_user'@'%';"
                cur.execute(sq)

            sq = "FLUSH PRIVILEGES;"
            cur.execute(sq)


            
    dbcon.close()
    return True

def checkCTuser():   
    host=''
    user='ct_user'
    password = '13579'
    charset = 'utf8'
    port = getMysqlPort()

    dbcon = pymysql.connect(host=host, user=str(user), password=str(password),  charset=charset, port=port)

    sq = " show databases"
    cur = dbcon.cursor()
    cur.execute(sq)
    dbs = cur.fetchall()
   
    arr = list()
    for db in dbs:
        arr.append(db[0])
    if not ('common' in arr and 'cnt_demo' in arr):
        return False
    
    arr_db_table = list()
    for db in arr:
        # print (db)
        sq = "show tables from " + db
        cur.execute(sq)
        tbls = cur.fetchall()
        for tbl in tbls:
            # print (tbl)
            arr_db_table.append((db, tbl[0]))


    for db, table in arr_db_table:
        if db == 'information_schema' or db == 'mysql' or db=='performance_schema' or db=='test':
            continue

        sq = "check table %s.%s" %(db, table)
        cur.execute(sq)
        rs = cur.fetchall()
        # print(rs)
        if not (rs[0][3] == 'OK') :
            return False
    dbcon.close()

    # print (arr_db_table)
    return True



def repairStep0():
    global _ROOT_DIR
    global bk_str

    mysql_base_dir = runMysql('basedir')
    if mysql_base_dir:
        p_a = os.path.abspath(os.path.dirname(mysql_base_dir))
        p_b = os.path.abspath(os.path.dirname(_ROOT_DIR+"/MariaDB/"))
        if (runMysql('status') and p_a != p_b):
            runMysql('stop') 
            time.sleep(2)

    print("backup ibdata1 and my.ini")
    shutil.copy(_ROOT_DIR + "/Mariadb/data/ibdata1", _ROOT_DIR + "/DB_BACKUP/ibdata1.%s" %bk_str)
    shutil.copy(_ROOT_DIR + "/Mariadb/data/mysql/db.MAI", _ROOT_DIR + "/DB_BACKUP/db.MAI.%s" %bk_str)
    if not  os.path.isfile( _ROOT_DIR + "/DB_BACKUP/my.ini.bk") : 
        shutil.copy(_ROOT_DIR + "/Mariadb/data/my.ini", _ROOT_DIR + "/DB_BACKUP/my.ini.bk")
    
    return True

def repairStep1():
    print ("Repair Mysql DB / Maria DB ")

    deleteUnessaryFiles()
    time.sleep(2)
    x = runMysql('stop')
    time.sleep(2)
    x = runMysql('start')
    time.sleep(2)
    print(x)

    if(x) :
        print("repair completed step1")
        return True
    return False

def repairStep2():
    global _ROOT_DIR
    # if fail, delete ibdata1 and start / stop and copy original ib_data1 and recovery
    # not a normal operation. execute success means that problem will be ibdata1
    x = runMysql('stop')
    time.sleep(2)
    deleteUnessaryFiles()
    os.unlink(_ROOT_DIR + "/Mariadb/data/ibdata1")
    x = runMysql('start')
    time.sleep(2)
    x = runMysql('status')
    print(x)
    if x:
        print("repair completed step2, and must start step3")
        return True

    print("repair completed step2, and must start step4 and step3")
    return False

def repairStep3():
    global bk_str
    #change ini file to innodb_force_recovery = 1, ibdata1 returns original
    x = runMysql('stop')
    time.sleep(2)
    shutil.copy(_ROOT_DIR + "/DB_BACKUP/ibdata1.%s" %bk_str, _ROOT_DIR + "/Mariadb/data/ibdata1")
    mysqlINI() # edit my.ini to recovery.. innodb_force_recovery = 1

    deleteUnessaryFiles()
    x = runMysql('start')
    time.sleep(2)
    if x:
        print("repair completed step3")
        shutil.copy(_ROOT_DIR + "/DB_BACKUP/my.ini.bk", _ROOT_DIR + "/Mariadb/data/my.ini")
        return True

    return False

def repairStep4():
    global bk_str
    shutil.copy(_ROOT_DIR + "/DB_BACKUP/db.MAI.%s" %bk_str, _ROOT_DIR + "/Mariadb/data/mysql/db.MAI")
    deleteUnessaryFiles()
    x = runMysql('start')
    time.sleep(2)
    if x:
        print("repair completed step4")
        shutil.copy(_ROOT_DIR + "/DB_BACKUP/my.ini.bk", _ROOT_DIR + "/Mariadb/data/my.ini")
        return True

    return False






bk_str = str(time.strftime("%Y%m%d%H%M%S"))

step = [False]*10

#  backup files
step[0] = repairStep0()

# delete unnecessary files
step[1] = repairStep1()

# delete ibdata
if not step[1]:
    step[2] = repairStep2()

if not step[1] :
    if not step[2]:
        step[4] = repairStep4()
        if step[4]:
            step[3] = repairStep3()
    else:
        step[3] = repairStep3()
        step[4] = True


print (step)

if step[1] or step[3]:
    print ("mysqld can startd")
    a = os.popen("mysqladmin ping -uroot -p%s" %_ROOT_PASSWORD)
    p = a.read()

    step[5] = checkCTuser()
    if not step[5]:
        step[6] = checkMysql()
        step[7] = addCtuerRight()

    if step[6] and step[7]:
        "repair completed"
    

else :
    print ("start mysqld failed")
    
print(step)
