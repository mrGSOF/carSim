import math
from GSOF_ArduBridge import ArduBridge
from modules.Freenove_ThreeWheeledSmartCarKit_for_ArduBridge.Python.Modules import mDev_ArduBridge as mDev
from modules import MathLib as ml

class State():
    """ The car's state variables """
    def __init__(self, Px, Py, V, heading):
        self.setFromVector([Px,Py,V,heading])

    def getVector(self):
        return(self.Px, self.Py, self.V, self.heading)

    def setFromVector(self, V):
        self.Px = V[0]
        self.Py = V[1]
        self.V  = V[2]       #< Car's velocity (pix/s)
        self.heading = V[3]  #< Car heading (driving wheel pos(in rad))
        
class Input():
    """ The car's input variables """
    def __init__(self, acc, steering):
        self.setFromVector([acc,steering])

    def getVector(self):
        return (0,0,self.acc, self.steering)

    def setFromVector(self, V):
        self.acc  = V[0]       #< Car's velocity (pix/s)
        self.steering = V[1]   #< Car's steering angle (rad)

class Car():
    def __init__(self, dt=0.05, port = "COM9", position=[0,0], velocity=0, heading=0, Cd=0.05):
        self.state = State(position[0], position[1], velocity, heading) #< Car's state
        self.input = Input(acc=0, steering=0)                           #< Car's input
        
        self.dt = dt          #< not used
        self.Cd = Cd          #< not used
        self.pos = (0,0)      #< not used

        self.Min = -1.22      #< Max steering angle (rad)
        self.Max = +1.22      #< Max steering angle (rad)
        
        self.port = port
        self._start()

    def _start(self):
        baudRate = 115200*2
        
        print('Using port %s at %d'%(self.port, baudRate))
        ardu = ArduBridge.ArduBridge( COM=self.port, baud=baudRate )
        
        self.car = mDev.mDEV(addr=0x18, i2c=ardu.i2c)

        print('Discovering ArduBridge on port %s'%(self.port))
        if ardu.OpenClosePort(1):
            print('ArduBridge is ON-LINE.')
        else:
            print('ArduBridge is not responding.')

    def addAcc(self, dAcc):
        self.input.acc += dAcc

    def setAcc(self, acc):
        self.input.acc = acc

    def setVel(self, V):
        raise Exception("you cannot set the velocity in the pysical version of the car module")

    def setSteering(self, rad):
        self.input.steering = ml.clip(rad, self.Min, self.Max)
        
    def addSteering(self, dRad):
        steering = self.input.steering +dRad
        self.input.steering = ml.clip(steering, self.Min, self.Max)

    def update(self):
        print(math.degrees(self.input.steering+self.Max))
        self.car.move(self.input.acc, self.input.acc, math.degrees(self.input.steering+self.Max))
        # self.A = self._calcStateTransitionMatrix()
        # self.B = self._calcInputMatrix()
        # Ax = ml.MxV(self.A, self.state.getVector())
        # Bu = ml.MxV(self.B, self.input.getVector())
        # self.state.setFromVector(ml.addV(Ax, Bu))
        
        # while self.state.heading > 2*math.pi:
        #     self.state.heading -= 2*math.pi
        # while self.state.heading < -2*math.pi:
        #     self.state.heading += 2*math.pi
            
        # self.pos = (self.state.Px, self.state.Py)
    
    def _calcStateTransitionMatrix(self):
        raise Exception("this function does not exist in the pysical version of the car module")

    def _calcInputMatrix(self):
        raise Exception("this function does not exist in the pysical version of the car module")
