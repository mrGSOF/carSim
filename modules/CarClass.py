import math
from modules import MathLib as ml

class State():
    """ The car's state variables """
    def __init__(self, Px, Py, V, heading):
        self.setFromVector( [Px,Py,V,heading] )

    def getVector(self):
        return (self.Px, self.Py, self.V, self.heading)

    def setFromVector(self, V):
        self.Px = V[0]
        self.Py = V[1]
        self.V  = V[2]       #< Car's velocity (pix/s)
        self.heading = V[3]  #< Car heading (rad)
        
class Input():
    """ The car's input variables """
    def __init__(self, acc, steering):
        self.setFromVector( [acc,steering] )

    def getVector(self):
        return (0,0,self.acc, self.steering)

    def setFromVector(self, V):
        self.acc  = V[0]       #< Car's velocity (pix/s)
        self.steering = V[1]   #< Car's steering angle (rad)

class Car():
    def __init__(self, dt, position=[0,0], velocity=0, heading=0, Cd=0.05):
        self.state = State(position[0], position[1], velocity, heading) #< Car's state
        self.input = Input(acc=0, steering=0)                           #< Car's input
        self.Cd = Cd
        self.dt = dt
        self.pos = (0, 0)
        self.Min = -0.5       #< Max steering angle (rad)
        self.Max = +0.5       #< Max steering angle (rad)

    def addAcc(self, dAcc):
        self.input.acc += dAcc

    def setAcc(self, acc):
        self.input.acc = acc

    def setVel(self, V):
        self.state.V = V
        self.setAcc(0)

    def setSteering(self, rad):
        self.input.steering = ml.clip(rad, self.Min, self.Max)
        
    def addSteering(self, dRad):
        steering = self.input.steering +dRad
        self.input.steering = ml.clip(steering, self.Min, self.Max)

    def update(self):
        self.A = self._calcStateTransitionMatrix()
        self.B = self._calcInputMatrix()
        Ax = ml.MxV(self.A, self.state.getVector())
        Bu = ml.MxV(self.B, self.input.getVector())
        self.state.setFromVector(ml.addV(Ax, Bu))
        
        while self.state.heading > 2*math.pi:
            self.state.heading -= 2*math.pi
        while self.state.heading < -2*math.pi:
            self.state.heading += 2*math.pi
            
        self.pos = (self.state.Px, self.state.Py)
        #print("Heading: %1.2f (rad)"%(self.state.heading))

    def _calcStateTransitionMatrix(self):
        dt = self.dt
        heading = self.state.heading
        Cd = self.Cd
        A = [0]*4
        A[0] = [1, 0, math.cos(heading)*dt, 0]
        A[1] = [0, 1, math.sin(heading)*dt, 0]
        A[2] = [0, 0, (1 -Cd), 0]
        A[3] = [0, 0, 0, 1]
        return A

    def _calcInputMatrix(self):
        dt = self.dt
        heading = self.state.heading
        V = self.state.V
        B = [0]*4
        B[0] = [0, 0, 0.5*(dt**2), 0]
        B[1] = [0, 0, 0.5*math.sin(heading)*(dt**2), 0]
        B[2] = [0, 0, dt, 0]
        B[3] = [0, 0, 0, V*dt]
        return B
