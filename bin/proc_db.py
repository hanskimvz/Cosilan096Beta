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

import time
import json
from math import floor
import threading

from functions_s import (configVars, TZ_OFFSET, log, dbconMaster, PROBE_INTERVAL, info_to_db, message)

# info_to_db('proc_db', change_log)
# message (change_log)

MYSQL = { 
    "commonParam": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.param'),
    "commonSnapshot": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.snapshot'),
    "commonCount": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.counting'),
    "commonHeatmap": configVars('software.mysql.db') +"." + configVars('software.mysql.db_common.table.heatmap'),
    "commonCountEvent": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.count_event'),
    "commonFace": configVars('software.mysql.db') + "." + configVars('software.mysql.db_common.table.face'),
    "customCount": configVars('software.mysql.db_custom.table.count'),
    "customHeatmap": configVars('software.mysql.db_custom.table.heatmap'),
    "customAgeGender": configVars('software.mysql.db_custom.table.age_gender'),
    "customSquare": configVars('software.mysql.db_custom.table.square'),
    "customStore": configVars('software.mysql.db_custom.table.store'),
    "customCamera": configVars('software.mysql.db_custom.table.camera'),
    "customCounterLabel": configVars('software.mysql.db_custom.table.counter_label'),
    "customRtCount": "realtime_counting",
}

#new function , real age number array to json str , 0,1,2,3,4 ~~99
def inc_age_value(json_str, age):
    if not json_str :
        json_str = ''
    json_str='[' + json_str + ']'
    arr = json.loads(json_str) #json to array
    for i in range(len(arr), 100) :
        arr.append(0)
		
    arr[age] +=1
    json_str = json.dumps(arr)	 #array to json
    return json_str[1:len(json_str)-1]

def inc_gender_value(json_str, gender):
# [int(male), int(female)]
    if not json_str :
        json_str = ''
	
    json_str='[' + json_str + ']'
    arr = json.loads(json_str) #json to array
    for i in range(len(arr),2) :
        arr.append(0)

    if str(gender).upper() =='MALE'	:
        gender = 0
    elif str(gender).upper() == 'FEMALE':
        gender = 1

    arr[gender] +=1
    json_str = json.dumps(arr)	 #array to json
    return json_str[1:len(json_str)-1]	

def dbNames(cursor):
    arr_db = []
    sq = "select db_name from " + MYSQL['commonParam'] + " where db_name != 'none' group by db_name"
    cursor.execute(sq)
    rows = cursor.fetchall()
    for row in rows :
        arr_db.append(row[0])

    return arr_db

def dateTss(tss):
    # tm_year=2021, tm_mon=3, tm_mday=22, tm_hour=21, tm_min=0, tm_sec=0, tm_wday=0, tm_yday=81, tm_isdst=-1
    year = int(tss.tm_year)
    month = int(tss.tm_mon) 
    day = int(tss.tm_mday)
    hour = int(tss.tm_hour)
    min = int(tss.tm_min)
    wday = int((tss.tm_wday+1)%7)
    week = int(time.strftime("%U", tss))

    return (year, month, day, hour, min, wday, week)

def check_null_heatmap(body_csv):
    arr = json.loads("[" + body_csv + "0]")
    for t in arr :
        if t :
            return False
    return True

def procFaceDB():
    dbconn0 = dbconMaster()
    with dbconn0:
        cur = dbconn0.cursor()
        sq = "select A.pk, A.device_info, A.timestamp, A.datetime,  A.gender, A.age, B.db_name from " + MYSQL['commonFace'] + " as A inner join " + MYSQL['commonParam'] + " as B on A.device_info = B.device_info where A.flag='y' and A.flag_fd='y' and A.flag_ud='n' order by A.timestamp desc limit 100"
        # print (sq)
        cur.execute(sq)
        rows = cur.fetchall()
        
        if not rows:
            return False

        for row in rows :
            cpk, device_info, timestamp, datetime,  gender, age, db_name = row

            if db_name == 'none':
                # print (device_info + " is not assigned")
                continue

            ref_timestamp = int(floor(int(timestamp)/600)*600 + 600)
            sq = "select pk, age, gender from " + db_name +"." + MYSQL['customAgeGender'] + " where timestamp = %d and device_info = '%s' " %(ref_timestamp, device_info)
            # print (sq)
            cur.execute(sq)
            row = cur.fetchone()
            if not row :
                tss = time.gmtime(ref_timestamp)
                year, month, day, hour, min, wday, week = dateTss(tss)

                sqa = "select code, store_code, square_code from " + db_name + "." + MYSQL['customCamera'] + " where device_info = '%s'" %device_info
                cur.execute(sqa)
                rowa = cur.fetchone()
                camera_code, store_code, square_code = rowa
                
                record = (device_info, ref_timestamp, year, month, day, hour, min, wday, week, square_code, store_code, camera_code)

                sqa = "insert into " + db_name + "." + MYSQL['customAgeGender'] + "(device_info, timestamp, year, month, day, hour, min, wday, week, square_code, store_code, camera_code) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
                cur.execute(sqa, record)
                dbconn0.commit()
            
            cur.execute(sq)
            row = cur.fetchone()
            pk, age_b, gender_b = row
            
            json_age = inc_age_value(age_b, age)
            json_gender = inc_gender_value(gender_b, gender)
            
            sq = "update " + db_name + "." +  MYSQL['customAgeGender'] + " set age = %s, gender = %s where pk=%s"
            # print (sq)
            cur.execute(sq, (json_age, json_gender, pk))
            dbconn0.commit()		
            
            sq = "update " + MYSQL['commonFace'] + " set flag_ud = 'y' where pk = %s "
            # print (sq)
            cur.execute(sq, cpk)
            dbconn0.commit()
            # log.info(MYSQL['commonFace'] + " => " +  db_name + "." +  MYSQL['customAgeGender'] + " updated: %s " %datetime)
        
    return True

def procCountDB():
    dbconn0 = dbconMaster()
    with dbconn0:
        cur = dbconn0.cursor()
        arr_db = dbNames(cur)
        str_pk = ""
        str_upk = ""
        for db_name in arr_db:
            sq = "select A.pk, A.device_info, A.timestamp, A.datetime, A.counter_name, A.counter_val, B.db_name from " + MYSQL['commonCount'] + " as A inner join " + MYSQL['commonParam']  + " as B on A.device_info = B.device_info where A.flag='n' and B.db_name = '" + db_name +"' order by A.timestamp desc, A.status desc limit 100"
            cur.execute(sq)
            rows0 = cur.fetchall()

            arr_record = []
            for row0 in rows0 :
                cpk, device_info, timestamp, datetime, counter_name, counter_val, db_name = row0

                tss = time.strptime(str(datetime), "%Y-%m-%d %H:%M:%S")
                year, month, day, hour, min, wday, week = dateTss(tss)
    
                sq = "select A.code, A.store_code, A.square_code, B.counter_name, B.counter_label from " + db_name + "." + MYSQL['customCamera'] + " as A inner join " + db_name + "." + MYSQL['customCounterLabel'] + " as B on A.code = B.camera_code where A.device_info = '" + device_info + "' and B.counter_name = '" + counter_name + "' "
                # print (sq)
                cur.execute(sq) 
                row = cur.fetchone()
                if row :
                    if str_pk:
                        str_pk += " or "
                    str_pk += "pk=%d" %cpk
                    camera_code, store_code, square_code, counter_name_t, counter_label = row
                    arr_record.append((device_info, int(timestamp), year, month, day, hour, min, wday, week, counter_name, int(counter_val), counter_label, camera_code, store_code, square_code))
                else :
                    if str_upk:
                        str_upk += " or "
                    str_upk += "pk=%d" %cpk

            sq = "insert into " + db_name + "." + MYSQL['customCount'] + "(device_info, timestamp, year, month, day, hour, min, wday, week, counter_name, counter_val, counter_label, camera_code, store_code, square_code) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 

            # print (sq, arr_record)
            if arr_record:
                cur.executemany(sq, arr_record)
            # log.info( MYSQL['commonCount'] + " => " +  db_name + "." + MYSQL['customCount'] + " updated: %d " %len(arr_record))

        if str_pk:
            sq = "update " +  MYSQL['commonCount'] + " set flag='y', status=0 where ( %s )" %str_pk
            # print (sq)
            cur.execute(sq)

        if str_upk:
            sq = "update " +  MYSQL['commonCount'] + " set status=(status+1) where ( %s )" %str_upk
            # print (sq)
            cur.execute(sq)

        dbconn0.commit()


def procHeamapDB():
    dbconn0 = dbconMaster()
    with dbconn0:
        cur = dbconn0.cursor()
        arr_db = dbNames(cur)
        str_pk = ""
        for db_name in arr_db:
            sq = "select A.pk, A.device_info, A.timestamp, A.datetime, A.body_csv, B.db_name from " + MYSQL['commonHeatmap'] + " as A inner join " + MYSQL['commonParam'] + " as B on A.device_info = B.device_info where A.flag='n' and B.db_name = '" + db_name +"' order by A.timestamp desc limit 100"
            cur.execute(sq)
            rows0 = cur.fetchall()

            arr_record = []
            for row0 in rows0:
                cpk, device_info, timestamp, datetime, body_csv, db_name = row0
                if str_pk:
                    str_pk += " or "
                str_pk += "pk=%d" %cpk

                # print (datetime)
                tss = time.strptime(str(datetime), "%Y-%m-%d %H:%M:%S")
                # print (tss)
                year, month, day, hour, min, wday, week = dateTss(tss)

                if not check_null_heatmap(body_csv) :
                    sq = "select code, store_code, square_code from " + db_name + "." + MYSQL['customCamera'] + " where device_info = '" + device_info + "' "
                    cur.execute(sq)
                    row = cur.fetchone()
                    camera_code, store_code, square_code = row

                    arr_record.append((device_info, int(timestamp), year, month, day, hour, wday, week, body_csv, camera_code, store_code, square_code))                        
                    
                    # log.info( MYSQL['commonHeatmap'] + " => " +  db_name + "." + MYSQL['customHeatmap'] + " updated: %s " %datetime)	

            sq = "insert into  " + db_name + "." + MYSQL['customHeatmap'] + "(device_info, timestamp, year, month, day, hour, wday, week, body_csv, camera_code, store_code, square_code) values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" 
            # print (sq)
            if arr_record:
                cur.executemany(sq, arr_record)

        if str_pk:
            sq = "update " + MYSQL['commonHeatmap'] + " set flag = 'y' where %s" %str_pk
            # print (sq)
            cur.execute(sq)
        dbconn0.commit()

"""
CREATE TABLE `realtime_screen` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `name` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `enable` enum('yes', 'no') DEFAULT 'yes',
  `text` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `font` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `color` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `size` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `position` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `padding` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '[]',
  `ct_labels` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '["entrance", "exit"]',
  `rule` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `flag` enum('y','n')  DEFAULT 'n',
  PRIMARY KEY (`pk`)
)
"""
"""
CREATE TABLE `realtime_counting` (
  `pk` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `category` varchar(63) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `day_before` int(2) unsigned default 0,
  `ct_label` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `ct_value` int default 0,
  `latest` int(10) unsigned,
  `ref_date` datetime,
  PRIMARY KEY (`pk`)
)
"""
# def procRptCountingXXXX(day_before=0):
#     ts_midnight = int((time.time() + TZ_OFFSET) //(3600*24)) * 3600*24
#     arr = dict()

#     start_ts = ts_midnight - 3600*24*day_before
#     end_ts = ts_midnight + 3600*24 - 3600*24*day_before

#     if start_ts > int(time.time() + TZ_OFFSET):
#         start_ts -= 3600*24
#         end_ts -= 3600*24

#     # print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_ts)), " ~ ", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(end_ts)))
#     dbconn = dbconMaster()
#     with dbconn:
#         cur = dbconn.cursor()
#         arr_db = dbNames(cur)
#         for db_name in arr_db:
#             arr_sq = []
#             sq = "select code, open_hour, close_hour, apply_open_hour from %s.%s " %(db_name, MYSQL['customStore'])
#             # print (sq)
#             cur.execute(sq)
#             for row in cur.fetchall():
#                 # print(db_name, row)
#                 if row[3]=='n' :
#                     arr_sq.append("(store_code='%s')" %row[0])
#                 elif row[1] < row[2] :
#                     arr_sq.append("(store_code='%s' and hour>=%d and hour < %d)" %(row[0], row[1], row[2]) )
            
#             if arr_sq:
#                 sq_work = ' or '.join(arr_sq)
#                 sq_work = "and (%s)" %sq_work
#             # print (sq_work)
#             sq = "select counter_label, sum(counter_val) as sum, max(timestamp) as latest_ts from %s.count_tenmin where timestamp >= %d and timestamp < %d %s group by counter_label" %(db_name, start_ts, end_ts, sq_work)
#             # print (sq)
#             cur.execute(sq)
#             rows = cur.fetchall()
#             if not rows:
#                 sq = "update %s.%s set text='0' where name='%d' " %(db_name, MYSQL['customRtCount'], day_before)
#                 # print (sq)
#                 cur.execute(sq)
#             for row in rows:
#                 sq = "select pk from %s.%s where category='crpt' and name='%d' and ct_labels='%s'" %(db_name, MYSQL['customRtCount'], day_before, row[0])
#                 r = cur.execute(sq)
#                 if r:
#                     pk = cur.fetchone()[0]
#                     sq = "update %s.%s set text='%s', position='%s', font='%s' where pk = %d" %(db_name, MYSQL['customRtCount'], str(row[1]), str(row[2]), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[2])), pk)
#                 else :
#                     sq = "insert into %s.%s (category, name, ct_labels, text, position, font) values('crpt','%s', '%s','%s', '%s') " %(db_name, MYSQL['customRtCount'], day_before, row[0], str(row[1]), str(row[2]), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[2])))
#                 # print(sq)
#                 cur.execute(sq)
#                 # log.info("rt_screen updated %s %d" %(db_name, day_before))
#             dbconn.commit()
            
def procRptCounting(day_before=0):
    ts_midnight = int((time.time() + TZ_OFFSET) //(3600*24)) * 3600*24
    arr = dict()

    start_ts = ts_midnight - 3600*24*day_before
    end_ts = ts_midnight + 3600*24 - 3600*24*day_before

    if start_ts > int(time.time() + TZ_OFFSET):
        start_ts -= 3600*24
        end_ts -= 3600*24

    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(start_ts)), " ~ ", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(end_ts)))
    dbconn = dbconMaster()
    with dbconn:
        cur = dbconn.cursor()
        arr_db = dbNames(cur)
        for db_name in arr_db:
            arr_sq = []
            sq = "select code, open_hour, close_hour, apply_open_hour from %s.%s " %(db_name, MYSQL['customStore'])
            # print (sq)
            cur.execute(sq)
            for row in cur.fetchall():
                # print(db_name, row)
                if row[3]=='n' :
                    arr_sq.append("(store_code='%s')" %row[0])
                elif row[1] < row[2] :
                    arr_sq.append("(store_code='%s' and hour>=%d and hour < %d)" %(row[0], row[1], row[2]) )
            
            if arr_sq:
                sq_work = ' or '.join(arr_sq)
                sq_work = "and (%s)" %sq_work
            # print (sq_work)
            sq = "select counter_label, sum(counter_val) as sum, max(timestamp) as latest_ts from %s.count_tenmin where timestamp >= %d and timestamp < %d %s group by counter_label" %(db_name, start_ts, end_ts, sq_work)
            # print (sq)
            cur.execute(sq)
            rows = cur.fetchall()
            if not rows:
                sq = "update %s.%s set ct_value='0' where category='crpt' and day_before='%d' " %(db_name, MYSQL['customRtCount'], day_before)
                cur.execute(sq)
            for row in rows:
                sq = "select pk from %s.%s where category='crpt' and day_before=%d and ct_label='%s'" %(db_name, MYSQL['customRtCount'], day_before, row[0])
                r = cur.execute(sq)
                if r:
                    pk = cur.fetchone()[0]
                    sq = "update %s.%s set ct_value=%d, latest=%d, ref_date='%s' where pk = %d" %(db_name, MYSQL['customRtCount'], int(row[1]), int(row[2]), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[2])), pk)
                else :
                    sq = "insert into %s.%s (category, day_before, ct_label, ct_value, latest, ref_date) values('crpt', %d, '%s',%d, %d, '%s') " %(db_name, MYSQL['customRtCount'], day_before, row[0], int(row[1]), int(row[2]), time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(row[2])))
                print(sq)
                cur.execute(sq)
                # log.info("rt_screen updated %s %d" %(db_name, day_before))
            dbconn.commit()
# procRptCounting(day_before=1)

# import sys
# sys.exit()

# import json
# arr_sq = []
# with open ('rtScreen.json', 'r', encoding='utf8')  as f:
#     body = f.read()
# arr_t = json.loads(body)
# arrs = arr_t['screen']
# # MYSQL = arr_t['mysql']
# # print (MYSQL)

# # print(arrs)

# aaa = arrs['title']
# aaa['enable'] = aaa.get('enable')
# if not aaa['enable']:
#     aaa['enable'] ='yes'
# w = aaa.get('width')
# h = aaa.get('height')
# if not h:
#     h = 1
# aaa['size'] =[w, h]
# px = aaa.get('padx')
# py = aaa.get('pady')
# if not px:
#     px = 0
# if not py:
#     py=0

# aaa['padding'] = [px, py]
# sq = "insert into cnt_demo.realtime_screen(category, name, enable, text, font, color, size, position, padding) values('title', '%s', '%s','%s','%s','%s','%s','%s','%s')" %(aaa['name'], aaa['enable'], aaa['text'], json.dumps(aaa['font']), json.dumps(aaa['color']), json.dumps(aaa['size']), json.dumps(aaa['position']), json.dumps(aaa['padding']))
# # print (sq)
# arr_sq.append(sq)
# bbb = arrs['sections']
# for aaa in bbb:
#     # print (aaa)
#     aaa['enable'] = aaa.get('enable')
#     if not aaa['enable']:
#         aaa['enable'] ='yes'    
#     w = aaa.get('width')
#     h = aaa.get('height')
#     if not h:
#         h = 1
#     aaa['size'] =[w, h]
#     px = aaa.get('padx')
#     py = aaa.get('pady')
#     if not px:
#         px = 0
#     if not py:
#         py=0
#     aaa['padding'] = [px, py]
#     sq = "insert into cnt_demo.realtime_screen(category, name, enable, text, font, color, size, position, padding) values('sections', '%s', '%s','%s','%s','%s','%s','%s','%s')" %(aaa['name'], aaa['enable'], aaa['text'], json.dumps(aaa['font']), json.dumps(aaa['color']), json.dumps(aaa['size']), json.dumps(aaa['position']), json.dumps(aaa['padding']))
#     # print (sq)
#     arr_sq.append(sq)

# db_con = dbconMaster()
# with db_con:
#     cur = db_con.cursor()
#     for sq in arr_sq:
#         print (sq)
#         cur.execute(sq)

#     db_con.commit()



# sys.exit()



# class thFaceDBCustomTimer():
#     def __init__(self, t=60):
#         self.name = "proc_face_db"
#         self.t = PROBE_INTERVAL
#         self.last = int(time.time())
#         self.thread = threading.Timer(1, self.handle_function)

#     def handle_function(self):
#         self.main_function()
#         self.last = int(time.time())
#         self.thread = threading.Timer(self.t, self.handle_function)
#         self.thread.start()
    
#     def main_function(self):
#         procFaceDB()
   
#     def start(self):
#         str_s = "Starting processing face db Service"
#         print(str_s)
#         log.info (str_s)
#         self.last = int(time.time())
#         self.thread.start()

#     def is_alive(self) :
#         if int(time.time()) - self.last > 300:
#             return False
#         return True

#     def cancel(self):
#         str_s = "Stopping processing face db Service"
#         print(str_s)
#         log.info(str_s)
#         self.thread.cancel()

#     def stop(self):
#         self.cancel()       


# class ThFaceDBCustom(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self, name='proc_face_db')
#         self.daemon = True
#         self.running = True
#         self.last = int(time.time())
#         self.interval = PROBE_INTERVAL

#     def run(self):
#         str_s = "Starting processing face db Service"
#         print(str_s)
#         log.info (str_s)
#         while self.running:
#             rs = procFaceDB()
#             self.last = int(time.time())
#             time.sleep(self.interval)
#         str_s = "Stopping processing face db Service"
#         print(str_s)
#         log.info(str_s)

#     def stop(self):
#         self.running = False


# class thCountingDBCustomTimer():
#     def __init__(self, t=60):
#         self.name = "proc_count_db"
#         self.t = PROBE_INTERVAL
#         self.last = int(time.time())
#         self.thread = threading.Timer(1, self.handle_function)
 
#     def handle_function(self):
#         self.main_function()
#         self.last = int(time.time())
#         self.thread = threading.Timer(self.t, self.handle_function)
#         self.thread.start()
    
#     def main_function(self):
#         procCountDB()
   
#     def start(self):
#         str_s = "Starting processing counting db Serivice"
#         print(str_s)
#         log.info (str_s)
#         self.last = int(time.time())
#         self.thread.start()

#     def is_alive(self) :
#         if int(time.time()) - self.last > 300:
#             return False
#         return True

#     def cancel(self):
#         str_s = "Stopping processing counting db Service"
#         print(str_s)
#         log.info(str_s)
#         self.thread.cancel()

#     def stop(self):
#         self.cancel()


# class ThCountingDBCustom(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self, name='proc_count_db')
#         self.daemon =  True
#         self.running = True
#         self.last = int(time.time())
#         self.interval = PROBE_INTERVAL
        
#     def run(self):
#         str_s = "Starting processing counting db service"
#         print(str_s)
#         log.info (str_s)
#         while self.running:
#             procCountDB()
#             self.last = int(time.time())
#             time.sleep(self.interval)
#         print ("stopping processing counting db")
#         log.info("stopping processing counting db")  

#     def stop(self):
#         self.running = False


# class thHeatmapDBCustomTimer():
#     def __init__(self, t=60):
#         self.name = "proc_heatmap_db"
#         self.t = PROBE_INTERVAL
#         self.last = int(time.time())
#         self.thread = threading.Timer(5, self.handle_function)

#     def handle_function(self):
#         self.main_function()
#         self.last = int(time.time())
#         self.thread = threading.Timer(self.t, self.handle_function)
#         self.thread.start()
    
#     def main_function(self):
#         procHeamapDB()
   
#     def start(self):
#         str_s = "Starting processing heatmap db Service"
#         print(str_s)
#         log.info (str_s)
#         self.last = int(time.time())        
#         self.thread.start()

#     def is_alive(self) :
#         if int(time.time()) - self.last > 300:
#             return False
#         return True

#     def cancel(self):
#         str_s = "Stopping processing heatmap db service"
#         print(str_s)
#         log.info (str_s)
#         self.thread.cancel()

#     def stop(self):
#         self.cancel()

# class ThHeatmapDBCustom(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self, name='proc_heatmap_db')
#         self.daemon = True
#         self.running = True
#         self.last = int(time.time())
#         self.interval = PROBE_INTERVAL
        
#     def run(self):
#         str_s = "Starting processing heatmap db Serivce"
#         print(str_s)
#         log.info (str_s)
#         while self.running:
#             procHeamapDB()
#             self.last = int(time.time())
#             time.sleep(self.interval)

#         str_s = "Stopping processing heatmap db Service"
#         print(str_s)
#         log.info (str_s)
    
#     def stop(self):
#         self.running = False


class thProcDBCustomTimer():
    def __init__(self, t=20):
        self.name = "proc_custom_db"
        self.t = PROBE_INTERVAL
        self.last = 0
        self.thread = threading.Timer(5, self.handle_function)
        self.date_flag = 0
        self.min_flag = 0

    def handle_function(self):
        self.main_function()
        self.last = int(time.time())
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()
    
    def main_function(self):
        ts = int(time.time())
        procCountDB()
        procHeamapDB()
        procFaceDB()
        # if int(ts // (3600*12)) != self.date_flag:
        #     procRptCounting(1)
        #     log.info("rt_screen updated, yesterday: %d != %d " %(int(ts // (3600*12)), self.date_flag))
        #     self.date_flag = int(ts // (3600*12))
        # if int(ts // 300) != self.min_flag:
        #     procRptCounting(0)
        #     log.info("rt_screen updated, today: %d != %d " %(int(ts // (300)), self.min_flag))
        #     self.min_flag = int(ts//300)

        te = int(time.time())
        self.t = PROBE_INTERVAL - (te - ts)
        if self.t <= 0:
            self.t = 1
   
    def start(self):
        str_s = "Starting processing counting, heatmap, face db service"
        print(str_s)
        log.info (str_s) 
        self.last = int(time.time())        
        self.thread.start()

    def is_alive(self) :
        if int(time.time()) - self.last > 600:
            return False
        return True

    def cancel(self):
        str_s = "Stopping processing ounting, heatmap, face db Service"
        print(str_s)
        log.info (str_s)
        self.thread.cancel()

    def stop(self):
        self.cancel()

if __name__ == '__main__':
    procRptCounting(0)
    pass
    # from functions_s import _th
    # tc = ThCountingDBCustom()
    # th = ThHeatmapDBCustom()
    # tf = ThFaceDBCustom()
    # _th['proc_count_db'] = thCountingDBCustomTimer()
    # _th['proc_heatmap_db'] = thHeatmapDBCustomTimer()
    # _th['proc_face_db'] = thFaceDBCustomTimer()


    # _th['proc_count_db'].start()
    # time.sleep(1)

    # _th['proc_heatmap_db'].start()
    # time.sleep(1)
    
    # _th['proc_face_db'].start()
    # time.sleep(1)


    # while True:
        # message("================================================================" )
        # message("%-20s %-24s %-10s %s" %("name", "Thread", "is alive", "last") )
        # message("----------------------------------------------------------------")        
        # message("%-20s %-24s %-10s %d" %(str(tc.name), str(tc.__class__.__name__),  tc.is_alive(), Running[tc.name]))
        # message("%-20s %-24s %-10s %d" %(str(th.name), str(th.__class__.__name__),  th.is_alive(), Running[th.name]))
        # message("%-20s %-24s %-10s %d" %(str(tf.name), str(tf.__class__.__name__),  tf.is_alive(), Running[tf.name]))
        # message()
        # time.sleep(5)


