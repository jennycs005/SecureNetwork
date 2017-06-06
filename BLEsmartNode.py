import thread
import threading
import time
import bluetooth
import datetime
import os
import sys
import sensor
from bluepy.btle import Scanner, DefaultDelegate
import subprocess
import random

# for node this is a id which is assigned by server
# for server this is the id for assigning to the next incoming node, then PIID+=1

PIID = 0
rank=-1

# manually setup on the file
macAddr = ""

# the iterval time in second for scan the smart nodes
iterval_for_scan = 10
iterval_for_scan_random = 50
# the iterval time in secone for broadcasting the data
interval_for_sending = 1
interval_for_sending_random = 5

## delay for response
interval_for_response = 0

## fixed time for assign a new id
interval_for_assign_new_id = 60

# locker
mutex = threading.Lock()
mutex_scan = threading.Lock()

## mac -> ID table
macIDTable = {}



###############################################################
# broadcast simple example
# broadcast my rank
def Broadcast_Server_03_01():
    #time.sleep(interval_for_response)
    
    global rank
    
    irank = "00 "
    if (rank != -1):
        irank = "00" + (str)(rank)
        irank = irank[-2:] + " "
                
    data = "04 c1 03 01 " + irank
    print "broadcasting data: ", data
    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"Broadcast_Server_03_01|"+ data + '\n')
        input_file.close()
    
    subprocess.call("sudo hciconfig hci0 up",shell=True);
    subprocess.call("sudo hciconfig leadv 3",shell=True);
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000A 01",shell=True)

    # server rank    
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 88 "+ data,shell=True)

    interval = random.uniform(interval_for_sending,interval_for_sending_random)
    time.sleep(interval)

###############################################################
# broadcast simple example
# request a newest PIID
def Broadcast_Client_01_01():
    global rank,PIID,macAddr

    if (PIID > 0):
        return

    print "request a PIID."
    
    print "PIID: ", PIID

    data = ""

    # modify the data
    idd = "0000" + (str)(PIID)
    idd = idd[-4:]
    idd = idd[0] + idd[1] + " " + idd[2] + idd[3] + " "

    irank = "00 "
    if (rank != -1):
        irank = "00" + (str)(rank)
        irank = irank[-2:] + " "

    str_macAddr = macAddr.replace(":"," ") + " "
    
    data = "C1 " + "01 " + "01 " + idd + idd + irank + str_macAddr
    tdata = data.replace(" ","")
    
    # len of the data
    data = (str)(len(tdata)/2) + " " + data
    # broadcast
    BroadCast(data, 0)
    

###############################################################
# broadcast simple example
# upload the local data to server
def Broadcast_Client_01_02():
    global rank,PIID
    
    print "upload data."
    print "PIID: ", PIID
    print "rank: ", rank

    
    data = ""
    ctim = time.time()
    temp,hum = sensor.Tempture()
    print "temp,hum: ",temp, ",",hum
    power = sensor.Power_consumption()
    print "power consumption: ", power

    # modify the data
    temp = "00" + (str)(temp)
    temp = temp[-2:] + " "

    hum = "00" + (str)(hum)
    hum = hum[-2:] + " "

    power = "00" + (str)(power)
    power = power[-2:] + " "

    idd = "0000" + (str)(PIID)
    idd = idd[-4:]
    idd = idd[0] + idd[1] + " " + idd[2] + idd[3] + " "

    irank = "00 "
    if (rank != -1):
        irank = "00" + (str)(rank)
        irank = irank[-2:] + " "
    
    # make a data package

    data = "C1 " + "01 " + "02 " + idd + idd + irank + temp + hum + "00 " + power
    tdata = data.replace(" ","")
    
    # len of the data
    data = (str)(len(tdata)/2) + " " + data

    # broadcast
    BroadCast(data, 0)
    
###############################################################
def BroadCast(data,fixedtime):
    #time.sleep(interval_for_response)
    print "broadcasting data: ", data
    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"BroadCast|"+ data + '\n')
        input_file.close()
    subprocess.call("sudo hciconfig hci0 up",shell=True);
    subprocess.call("sudo hciconfig leadv 3",shell=True);
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x000A 01",shell=True)
    subprocess.call("sudo hcitool -i hci0 cmd 0x08 0x0008 1E 02 01 88 " + data,shell=True)

    interval = random.uniform(interval_for_sending,interval_for_sending_random) + fixedtime
    time.sleep(interval)

    
###############################################################
## client scan network
def ScanNetwork():
    global rank, iterval_for_scan, interval_for_sending, macAddr


    
    subprocess.call("sudo hciconfig hci0 piscan",shell=True);

    interval = random.uniform(iterval_for_scan,iterval_for_scan_random)

    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"start scan" + '\n')
        input_file.close()
        
    scanner = Scanner()#.withDelegate(ScanDelegate()) 
    devices = scanner.scan(interval) # 0 = loop
    
    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"end scan" + '\n')
        input_file.close()
        
###############################################################
##  rerank first
    if (rank != 0 ): # if not the server, rerank
        print "reranking..."
        rank = -1
        for dev in devices: 
            dict = {}
            for (adtype, desc, value) in dev.getScanData(): 
                dict[adtype] = value

            # handle the flag == 88
            if (dict.has_key(1) and dict[1] == '88'):
               
        
###############################################################
                # handle type = 0xc1
                if (dict.has_key(0xc1)):
                    data = dict[0xc1]
                    print "recv data [0xC1]: ", data
                    # parse cmd
                    cmd = data[0:2]
                    data = data[2:]
                    print "cmd: ", cmd, ":",data
###############################################################
                    if (cmd == '03'):
                        print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
                
                        for (adtype, desc, value) in dev.getScanData():
                            print "  %s = %s" % (desc, value)

                        for key in dict:        
                            print "  msg %d = %s" % (key, dict[key])
                            
                        handle_cmd_03(data)
                    
###############################################################
## other task:       
    for dev in devices: 
        dict = {}
        for (adtype, desc, value) in dev.getScanData(): 
            dict[adtype] = value

        # handle the flag == 88
        if (dict.has_key(1) and dict[1] == '88'):
            
###############################################################
            # handle type = 0xc1
            if (dict.has_key(0xc1)):
                data = dict[0xc1]
                print "recv data [0xC1]: ", data
                # parse cmd
                cmd = data[0:2]
                data = data[2:]
                print "cmd: ", cmd, ":",data
###############################################################
                # cmd 01: upload to server
                if (cmd == '01'):
                    print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
            
                    for (adtype, desc, value) in dev.getScanData():
                        print "  %s = %s" % (desc, value)

                    for key in dict:        
                        print "  msg %d = %s" % (key, dict[key])
                        
                    handle_cmd_01(data)
                # cmd 02: download to client
                if (cmd == '02'):
                    print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)
            
                    for (adtype, desc, value) in dev.getScanData():
                        print "  %s = %s" % (desc, value)

                    for key in dict:        
                        print "  msg %d = %s" % (key, dict[key])
                        
                    handle_cmd_02(data)

###############################################################
# cmd 01: 
def handle_cmd_01(data):
    global rank, PIID

    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"handle_cmd_01|"+ data + '\n')
        input_file.close()
    
###############################################################
    # server
    if (rank == 0):
        # handle the msg
        # type
        ty = data[0:2]
        data = data[2:]
###############################################################
        # type 01: request a PIID
        if (ty == '01'):

            with open("clog.txt","a") as input_file:
                input_file.write(str(datetime.datetime.now())+ "|"+"request a PIID"+'\n')
                input_file.close()
                
            print "request a PIID."
            fromID = data[0:4]
            print "Source ID: ", fromID
            
            theLastForwardedID = data[4:8]
            print "The last forward ID: ", theLastForwardedID
            
            theLastRank = data[8:10]
            print "the last rank: ", theLastRank

            nodeAddr = data[10:22]
            print "node address: ", nodeAddr

## need to handle the mac ID table here, TODO::
## now just simply way to do this            
            
            # assign a PIID
            PIID = PIID + 1
            if (PIID > 9999):
                PIID = 0

            with open("clog.txt","a") as input_file:
                input_file.write(str(datetime.datetime.now())+ "|"+"assign a PIID|" +(str)(PIID) +'\n')
                input_file.close()

            # ready to send it back
            data = ""

            # new id for client
            idd = "0000" + (str)(PIID)
            idd = idd[-4:]
            idd = idd[0] + idd[1] + " " + idd[2] + idd[3] + " "

            irank = "00 "
            if (rank != -1):
                irank = "00" + (str)(rank)
                irank = irank[-2:] + " "

            nodeAddr = nodeAddr[0:2] + " " + nodeAddr[2:4] + " " + nodeAddr[4:6] + " " + nodeAddr[6:8] + " " + nodeAddr[8:10] + " " + nodeAddr[10:12] + " "

            # make a data package
            # send to node
            # cmd = 02 01
            data = "C1 " + "02 " + "01 " + idd + idd + irank + nodeAddr
            tdata = data.replace(" ","")
            
            # len of the data
            data = (str)(len(tdata)/2) + " " + data

            # broadcast
            BroadCast(data, interval_for_assign_new_id)
            
###############################################################       
        # type 02: msg upload to server 
        if (ty == '02'):

            with open("clog.txt","a") as input_file:
                input_file.write(str(datetime.datetime.now())+ "|"+"msg upload to server" +'\n')
                input_file.close()
                
            fromID = data[0:4]
            print "Source ID: ", fromID
            
            theLastForwardedID = data[4:8]
            print "The last forward ID: ", theLastForwardedID
            
            theLastRank = data[8:10]
            print "The last rank: ", theLastRank

            temp = data[10:12]
            print "Temp: ", temp

            hum = data[12:14]
            print "Hum: ", hum

            smoke = data[14:16]
            print "Smoke: ", smoke

            power = data[16:18]
            print "Power consumption: ", power
            
###############################################################
    # client
    if (rank > 0):
        # forword this msg
        ty = data[0:2]
        data = data[2:]
        
        forwardData = "C1 01 " + ty + " " # up load to server

        # source ID
        forwardData = forwardData + data[0:2] +" " + data[2:4] + " "

        # the my ID
        # modify the data
        idd = "0000" + (str)(PIID)
        idd = idd[-4:]
        idd = idd[0] + idd[1] + " " + idd[2] + idd[3] + " "
        forwardData = forwardData + idd

        # its rank
        itsRank = (int)(data[8:10])
        if (rank >= itsRank):
            print "NOT forword this msg to server."
            with open("clog.txt","a") as input_file:
                input_file.write(str(datetime.datetime.now())+ "|"+"NOT forword this msg to server" +'\n')
                input_file.close()
            return

        #my rank
        irank = "00 "
        if (rank != -1):
            irank = "00" + (str)(rank)
            irank = irank[-2:] + " "
        forwardData = forwardData + irank
          
        for i in range(10, len(data), 2):
            forwardData = forwardData + data[i] + data[i+1] + " "

        tdata = forwardData.replace(" ","")
            
        # len of the data
        forwardData = (str)(len(tdata)/2) + " " + forwardData

        print "forword this msg to server."
        with open("clog.txt","a") as input_file:
            input_file.write(str(datetime.datetime.now())+ "|"+"forword this msg to server" +'\n')
            input_file.close()
        
        # broadcast
        BroadCast(forwardData, 0)
                
        pass


###############################################################
# cmd 02: 
def handle_cmd_02(data):
    global rank, macAddr, PIID

    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"handle_cmd_02|"+ data + '\n')
        input_file.close()
    
    
###############################################################
    # server
    if (rank == 0):
        print "I am server."
        pass
        
###############################################################
    # client
    if (rank != 0):
        # handle the msg
        # type
        ty = data[0:2]
        data = data[2:]
        # if this msg is for me
###############################################################
        # assign a PIID
        if (ty == '01'):
                
            newID = data[0:4]
            print "New ID: ", newID
            
            theLastForwardedID = data[4:8]
            print "The last forward ID: ", theLastForwardedID
            
            theLastRank = data[8:10]
            print "The last rank: ", theLastRank

            nodeAddr = data[10:22]
            print "Rev Addr: ", nodeAddr.upper().strip()
            print "My  Addr: ", macAddr.replace(":","").upper().strip()
        
            # get a new PIID
            if (nodeAddr.upper().strip() == macAddr.replace(":","").upper().strip()):
                PIID = (int)(newID)
                print "Assigned a new PIID: ", PIID
                
                with open("clog.txt","a") as input_file:
                    input_file.write(str(datetime.datetime.now())+ "|"+"newID|" +(str)(PIID) +'\n')
                    input_file.close()
            else:
                # downforward this msg

                downwardData = "C1 02 01 "
                #new ID
                downwardData = downwardData + data[0:2] + " " + data[2:4] + " "

                # the my ID
                # modify the data
                idd = "0000" + (str)(PIID)
                idd = idd[-4:]
                idd = idd[0] + idd[1] + " " + idd[2] + idd[3] + " "
                downwardData = downwardData + idd
                
                # its rank
                itsRank = (int)(data[8:10])
                if (rank <= itsRank):
                    print "NOT downwardData this msg."
                    with open("clog.txt","a") as input_file:
                        input_file.write(str(datetime.datetime.now())+ "|"+"NOT downwardData this msg" +'\n')
                        input_file.close()
                    return

                #my rank
                irank = "00 "
                if (rank != -1):
                    irank = "00" + (str)(rank)
                    irank = irank[-2:] + " "
                downwardData = downwardData + irank

                for i in range(10, len(data), 2):
                    downwardData = downwardData + data[i] + data[i+1] + " "

                tdata = downwardData.replace(" ","")
            
                # len of the data
                downwardData = (str)(len(tdata)/2) + " " + downwardData
                
                print "Downward this msg to node."
                
                with open("clog.txt","a") as input_file:
                    input_file.write(str(datetime.datetime.now())+ "|"+"downwardData this msg"+'\n')
                    input_file.close()

                # broadcast
                BroadCast(downwardData, 0)
                
                pass
               
###############################################################
# cmd 03: only broadcast msg
def handle_cmd_03(data):
    global rank

    with open("clog.txt","a") as input_file:
        input_file.write(str(datetime.datetime.now())+ "|"+"handle_cmd_03|"+ data + '\n')
        input_file.close()
    
    if (rank == 0):
        print "I am server."
        return
    
    # type
    ty = data[0:2]
    data = data[2:4]
    # server broadcast it's rank
    if (ty == '01'):
        print "incoming rank:", data
        ser_rank = (int)(data)
        if ((rank == -1 or ser_rank <rank -1) and ser_rank >=0):
            rank = ser_rank + 1
        print "my rank: ", rank

        with open("clog.txt","a") as input_file:
            input_file.write(str(datetime.datetime.now())+ "|"+"my rank|" + (str)(rank)+'\n')
            input_file.close()




###############################################################


if __name__ == '__main__':
# read the rank from file
    with open("rank.txt","r") as input_file:
        rank = (int)(input_file.readline())
        input_file.close()
    print "rank: ",rank

# read the mac address from file
    with open("macAddr.txt","r") as input_file:
        macAddr = input_file.readline()
        input_file.close()
    print "Mac Address: ",macAddr

# start log
with open("clog.txt","a") as input_file:
    input_file.write("##############################################\n")
    input_file.write("Start Time|"+str(datetime.datetime.now())+'\n')
    input_file.close()

## use try catch {} to handle the while True.
    while True:
        try:
            # client
            if (rank != 0):
                # scan network
                ScanNetwork()
                # broadcast for a while
                # upload data to server
                if (PIID == 0):
                    # request a PIID
                    Broadcast_Client_01_01()
               
                if (rank > 0 and PIID > 0):
                    # broadcast for a while
                    Broadcast_Server_03_01()
                    # upload data to server
                    Broadcast_Client_01_02()
                    
            # server
            if (rank == 0):
                # scan network
                ScanNetwork()
                # broadcast for a while
                Broadcast_Server_03_01()
        except:
            print 'error and rerun again.'
            pass
        

