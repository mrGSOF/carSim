#-*- coding: utf-8 -*-
########################################################################
# Filename    : mDev.py
# Description : This is the Class mDev. Used for Control the Shield.
# auther      : www.freenove.com
# modification: 2020/03/26
########################################################################
import time, threading

def numMap(value,fromLow,fromHigh,toLow,toHigh):
    return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

def clamp(val, Min, Max):
    if val < Min:
        return Min
    elif val > Max:
        return Max
    return val

class mDEV:
    CMD_SERVO1      =   0
    CMD_SERVO2      =   1
    CMD_SERVO3      =   2
    CMD_SERVO4      =   3
    CMD_PWM1        =   4
    CMD_PWM2        =   5
    CMD_DIR1        =   6
    CMD_DIR2        =   7
    CMD_BUZZER      =   8
    CMD_IO1         =   9
    CMD_IO2         =   10
    CMD_IO3         =   11
    CMD_SONIC       =   12
    SERVO_MAX_PULSE_WIDTH = 2500
    SERVO_MIN_PULSE_WIDTH = 500
    SONIC_MAX_HIGH_BYTE = 50
    Is_IO1_State_True = False
    Is_IO2_State_True = False
    Is_IO3_State_True = False
    Is_Buzzer_State_True = False
    handle = True
    mutex = threading.Lock()
    def __init__(self, addr=0x18, i2c=None):
        self.address = addr #default address of mDEV
        self.bus=i2c

    def i2cRead(self,reg):
        return self.bus.readRegister(dev=self.address, reg=reg, N=1)
        #self.bus.read_byte_data(self.address,reg)
        
    def i2cWrite1(self,cmd,value):
        self.bus.writeRegister(dev=self.address, reg=cmd, vByte=[value])
        #self.bus.write_byte_data(self.address,cmd,value)
        
    def i2cWrite2(self,value):
        self.bus.writeRegister(dev=self.address, reg=value, vByte=[])
        #self.bus.write_byte(self.address,value)
    
    def writeReg(self,cmd,value):
        value = int(value)
        #print(value,type(value))
        for i in range(0,3):
            self.bus.writeRegister(dev=self.address, reg=cmd, vByte=[value>>8,value&0xff])
            #time.sleep(0.05)
        
    def readReg(self,cmd):      
        ##################################################################################################
        #Due to the update of SMBus, the communication between Pi and the shield board is not normal. 
        #through the following code to improve the success rate of communication.
        #But if there are conditions, the best solution is to update the firmware of the shield board.
        ##################################################################################################
        for i in range(0,10,1):
            #self.bus.write_i2c_block_data(self.address,cmd,[0])
            self.i2cWrite1(cmd, 0)

            #a = self.bus.read_i2c_block_data(self.address,cmd,1)
            a = self.i2cRead(cmd)
            
            #self.bus.write_byte(self.address,cmd+1)
            self.i2cWrite2(cmd+1)

            #b = self.bus.read_i2c_block_data(self.address,cmd+1,1)
            b = self.i2cRead(cmd+1)
            
            #self.bus.write_byte(self.address,cmd)
            self.i2cWrite2(cmd)
            
            #c = self.bus.read_byte_data(self.address,cmd)
            c = self.i2cRead(cmd)
            
            #self.bus.write_byte(self.address,cmd+1)
            self.i2cWrite2(cmd+1)

            #d = self.bus.read_byte_data(self.address,cmd+1)
            d = self.i2cRead(cmd+1)

            #print i,a,b,c,d
            #'''
            if(a[0] == c and c < self.SONIC_MAX_HIGH_BYTE ): #and b[0] == d
                return c<<8 | d
            else:
                continue
            #'''
            '''
            if (a[0] == c and c < self.SONIC_MAX_HIGH_BYTE) :
                return c<<8 | d
            elif (a[0] > c and c < self.SONIC_MAX_HIGH_BYTE) :
                return c<<8 | d
            elif (a[0] < c and a[0] < self.SONIC_MAX_HIGH_BYTE) :
                return a[0]<<8 | b[0]
            else :
                continue
            '''
        return 0
        #################################################################################################
        #################################Old codes#######################################################
        #[a,b]=self.bus.read_i2c_block_data(self.address,cmd,2)
        #print "a,b",[a,b]
        #return a<<8 | b
        #################################################################################################
    def move(self, left_pwm, right_pwm, steering_angle=90):
        self.setServo(index='1', angle=steering_angle)
        self.setMotor(ch='1', p=clamp(right_pwm, -1000, 1000))
        self.setMotor(ch='2', p=clamp(left_pwm, -1000, 1000))

    def setMotor(self, ch, p):
        Mtr_dir = 1
        if p < 0:
            Mtr_dir = 0
            p = abs(p)
            
        if (ch == '1') or (ch == 1):
            self.writeReg(self.CMD_DIR1, Mtr_dir)
            self.writeReg(self.CMD_PWM1, p)
        elif (ch == '2') or (ch == 2):
            self.writeReg(self.CMD_DIR2, Mtr_dir)
            self.writeReg(self.CMD_PWM2, p)
        else:
            print("Error in PWM channel")

    def setServo(self, index, angle):
        angle=numMap( abs(angle),0,180,500,2500)
        if (index == '1') or (index == 1):
            self.writeReg(self.CMD_SERVO1, angle)
        elif (index == '2') or (index == 2):
            self.writeReg(self.CMD_SERVO2, angle)
        elif (index == '3') or (index == 3):
            self.writeReg(self.CMD_SERVO3, angle)
        elif (index == '4') or (index == 4):
            self.writeReg(self.CMD_SERVO4, angle)
    
    def setLed(self, R, G, B):
        self.writeReg(self.CMD_IO1, clamp(R, 0,1))
        self.writeReg(self.CMD_IO2, clamp(G, 0,1))
        self.writeReg(self.CMD_IO3, clamp(B, 0,1))
            
    def setBuzzer(self, PWM):
        self.writeReg(self.CMD_BUZZER, PWM)
        
    def getSonicEchoTime():
        SonicEchoTime = self.readReg(self.CMD_SONIC)
        return SonicEchoTime
        
    def getSonic(self):
        SonicEchoTime = self.readReg(self.CMD_SONIC)
        distance = SonicEchoTime * 17.0 / 1000.0
        return distance
    
    def setShieldI2cAddress(self,addr): #addr: 7bit I2C Device Address 
        if (addr<0x03) or (addr > 0x77) :
            return 
        else :
            self.writeReg(0xaa,(0xbb<<8)|(addr<<1))

##mdev = mDEV()   
##def loop(): 
##    mdev.readReg(mdev.CMD_SONIC)
##    while True:
##        SonicEchoTime = mdev.readReg(mdev.CMD_SONIC)
##        distance = SonicEchoTime * 17.0 / 1000.0
##        print("EchoTime: %d, Sonic: %.2f cm"%(SonicEchoTime,distance))
##        time.sleep(0.001)
##    
##if __name__ == '__main__':
##    import sys
##    print("mDev.py is starting ... ")
##    #setup()
##    try:
##        if len(sys.argv)<2:
##            print("Parameter error: Please assign the device")
##            exit() 
##        print(sys.argv[0],sys.argv[1])
##        if sys.argv[1] == "servo":      
##            cnt = 3 
##            while (cnt != 0):       
##                cnt = cnt - 1
##                for i in range(50,140,1):   
##                    mdev.writeReg(mdev.CMD_SERVO1,numMap(i,0,180,500,2500))
##                    time.sleep(0.005)
##                for i in range(140,50,-1):  
##                    mdev.writeReg(mdev.CMD_SERVO1,numMap(i,0,180,500,2500))
##                    time.sleep(0.005)
##            mdev.writeReg(mdev.CMD_SERVO1,numMap(90,0,180,500,2500))
##        if sys.argv[1] == "buzzer":
##            mdev.writeReg(mdev.CMD_BUZZER,2000)
##            time.sleep(3)
##            mdev.writeReg(mdev.CMD_BUZZER,0)
##        if sys.argv[1] == "RGBLED":
##            for i in range(0,3):
##                mdev.writeReg(mdev.CMD_IO1,0)
##                mdev.writeReg(mdev.CMD_IO2,1)
##                mdev.writeReg(mdev.CMD_IO3,1)
##                time.sleep(1)
##                mdev.writeReg(mdev.CMD_IO1,1)
##                mdev.writeReg(mdev.CMD_IO2,0)
##                mdev.writeReg(mdev.CMD_IO3,1)
##                time.sleep(1)
##                mdev.writeReg(mdev.CMD_IO1,1)
##                mdev.writeReg(mdev.CMD_IO2,1)
##                mdev.writeReg(mdev.CMD_IO3,0)
##                time.sleep(1)
##            mdev.writeReg(mdev.CMD_IO1,1)
##            mdev.writeReg(mdev.CMD_IO2,1)
##            mdev.writeReg(mdev.CMD_IO3,1)
##        if sys.argv[1] == "ultrasonic" or sys.argv[1] == "s":
##            while True:
##                print("Sonic: ",mdev.getSonic())
##                time.sleep(0.1)
##        if sys.argv[1] == "motor":
##                mdev.writeReg(mdev.CMD_DIR1,0)
##                mdev.writeReg(mdev.CMD_DIR2,0)
##                for i in range(0,1000,10):  
##                    mdev.writeReg(mdev.CMD_PWM1,i)
##                    mdev.writeReg(mdev.CMD_PWM2,i)
##                    time.sleep(0.005)
##                time.sleep(1)
##                for i in range(1000,0,-10): 
##                    mdev.writeReg(mdev.CMD_PWM1,i)
##                    mdev.writeReg(mdev.CMD_PWM2,i)
##                    time.sleep(0.005)
##                mdev.writeReg(mdev.CMD_DIR1,1)
##                mdev.writeReg(mdev.CMD_DIR2,1)
##                for i in range(0,1000,10):  
##                    mdev.writeReg(mdev.CMD_PWM1,i)
##                    mdev.writeReg(mdev.CMD_PWM2,i)
##                    time.sleep(0.005)
##                time.sleep(1)
##                for i in range(1000,0,-10): 
##                    mdev.writeReg(mdev.CMD_PWM1,i)
##                    mdev.writeReg(mdev.CMD_PWM2,i)
##                    time.sleep(0.005)
##    except KeyboardInterrupt:
##        pass    
