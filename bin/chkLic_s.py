import time, os, sys
from hashlib import md5
import uuid

def getMac():
	mac = "%012X" %(uuid.getnode())
	return mac

def genLic(mac, datetime):
	a = md5()
	a.update(("HANS").encode('ascii'))
	a.update(mac.encode('ascii'))
	m= a.hexdigest().upper()

	d = "%d    " %int(time.mktime(time.strptime(datetime,"%Y-%m-%d"))+3600*8 + 3600*24 -1) if datetime else ''

	result = ''
	j=0
	for i, b in enumerate(m):
		if d and i>0 and i%3 == 0:
			result += str(d[j])
			j += 1
		result += str(b)
		
	# print ("%s\r\n%s\r\n%s" %(m, result, d))
	return result

def chkLic(mac, lic_code):
	m = ''; d = ''
	for i, b in enumerate(lic_code) :
		if i%4 == 3:
			d += b
			continue
		m += str(b)
	# print ("%s\r\n%s\r\n%s" %(lic_code, m, d))
	
	mr = genLic(mac, 0)
	if m == mr :
		datetime = time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime(int(d)))
		return int(d), datetime, mac
	return False

def chkLicMachine(lic_code) :
	MAC = getMac()
	
	lic_info = chkLic(MAC, lic_code)
	if not lic_info :
		lic_info = (0, '', MAC)
	return lic_info


# if __name__ == '__main__':
	
# 	mac = '7C67A2C64BC4'
	# mac = '525400C9FE37'
#   mac = 'A61EF34C4F93'
# 	datetime = '2050-12-31'
# 	print (genLic(mac, datetime))

	# code = 'EDB24D657F657CC6E47157A4F733EDA9BBA984F9BF'
	# print (chkLic(mac, code))

