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

import os, time, sys
import base64
import threading

from functions_s import (active_cgi, list_device, checkAuthMode, configVars, addSlashes, log, modifyConfig, info_to_db, message)
from parse_functions import parseParam, parseCountReport, parseHeatmapData
from db_functions import(MYSQL, getWriteParam, putWriteParam, updateSimpleParam, updateParam, updateSnapshot, getLatestTimestamp, updateCountingReport, updateHeatmap, getDeviceListFromDB, getDeviceInfoFromDB)
from cgis import arr_cgi_str, set_datetime_str

 
def putParam(device_ip=None, port=80, authkey=None, cgis=[]):
    data = []
    for cgi in cgis:
        rs = active_cgi(device_ip, authkey, cgi.strip(), port)
        data.append(rs)
    return data

def getParam(device_ip=None, port=80, authkey=None,  device_family='IPN'):
    if not device_family:
        return False
    cgi_str = arr_cgi_str["param"][device_family]
    data = b''
    ex_cgi = cgi_str.split(',')
    for cgi in ex_cgi:
        rs = active_cgi(device_ip, authkey, cgi.strip(), port)
        if rs:
            data += rs

    data = data.replace(b"Brand.prodshortname", b"BRAND.Product.shortname")
    return (parseParam(data))

def getSnapshot(device_ip=None, port=80, authkey=None, device_family='IPN', format='b64'):
    if not device_family:
        return False    
    cgi_str = arr_cgi_str["snapshot"][device_family]
    data = active_cgi(device_ip, authkey, cgi_str, port)
    if format == 'b64':
        data = b'data:image/jpg;base64,' + base64.b64encode(data)
        data = addSlashes(data.decode('utf-8'))
    return data

def getCountReport(device_ip=None, port=80, authkey=None,  device_family='IPN', from_t='2022/01/01', to_t='now'):
    if not device_family:
        return False    
    cgi_str = arr_cgi_str["countreport"][device_family] %(from_t, to_t)
    data = active_cgi(device_ip, authkey, cgi_str, port)
    data = data.replace(b'Time:', b'Records:')
    return (parseCountReport(data))

def getHeatmap(device_ip=None, port=80, authkey=None,  device_family='IPN', from_t='2022-01-01', to_t='now'):
    if not device_family:
        return False
    if not arr_cgi_str["heatmap"][device_family]:
        return False

    cgi_str = arr_cgi_str["heatmap"][device_family] %(from_t, to_t)
    data = active_cgi(device_ip, authkey, cgi_str, port)
    return (parseHeatmapData(data))

def testGetFunctions(dev_ip, userid, userpw):
    authkey, dev = checkAuthMode(dev_ip, userid, userpw)
    print (authkey, dev)
    param = getParam(device_ip=dev_ip, port=80, device_family=dev, authkey= authkey)
    print (param)
    snapshot = getSnapshot(device_ip=dev_ip, port=80, device_family=dev, authkey= authkey, format='b64')
    print (snapshot)
    crpt = getCountReport(device_ip=dev_ip, port=80, authkey=authkey,  device_family=dev, from_t='2022/01/01', to_t='now')
    print (crpt)
    hm = getHeatmap(device_ip=dev_ip, port=80, authkey=authkey,  device_family=dev, from_t='2022-01-01', to_t='now')
    print(hm)



def writeParam(device_info='', device_ip=None, port=80, authkey=None,  device_family='IPN'):
    regdate = time.strftime("%Y-%m-%d %H:%M:%S")
    arr_cmd = getWriteParam(device_info)
    if (arr_cmd):
        message ("write cgi commands to %s at %s" %(device_info, regdate))
        putParam(device_ip=device_ip, port=port, authkey=authkey, cgis=arr_cmd)
        putWriteParam(device_info, [])
    return True  

def setDatetimeToDevice(device_ip=None, port=80, authkey=None,  device_family='IPN'):
    if not device_family:
        return False      
    if not set_datetime_str["read"][device_family]:
        return False
    cgi_str = set_datetime_str["read"][device_family]
    data = active_cgi(device_ip, authkey, cgi_str, port)
    arr = dict()
    for line in data.splitlines():
        sp_line = line.split(b"=")
        if len(sp_line) <2:
            print (line)
            continue
        arr[sp_line[0].decode().lower().strip()] = sp_line[1].decode().lower().strip()

    if arr.get('system.datetime.tz.name') != 'hong_kong':
        print ("setting timezone")
        for cgi_str in set_datetime_str["set_tz"][device_family]:
            x = active_cgi(device_ip, authkey, cgi_str, port)
            print (x)
        time.sleep(2)

    cgi_str = set_datetime_str["set_datetime"][device_family] %(time.strftime("%m%d%H%M%Y.%S"))
    print(cgi_str)
    x = active_cgi(device_ip, authkey, cgi_str, port)
    print (x)
    log.info("%s: Setting datetimezone OK" %device_ip)

def searchDeviceToDB():
# {'idx': 0, 'usn': 'HA0A0073A', 'url': 'http://192.168.1.58:49152/upnpdevicedesc.xml', 'location': '192.168.1.58', 'mac': '001323A0073A', 'model': 'NS202HD', 'brand': 'CAP'}
    arr_dev = list_device()
    
    for dev in arr_dev:
        if not (dev['mac'] and dev['brand'] and dev['model']) :
            msg = "device_info Error mac:%s, brand:%s, model:%s " %(dev['mac'], dev['brand'], dev['model'])
            log.warning (msg)
            message (msg)
            continue

        message(dev)
        device_info = "mac=%s&brand=%s&model=%s" %(dev['mac'], dev['brand'], dev['model'])
        updateSimpleParam(device_info, dev['usn'], dev['location'])
    strn = "browsing devices %d and info to db succeed" %len(arr_dev)
    message (strn)
    log.info(strn)

def procActive():
    n= 0 
    set_date_flag = False
    arr_dev = getDeviceListFromDB()
    if int(configVars('software.status.datetime_sync')) + 3600*24 < int(time.time()) :
        set_date_flag = True
        log.info("Setting device time")

    for dev in arr_dev:
        if not dev['online']:
            continue
        # print(dev)
        if not ( dev['authkey'] and dev['device_family']):
            strn = "%s: No authkey or device family" %dev['ip']
            message(strn)
            log.info(strn)
            continue

        try:
            writeParam(device_info=dev['device_info'], device_ip=dev['ip'], port=80, authkey=dev['authkey'],  device_family=dev['device_family'])

        except Exception as e:
            msg = "fail to write params: {0}".format(str(e))
            message(msg)
            log.error(msg)
        


        if set_date_flag:
            setDatetimeToDevice(device_ip=dev['ip'], port=80, authkey=dev['authkey'], device_family=dev['device_family'])
        
        param = getParam(device_ip=dev['ip'], port=80, authkey=dev['authkey'], device_family=dev['device_family'])
        if param:
            updateParam(device_info=dev['device_info'], param=param)
        else:
            log.error(dev['ip'] + " param retrieve wrong")

        snapshot = getSnapshot(device_ip=dev['ip'], port=80, authkey=dev['authkey'], device_family=dev['device_family'], format='b64')
        if snapshot:
            updateSnapshot(device_info=dev['device_info'], snapshot=snapshot)
        else:
            log.error(dev['ip'] + " snapshot retrieve wrong")
        
        #get counting report and heatmap report where db_name !=none and function=y
        dev_info = getDeviceInfoFromDB(dev['device_info'])
        if dev_info: # False if not in db
            if dev_info['db_name'] != 'none':
                if dev_info['countrpt'] == 'y':
                    from_t, readflag, ts = getLatestTimestamp(MYSQL['commonCounting'], device_info=dev['device_info'])
                    if readflag >600:
                        crpt = getCountReport(device_ip=dev['ip'], port=80, authkey=dev['authkey'], device_family=dev['device_family'], from_t=from_t, to_t='now-600')
                        if crpt:
                            updateCountingReport(device_info=dev['device_info'], arr_record=crpt)
                        else :
                            log.error(dev['ip'] + "CRTP is bool or wrong")

                if dev_info['heatmap'] == 'y':
                    from_t, readflag, ts = getLatestTimestamp(MYSQL['commonHeatmap'], device_info=dev['device_info'])
                    if readflag >3600:
                        from_t = time.strftime("%Y/%m/%d%%20%H:%M", time.gmtime(ts+3600))
                        hm = getHeatmap(device_ip=dev['ip'], port=80, authkey=dev['authkey'], device_family=dev['device_family'], from_t=from_t, to_t='now')
                        if hm:
                            updateHeatmap(device_info=dev['device_info'], arr_record=hm)
                        else :
                            log.error(dev['ip'] + "Heatmap is bool or wrong")


        modifyConfig('software.status.last_device_access', int(time.time()))
        n+=1

    if set_date_flag:
        modifyConfig('software.status.datetime_sync', int(time.time()))
        set_date_flag = False

    return n

class thActiveCountingTimer():
    def __init__(self, t=60):
        self.name = "active_count"
        self.t = t
        self.last = 0
        self.i = 0
        self.thread = threading.Timer(1, self.handle_function)

    def handle_function(self):
        self.main_function()
        self.last = int(time.time())
        self.thread = threading.Timer(self.t, self.handle_function)
        self.thread.start()
    
    def main_function(self):
        ts = time.time()
        str_s = "======== Active Counting, starting %d ========" %self.i
        log.info (str_s)
        message (str_s)
        searchDeviceToDB()

        n = procActive()
        te = time.time()
        self.t = 300 - int(te - ts) 
        if self.t  < 0:
            self.t  = 1
        str_s = "Online %d, elaspe time: %d, need %d sec sleep" %(n, (te-ts), self.t )
        message (str_s)
        log.info(str_s)
        
        self.i += 1

    def start(self):
        str_s = "starting Active Counting Service"
        message(str_s)
        log.info (str_s)
        self.last = int(time.time())
        self.thread.start()

    def is_alive(self):
        if int(time.time()) - self.last > 600 :
            return False
        return True
    
    def cancel(self):
        str_s = "stopping Active Counting Servce"
        message(str_s)
        log.info (str_s)
        self.thread.cancel()
    
    def stop(self):
        self.cancel()

# class ThActiveCounting(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self, name='active_count')
#         self.daemon = True
#         # self.TimeSetFlag = int(time.strftime("%m%d")) -1
#         self.running = True
#         self.i = 0
        
#     def run(self):
#         str_s = "starting Active Counting Service"
#         print(str_s)
#         log.info (str_s)

#         while self.running:
#             ts = int(time.time())
#             str_s = "======== Active Counting, starting %d ========" %self.i
#             log.info (str_s)
#             print (str_s)            
#             searchDeviceToDB()
        
#             # # if self.TimeSetFlag < int(time.strftime("%m%d")) and int(time.strftime("%H")) < 2: # Am 0:00 ~ 02:00, once
#             # if int(configVars('software.status.datetime_sync')) + 3600*24 < int(time.time()) :
#             #     log.info("Setting device time")
#             #     setDatetimeToDevice()
#             #     modifyConfig('software.status.datetime_sync', int(time.time()))
#             #     # self.TimeSetFlag = int(time.strftime("%m%d"))
#             #     self.i = 0
            
#             # num_online = getDataFromDevice()
            
#             n = procActive()
#             te = int(time.time)
#             dtime = 300 - (te - ts) 
#             if dtime < 0:
#                 dtime = 1

#             str_s = "Online %d, elaspe time: %d, need %d sec sleep" %(n, (te-ts), dtime )
#             print (str_s)
#             log.info(str_s)

#             # if not num_online:
#             #     self.Running = False
#             for t in range (dtime):
#                 time.sleep(1)
#                 if not self.running:
#                     return False

#             self.i += 1

#         print ("stopping Active Counting")
#         log.info ("stopping Active Counting")

#     def stop(self):
#         self.running = False





if __name__ == '__main__':

    dev_ip = "192.168.3.38" ;    userid = 'root';     userpw = 'pass'
    # dev_ip = "192.168.1.190";    userid = 'root';     userpw = 'pass'
    # dev_ip = "192.168.1.136";    userid = 'root';     userpw = 'Rootpass12345'
    # dev_ip = "z7.ziyanyun.com";    userid = 'root';     userpw = 'pass'
    # authkey, dev = checkAuthMode(dev_ip, userid, userpw)
    # print (authkey, dev)
    # setDatetimeToDevice(device_ip=dev_ip, port=80, authkey=authkey,  device_family=dev)

    # testGetFunctions(dev_ip, userid, userpw)
    # sys.exit()
    # x = searchDeviceToDB()
    # print(x)
    procActive()
    # tc = ThActiveCounting()
    # tc.start()
    # while True:
    #     time.sleep (100)
    
