from bluepy.btle import Scanner, DefaultDelegate
import subprocess


from bluepy.btle import Scanner, DefaultDelegate
class ScanDelegate(DefaultDelegate): 
    def __init__(self): 
        DefaultDelegate.__init__(self)
    def handleDiscovery(self, dev, isNewDev, isNewData): 
        if isNewDev: 
            print "Discovered device", dev.addr 
        elif isNewData: 
            print "Received new data from", dev.addr

while True:
    
    scanner = Scanner()#.withDelegate(ScanDelegate()) 
    devices = scanner.scan(5.0) # 0 = loop


    for dev in devices: 
        dict = {}
        for (adtype, desc, value) in dev.getScanData(): 
            #print "  %s = %s" % (desc, value)
            dict[adtype] = value

        if (dict.has_key(1) and dict[1] == '88'):

            print "Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi)

            for (adtype, desc, value) in dev.getScanData():
                print "  %s = %s" % (desc, value)

            for key in dict:        
                print "  msg %d = %s" % (key, dict[key])
        
        
    

        
