#!/usr/bin/env python
"""
Script to build an ArduBridge environment
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section

By: Guy Soffer
Date: 05/July/2021
"""

#Basic modules to load
import time
from GSOF_ArduBridge import ArduBridge
from Modules import mDev_ArduBridge as mDev
#from TestScripts import testScripts

def close():
    ardu.OpenClosePort(0)
    print('COM port is closed')

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/
    port = 'COM9' #19      #<--Change to the correct COM-Port to access the Arduino
    baudRate = 115200*2  #<--Leave as is
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\
    
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    
    # ArduCar shield over I2C:
    car = mDev.mDEV(addr=0x18, i2c=ardu.i2c)
#    test = testScripts.test(disp=disp)

    print('Discovering ArduBridge on port %s'%(port))
    if ardu.OpenClosePort(1):
        print('ArduBridge is ON-LINE.')
    else:
        print('ArduBridge is not responding.')
        
#    test.printHelp()
#    test.config()
