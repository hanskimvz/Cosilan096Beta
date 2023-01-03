# Copyright (c) 2022, Hans kim

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time, os, sys
import re, json, base64
import pymysql
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import cv2 as cv
import numpy as np
from PIL import ImageTk, Image
import threading
import locale
import uuid


cwd = os.path.abspath(os.path.dirname(sys.argv[0]))
os.chdir(cwd)

TZ_OFFSET = 3600*8

ARR_CRPT = dict()
ARR_CONFIG = dict()
ARR_SCREEN = list()

USE_SNAPSHOT = False

root = None
menus = dict()
var = dict()
lang = dict()

editmode = False
selLabel = None
templateFlag = True  # True : need read, False : no need to read

def updateVariables(_root=None, _menus=None, _var=None, _lang=None, _editmode=None, _selLabel=None):
    global root, menus, var, lang, editmode, selLabel
    if _root !=None:
        root = _root
    if _menus != None:
        menus = _menus
    if _var != None:
        var = _var
    if _lang != None:
        lang= _lang
    if _editmode != None:
        editmode = _editmode
    if _selLabel != None:
        selLabel = _selLabel

def getMac():
	mac = "%012X" %(uuid.getnode())
	return mac

def dbconMaster(host='', user='', password='',  charset = 'utf8', port=0): #Mysql
    global ARR_CONFIG
    if not host:
        host=ARR_CONFIG['mysql']['host']
    if not user :
        user = ARR_CONFIG['mysql']['user']
    if not password:
        password = ARR_CONFIG['mysql']['password']
    if not port:
        port = int(ARR_CONFIG['mysql']['port'])

    try:
        dbcon = pymysql.connect(host=host, user=str(user), password=str(password),  charset=charset, port=port)
    except pymysql.err.OperationalError as e :
        print (str(e))
        return None
    return dbcon   

def forgetLabel(label):
    global menus
    menus[label].place_forget()

def datetime_string():
    global timeshow_label
    if timeshow_label:
        dow = ["星期日","星期一","星期二","星期三","星期四","星期五","星期六"]
        w = dow[int(time.strftime("%w"))]
        text = time.strftime("%Y-%m-%d\n%H:%M:%S") + " " + w
        timeshow_label.config(text=text)
        timeshow_label.after(200, datetime_string)

def dateTss(tss):
    # tm_year=2021, tm_mon=3, tm_mday=22, tm_hour=21, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=81, tm_isdst=-1
    year = int(tss.tm_year)
    month = int(tss.tm_mon) 
    day = int(tss.tm_mday)
    hour = int(tss.tm_hour)
    min = int(tss.tm_min)
    wday = int((tss.tm_wday+1)%7)
    week = int(time.strftime("%U", tss))
    
def getSquare(cursor):
    sq = "select * from %s.square " %(ARR_CONFIG['mysql']['db'])
    cursor.execute(sq)
    return cursor.fetchall()

def getStore(cursor):
    sq = "select * from %s.store " %(ARR_CONFIG['mysql']['db'])
    cursor.execute(sq)
    return cursor.fetchall()

def getCamera(cursor):
    sq = "select * from %s.camera " %(ARR_CONFIG['mysql']['db'])
    cursor.execute(sq)
    return cursor.fetchall()

def getCounterLabel(cursor):
    sq = "select * from %s.counter_label " %(ARR_CONFIG['mysql']['db'])
    cursor.execute(sq)
    return cursor.fetchall()

def getDevices(cursor, device_info=''):
    sq = "select pk, device_info, usn, product_id, lic_pro, lic_surv, lic_count, face_det, heatmap, countrpt, macsniff, write_cgi_cmd, initial_access, last_access, db_name, url, method, user_id, user_pw from common.params "
    if device_info:
        sq += " where device_info='%s'" %device_info
    else :
        sq += " where db_name='%s'" %(ARR_CONFIG['mysql']['db'])
    cursor.execute(sq)
    return cursor.fetchall()

def getSnapshot(cursor, device_info):
    sq = "select body from common.snapshot where device_info='%s' order by regdate desc limit 1" %(device_info)
    cursor.execute(sq)
    body = cursor.fetchone()

    if body:
        return body[0]
    return False


def loadConfig():
    global lang, ARR_CONFIG

    with open ('%s\\rtScreen.json' %cwd, 'r', encoding='utf8')  as f:
        body = f.read()
    ARR_CONFIG = json.loads(body)        

    LOCALE = locale.getdefaultlocale()
    if LOCALE[0] == 'zh_CN':
        selected_language = 'Chinese'
    elif LOCALE[0] == 'ko_KR':
        selected_language = 'Korean'
    else :
        selected_language = 'English'

    for s in ARR_CONFIG['language']:
        lang[s['key']] = s[selected_language]

    # MYSQL = ARR_CONFIG['mysql']
    if not ARR_CONFIG['refresh_interval'] :
        ARR_CONFIG['refresh_interval'] = 2

    if not ARR_CONFIG['full_screen']:
        ARR_CONFIG['full_screen'] = "no"

def getScreenData(force = 0):
    global ARR_CONFIG, templateFlag, ARR_SCREEN
    if templateFlag or force:
        with open ("%s\\%s" %(cwd, ARR_CONFIG['template']), 'r', encoding="utf-8") as f:
            body = f.read()
            print ('readed template')
        ARR_SCREEN = json.loads(body)
        templateFlag = False

def putSections():
    global ARR_SCREEN, root, var, menus, editmode
    # print (root, editmode, selLabel)
    for rs in ARR_SCREEN:
        name = rs.get('name')
        if not (name.startswith('title') or name.startswith('label') or name.startswith('number') or name.startswith('snapshot') or name.startswith('video') or name.startswith('picture')):
            continue

        if not name in menus:
            menus[name] = Label(root)
            var[name] = StringVar()
            menus[name].configure(textvariable = var[name])
            print("create label %s" %name)

        if rs.get('flag') == 'n':
            menus[name].place_forget()
            continue
                
        if rs.get('text'):
            var[name].set(rs['text'])

        if rs.get('font'):
            menus[name].configure(font=tuple(rs['font']))
        if rs.get('color'):
            menus[name].configure(fg=rs['color'][0], bg=rs['color'][1])

        if rs.get('padding'):
            menus[name].configure(padx=rs['padding'][0], pady=rs['padding'][1])
        
        w, h = int(rs['size'][0]), int(rs['size'][1]) if rs.get('size') else (0, 0)
        posx, posy = (int(rs['position'][0]), int(rs['position'][1])) if rs.get('position') else (0, 0)

        if name.startswith('number'):
            menus[name].configure(anchor='e')
        elif name.startswith('picture') :
            imgPath = rs.get('url')
            if not (imgPath and os.path.isfile(imgPath)):
                imgPath = "cam.jpg"
            img = cv.imread(imgPath)
            img = Image.fromarray(img)
            img = img.resize((w, h), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            # menus[name].create_image(0, 0, anchor="nw", image=imgtk)
            menus[name].configure(image=imgtk)
            menus[name].photo=imgtk # phtoimage bug
            # imgPathOld[name] = imgPath

        elif name.startswith('snapshot'):
            if rs.get('device_info') :
                USE_SNAPSHOT = True
        elif name.startswith('video'):
            if rs.get('url') :
                USE_VIDEO = True
        
        if editmode and  selLabel == name:
                menus[name].configure(borderwidth=2, relief="groove")
        else :
            menus[name].configure(borderwidth=0)

        menus[name].configure(width=w, height=h)
        menus[name].place(x=posx, y=posy)


def getWorkingHour(cursor):
    arr_sq = list()
    sq_work = ""
    sq = "select code, open_hour, close_hour, apply_open_hour from %s.store " %(ARR_CONFIG['mysql']['db'])
    # print (sq)
    cursor.execute(sq)
    for row in cursor.fetchall():
        # print(db_name, row)
        if row[3]=='y' and  row[1] < row[2] :
            arr_sq.append("(store_code='%s' and hour>=%d and hour < %d)" %(row[0], row[1], row[2]) )
        else :
            arr_sq.append("(store_code='%s')" %row[0])
    
    if arr_sq:
        sq_work = ' or '.join(arr_sq)
        sq_work = "and (%s)" %sq_work
    return sq_work

def updateRptCounting(cursor):
    global ARR_CRPT
    ARR_CRPT = dict()
    # sq_work = getWorkingHour(cursor)
    # print("sqwork:", sq_work)
    sq_work = ""
    
    ts_now = int(time.time() + TZ_OFFSET)
    tsm = time.gmtime(ts_now)
    arr_ref = [
        {
            "ref_date": 'today',
            "start_ts" : int(ts_now //(3600*24)) * 3600*24,
            "end_ts" : int(time.time() + TZ_OFFSET),
        },
        {
            "ref_date" : 'yesterday',
            "start_ts" :  int(ts_now //(3600*24)) * 3600*24 - 3600*24,
            "end_ts" : int(ts_now //(3600*24)) * 3600*24,
            
        },
        {
            "ref_date" : 'thismonth',
            "start_ts" : int(time.mktime((tsm.tm_year, tsm.tm_mon, 1, 0, 0, 0, 0, 0, 0)) + TZ_OFFSET),
            "end_ts" : ts_now
        },
        {
            "ref_date" : 'thisyear',
            "start_ts" : int(time.mktime((tsm.tm_year, 1, 1, 0, 0, 0, 0, 0, 0)) + TZ_OFFSET),
            "end_ts" : ts_now
        }
    ]
    for arr in arr_ref:
        # print(arr)
        
        sq = "select device_info, counter_label, sum(counter_val) as sum, max(timestamp) as latest_ts from %s.count_tenmin where timestamp >= %d and timestamp < %d %s group by counter_label, device_info" %( ARR_CONFIG['mysql']['db'], arr['start_ts'], arr['end_ts'], sq_work)
        # print(arr['ref_date'], sq)
        cursor.execute(sq)
        for row in cursor.fetchall():
            # print (row)
            if not arr['ref_date'] in ARR_CRPT:
                ARR_CRPT[arr['ref_date']] = dict()
            if not row[0] in ARR_CRPT[arr['ref_date']]:
                ARR_CRPT[arr['ref_date']][row[0]] = dict()
            if not row[1] in ARR_CRPT[arr['ref_date']][row[0]]:
                ARR_CRPT[arr['ref_date']][row[0]][row[1]] = dict()

            ARR_CRPT[arr['ref_date']][row[0]][row[1]]['counter_val'] = row[2]
            ARR_CRPT[arr['ref_date']][row[0]][row[1]]['latest'] = row[3]
            ARR_CRPT[arr['ref_date']][row[0]][row[1]]['datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[3]))

            if not 'all' in ARR_CRPT[arr['ref_date']]:
                ARR_CRPT[arr['ref_date']]['all'] = dict()
            if not row[1] in ARR_CRPT[arr['ref_date']]['all']:
                ARR_CRPT[arr['ref_date']]['all'][row[1]] = {'counter_val':0, 'latest':0}


            ARR_CRPT[arr['ref_date']]['all'][row[1]]['counter_val'] += row[2]
            if (row[3] > ARR_CRPT[arr['ref_date']]['all'][row[1]]['latest']):
                ARR_CRPT[arr['ref_date']]['all'][row[1]]['latest'] = row[3]
                ARR_CRPT[arr['ref_date']]['all'][row[1]]['datetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[3]))

    for x in ARR_CRPT:
        for y in ARR_CRPT[x]:
            print (x, y, ARR_CRPT[x][y])
    
def getRtCounting(cursor):
    arr_t = dict()
    ct_mask =  list()
    if not ARR_CRPT.get('today'):
        return False

    for dev_info in ARR_CRPT['today']:
        for ct in ARR_CRPT['today'][dev_info]:
            if dev_info == 'all':
                continue
            ct_mask.append("(device_info = '%s' and counter_label='%s' and timestamp>%d)" %(dev_info, ct, ARR_CRPT['today'][dev_info][ct]['latest']))

    if (ct_mask) :
        sq_s = ' or '.join(ct_mask)
        sq_s = ' and (%s)' %(sq_s)
    sq = "select timestamp, counter_val, device_info, counter_label, counter_name from common.counting_event where db_name='%s' %s  order by timestamp asc " %(ARR_CONFIG['mysql']['db'], sq_s) 
    # print (sq)
    cursor.execute(sq)
    for row in cursor.fetchall():
        if not row[2] in arr_t:
            arr_t[row[2]] = dict()
        if not row[3] in arr_t[row[2]]:
            arr_t[row[2]][row[3]] = {'min': row[1], 'max':0, 'diff':0} 

        arr_t[row[2]][row[3]]['max'] = row[1]
        arr_t[row[2]][row[3]]['diff'] = abs(row[1] - arr_t[row[2]][row[3]]['min'])

        if not 'all' in arr_t:
            arr_t['all'] = dict()
        if not row[3] in arr_t['all']:
            arr_t['all'][row[3]] = {'min':0, 'max':0, 'diff':0} 

    for dev_info in arr_t:
        if dev_info == 'all':
            continue
        for ct in arr_t[dev_info]:
            arr_t['all'][ct]['diff'] += arr_t[dev_info][ct]['diff'] 

    return arr_t

def parseRule(ss):
    regex= re.compile(r"(\w+\s*:\s*\w+)", re.IGNORECASE)
    calc_regex= re.compile(r"(\w+)\(", re.IGNORECASE)
    m = calc_regex.search(ss)
    calc = m.group(1) if m else 'sum'
    if not calc in ['sum', 'diff', 'div', 'percent']:
        return False
    arr = list()
    for m in regex.finditer(ss):
        dt, ct = m.group().split(":")
        arr.append((dt.strip(), ct.strip()))
    if not arr:
        return False
    return (calc, arr)

def getNumberData(cursor):
    global ARR_CRPT, ARR_SCREEN
    arr_number = list()
   
    for n in ARR_SCREEN:
        if n['name'].startswith('number'):
            exp = parseRule(n['rule'])
            if not (exp):
                continue
            calc, rule = exp
            arr_number.append({
                "name": n['name'],
                "device_info": n['device_info'],
                "calc": calc,
                "rule": rule,
                "text": 0,
                "flag": n['flag']
            })
    arr_rt = getRtCounting(cursor)
    for i, arr in enumerate(arr_number):
        if arr['flag'] == 'n':
            continue
        
        if arr.get('device_info'):
            dev_info = arr['device_info']
        else :
            arr_number[i]['text'] = 0
            continue
        num=0
        n = 0
        for j, (dt, ct) in enumerate(arr['rule']):
            if ARR_CRPT.get(dt) and ARR_CRPT[dt].get(dev_info) and ARR_CRPT[dt][dev_info].get(ct):
                n = ARR_CRPT[dt][dev_info][ct]['counter_val']
            else :
                print ("Error on rpt >> dt:", dt, "dev_info:", dev_info, "ct:", ct)

            if dt != 'yesterday' :
                if arr_rt :
                    if arr_rt.get(dev_info) and arr_rt[dev_info].get(ct):
                        n += arr_rt[dev_info][ct]['diff']
                    else :
                        print ("Error on rt >> dev_info:", dev_info, "ct:", ct)
                else:
                    print ("Error on rt >> arr_rt is null")
            if j == 0:
                num = n
            
            elif arr['calc'] == 'sum':
                num += n
            
            elif arr['calc'] == 'diff':
                num -= n
                    
        if arr['calc'] == 'div' or arr['calc'] == 'percent' and n:
                num = "%3.2f %%"  %(num/n *100) if  arr['calc'] == 'percent' else "%3.2f"  %(num/n)

        arr_number[i]['text'] = num

    for n in arr_number:
        print (n)
    
    return arr_number  

def changeNumbers(arr):
    for rs in arr:
        if var.get(rs['name']):
            var[rs['name']].set(rs.get('text'))


def changeSnapshot(cursor):
    global ARR_SCREEN, menus
    for rs in ARR_SCREEN:
        name = rs.get('name')
        w, h = int(rs['size'][0]), int(rs['size'][1]) if rs.get('size') else (0, 0)
        if name.startswith('snapshot'):
            imgb64 = getSnapshot(cursor, rs.get('device_info'))
            if imgb64:
                imgb64 = imgb64.decode().split("jpg;base64,")[1]
                body = base64.b64decode(imgb64)
                imgarr = np.asarray(bytearray(body), dtype=np.uint8)
                img = cv.imdecode(imgarr, cv.IMREAD_COLOR)
            else :
                img = cv.imread("./cam.jpg")
            img = Image.fromarray(img)
            img = img.resize((w, h), Image.LANCZOS)
            imgtk = ImageTk.PhotoImage(image=img)
            # menus[name].create_image(0, 0, anchor="nw", image=imgtk)
            menus[name].configure(image=imgtk)
            menus[name].photo=imgtk # phtoimage bug
            # imgPathOld[name] = imgPath

class playVideo():
    def __init__(self, label_n, cap):
        self.cap = cap
        self.interval = 10 
        self.label= label_n
        self.w = 640
        self.h = 320
    def run(self):
        self.update_image()

    def update_image(self):    
        # Get the latest frame and convert image format
        self.OGimage = cv.cvtColor(self.cap.read()[1], cv.COLOR_BGR2RGB) # to RGB
        self.OGimage = Image.fromarray(self.OGimage) # to PIL format
        self.image = self.OGimage.resize((self.w, self.h), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.image) # to ImageTk format
        # Update image
        self.label.configure(image=self.image)
        # Repeat every 'interval' ms
        self.label.after(self.interval, self.update_image)

class showPicture(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.delay = ARR_CONFIG['refresh_interval']
        self.Running = True
        self.exFlag = False
        self.i = 0

    def run(self):
        imgPathOld =  dict()
        thx = dict()
        cap=None
        while self.Running :
            if self.i == 0:
                for rs in ARR_SCREEN:
                    name  = rs.get('name')
                    if rs.get('flag')=='n':
                        continue
                    if not name in menus:
                        menus[name] = Label(root, borderwidth=0)
                        # menus[name] = Canvas(root)

                    if name.startswith('picture') :
                        imgPath = rs.get('url')
                        w, h = rs.get('size')
                        if not imgPath :
                            continue
                        print (imgPath)
                        img = cv.imread(imgPath)
                        # img = cv.resize(img, (int(w), int(h)))
                        img = Image.fromarray(img)
                        img = img.resize((int(w), int(h)), Image.LANCZOS)
                        imgtk = ImageTk.PhotoImage(image=img)
                        # menus[name].create_image(0, 0, anchor="nw", image=imgtk)
                        menus[name].configure(image=imgtk)
                        menus[name].photo=imgtk # phtoimage bug
                        menus[name].configure(width=int(w), height=int(h))
                        menus[name].place(x=int(rs['position'][0]), y=int(rs['position'][1]))
                        imgPathOld[name] = imgPath
                    
                    elif name.startswith('video'):
                       
                        imgPath = rs.get('url')
                        w, h = rs.get('size')
                        if not imgPath:
                            continue
                        print (imgPath)
                        if imgPathOld.get(name) != imgPath:
                            if cap:
                                cap.release()
                            cap = cv.VideoCapture(imgPath)
                            thx[name] = playVideo(menus[name], cap)
                            thx[name].run()
                            print ("cap init")
                            imgPathOld[name] = imgPath
                        menus[name].configure(width=int(w), height=int(h))
                        thx[name].w = int(w)
                        thx[name].h = int(h)
                        menus[name].place(x=int(rs['position'][0]), y=int(rs['position'][1]))
                            
                            
                        
                        if self.Running == False:
                            cap.release()
                            cv.destroyAllWindows()
                            break
                    
            self.i += 1
            if self.i > self.delay:
                self.i = 0
            # print (self.i)
            time.sleep(1)
        # if cap:
        #     cap.release()
        self.exFlag = True       

    def stop(self):
        self.Running = False

class procScreen(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.delay = ARR_CONFIG['refresh_interval']
        self.Running = True
        self.exFlag = False
        self.i = 0

    def run(self):
        while self.Running :
            if self.i == 0 :
                getScreenData()
                putSections()

            self.i += 1
            if self.i > self.delay:
                self.i = 0
            # print (self.i)
            time.sleep(1)
        self.exFlag = True
                
    def stop(self):
        self.Running = False

class getDataThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.delay = ARR_CONFIG['refresh_interval']
        self.Running = True
        self.exFlag = False
        self.last = 0
        self.i = 0

    def run(self):
        self.dbcon = dbconMaster()
        while self.Running :
            if self.i == 0 :
                self.cur = self.dbcon.cursor()
                if int(time.time())-self.last > 300:
                # if (int(time.time())%300) < 2: #every 5minute
                    try:
                        updateRptCounting(self.cur)
                        self.last = int(time.time())
                    except Exception as e:
                        print (e)
                        time.sleep(5)
                        self.dbcon = dbconMaster()
                        print ("Reconnected")
                        continue
                
                changeSnapshot(self.cur)
                try :
                    arrn = getNumberData(self.cur)
                    self.dbcon.commit()
                except pymysql.err.OperationalError as e:
                    print (e)
                    time.sleep(5)
                    self.dbcon = dbconMaster()
                    print ("Reconnected")
                    continue

                # print(arrn)
                changeNumbers(arrn)
            
            self.i += 1
            if self.i > self.delay:
                self.i = 0
            # print (self.i)
            time.sleep(1)

        self.cur.close()
        self.dbcon.close()
        self.exFlag = True
                
    def stop(self):
        self.Running = False


loadConfig()

def getCRPT():
    return ARR_CRPT

def getSCREEN():
    return ARR_SCREEN

def getCONFIG():
    loadConfig()
    return ARR_CONFIG


# getScreenData()
# for x in ARR_CONFIG:
#     print (x)
