import subprocess
import time

# broadcasting by flag = 88, channel = 0xc1
def Broadcast(data):
    print "broadcasting data: ", data
    subprocess.call("sudo hciconfig hci0 up",shell=True);
    subprocess.call("sudo hciconfig leadv 3",shell=True);
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000A 01",shell=True)
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 88 " + data,shell=True)
    #subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 88 02 c1 11 03 c2 22 22 02 c3 33",shell=True)
    # demo
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 88 xx c1 03 01 00",shell=True)
