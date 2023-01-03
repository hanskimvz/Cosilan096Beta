
import os, sys, zipfile
print (sys.argv)
_ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))
kill_pid = sys.argv[1]
os.system("taskkill /pid %d /F" %(int(kill_pid)))
fname = "%s/python_bin_096_basic.zip"  %_ROOT_DIR
print ("extracting...")
extract_path = "%s/bin/" %_ROOT_DIR
zf = zipfile.ZipFile(fname,'r')
for fname in zf.namelist():
    try:
        zf.extract(fname, extract_path)
    except Exception as e:
        print (str(e))
zf.close()
print ("extract completed")
    