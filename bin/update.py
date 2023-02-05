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

# wget http://49.235.119.5/download.php?file=../bin/update.py -O /var/www/bin/update.py
# update from github // V0.97

import time, sys, os
import socket
from http.client import HTTPConnection
import uuid

_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0])))
os.chdir(_ROOT_DIR + "\\bin")
# print(os.getcwd())

args = ""
for i, v in enumerate(sys.argv):
    if i==0 :
        continue
    args += v + " "

_UPDATE_PAGE = "https://github.com/hanskimvz/Cosilan097Beta/"

def checkAvailabe():
    # check updage page and vaild page ? some sites have protect web page from external sites
    if os.name == 'nt':
        cmd = _ROOT_DIR + "wget.exe https://raw.githubusercontent.com/hanskimvz/Cosilan097Beta/main/bin/filelist.json" 
    server = ("github.com", 80)
    conn = HTTPConnection(*server)
    conn.putrequest("GET", "/hanskimvz/Cosilan097Beta/blob/main/bin/filelist.json") 
    conn.endheaders()
    rs = conn.getresponse()
    print(rs.read())
    
    conn.close()
    # blob/main/bin/filelist.json
    # if not is_online(_SERVER_IP):
        # print ("unknown IP or cannot reach")
        # return False

    # _MyPublicIP = getMyPublicIP()
    # if _SERVER_IP != "" and _SERVER_IP == _MyPublicIP :
    #         print ("SERVER IP and LOCAL MACHINE IP is the same, cannot updated.")
    #         return False
    # mac = "%012X" %(uuid.getnode())
    # if _SERVER_MAC == mac :
    #     print ("SERVER MAC and LOCAL MACHINE MAC is the same, cannot updated.")
    #     return False

    # return True

checkAvailabe()
sys.exit()
def update():
    if not checkAvailabe():
        return False
    server = (_SERVER_IP, _SERVER_PORT)
    conn = HTTPConnection(*server)
    print ("Downloading update main file ....", end="")
    fname = "update_main.py"
    
    conn.putrequest("GET", "/download.php?file=bin/%s" %fname) 
    conn.endheaders()
    rs = conn.getresponse()
    if rs:
        with open("%s\\bin\\%s" %(_ROOT_DIR, fname), "wb")  as f:
            f.write(rs.read())
        
        print (".... download completed")
    conn.close()

    os.chdir("%s/bin" %_ROOT_DIR)
    
    if os.name == 'nt':
        os.system("python3.exe %s %s" %(fname, args))
    
    elif os.name == 'posix':
        os.system("/usr/bin/python3 %s" %fname )
    

if __name__ == '__main__':
    update()
    sys.exit()

