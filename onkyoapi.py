import sys
import time
import logging
import requests
import socket
import binascii

class OnkyoReceiver(object):
    strZonesMute = ["AMT", "ZMT", "MT3"]
    strZonesLevel = ["MVL", "ZVL", "VL3"]
    strZonesPower = ["PWR", "ZPW", "PW3"]

    def __init__(self, ipaddress, port):
        self._ipaddress = ipaddress
        self._port = port

    def SendData(self, strData, breturndata = False):
        data = self.ConvertToTCPBytes(strData)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self._ipaddress, self._port))
        s.send(data)
        returndata = ""
        if breturndata == True:
            returndata = s.recv(40)
            #print(returndata)
        s.close()
        return returndata

    def CreateAndSend(self, prefixstring, zoneId, command, breturndata = False):
        zoneId = zoneId - 1
        strData = prefixstring[zoneId] + command
        return self.SendData(strData, breturndata)

    def ConvertToTCPBytes(self, strData):
        initData = bytearray([73, 83, 67, 80, 0, 0, 0, 16, 0, 0, 0, 8, 1, 0, 0, 0, 33, 49])
        strData = strData + '\r'
        tempdata = strData.encode('ascii')
        data = initData + tempdata
        data[11] = (len(strData)) + 2
        #print(data)
        return data

    
    def Mute(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesMute, zoneId, "01")
        
    def UnMute(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesMute, zoneId, "00")

    def Up(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesLevel, zoneId, "UP")

    def Down(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesLevel, zoneId, "DOWN")
    
    def Set(self, zoneId, volume):
        strVolume = "%02X" % volume
        self.CreateAndSend(OnkyoReceiver.strZonesLevel, zoneId, strVolume)

    def Get(self, zoneId):
        returndata = self.CreateAndSend(OnkyoReceiver.strZonesLevel, zoneId, "QSTN", True)
        temp = returndata[21:23]
        strtemp = temp.decode("utf-8")
        x = int(strtemp, 16)
        print(x)
        return x

    def On(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesPower, zoneId, "01")

    def Off(self, zoneId):
        self.CreateAndSend(OnkyoReceiver.strZonesPower, zoneId, "00")


