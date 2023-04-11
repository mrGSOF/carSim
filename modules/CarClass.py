import math
from modules import MathLib as ml

class State():
    """ The car's state variables """
    def __init__(self, Px, Py, V, F, heading):
        self.setFromVector( [Px,Py,V,F,heading] )

    def getVector(self):
        """ Returns a tuple of state variables (Px, Py, V, F, heading) """ 
        return (self.Px, self.Py, self.V, self.F, self.heading)

    def setFromVector(self, V):
        """ Store state variables as class members from list (Px, Py, V, heading) """
        self.Px =      V[0]
        self.Py =      V[1]
        self.V  =      V[2]  #< Car's velocity (pix/s)
        self.F =       V[3]  #< Car accelaration (pix/s^2)
        self.heading = V[4]  #< Car heading (rad)
        
class Input():
    """ The car's input variables """
    def __init__(self, F, steering):
        self.setFromVector( [F,steering] )

    def getVector(self):
        """ Returns a tuple of input variables (0, 0, 0, F, steering) """ 
        return (0,0,0, self.F, self.steering)

    def setFromVector(self, V):
        """ Store input variables as class members from list (F, steering) """
        self.F  = V[0]       #< Car's velocity (pix/s)
        self.steering = V[1] #< Car's steering angle (rad)

class Car():
    def __init__(self, dt=0.05, port=None, position=[0,0], velocity=0, F=0, heading=0, Cd=0.02):
        self.state = State(position[0], position[1], velocity, F, heading) #< Car's state
        self.input = Input(F=0, steering=0)                           #< Car's input
        self.Cd = Cd
        self.dt = dt
        self.Min = -0.5       #< Max steering angle (rad)
        self.Max = +0.5       #< Max steering angle (rad)
        self.collideTimeout = 0
    
    def _start(self):
        raise Exception("this function does not exist in the simulator version of the car module")

    def addAcc(self, dAcc):
        """Add dAcc to the current accelaration input value (pix/s^2)"""
        self.input.F += dAcc

    def setAcc(self, acc):
        """Set the accelaration input variable (pix/s^2)"""
        self.input.F = acc

    def setVel(self, V):
        """Set the velovity state variable to V and zero the acc input (pix/sec)"""
        self.state.V = V
        self.setAcc(0)

    def setSteering(self, rad):
        """Set the steering angle of the input variable (rad)"""
        self.input.steering = ml.clip(rad, self.Min, self.Max)
        
    def addSteering(self, dRad):
        """Add dRad to the current steering input value (rad)"""
        steering = self.input.steering +dRad
        self.input.steering = ml.clip(steering, self.Min, self.Max)

    def getSteering(self, units='r'):
        """Returns the car's steeringng angle in rad or degrees"""
        steering = self.input.steering #self.state.steering
        if units[0] == 'd':
            return ml.radToDeg(steering)
        return steering

    def getPosition(self):
        """Returns the car's position (Px, Py)"""
        return (self.state.Px, self.state.Py)
    
    def getVel(self):
        """Returns the car's velocity (pix/s)"""
        return self.state.V

    def getAcc(self):
        """Returns the car's accelarometer (pix/s^2)"""
        return self.input.F

    def getHeading(self, units='r'):
        """Returns the car's heading in rad or degrees"""
        heading = self.state.heading
        if units[0] == 'd':
            return ml.radToDeg(heading)
        return heading

    def getDirection(self) -> int:
        V = self.getVel()
        if V == 0:
            Direction = 1
        else:
            Direction = V/abs(V)
        return Direction
        
    def collide(self, vector=None):
        if (vector == None) and (self.collideTimeout == 0):
            V = self.getVel()
            Dir = self.getDirection()
            F = 0.8*V
            V0 = 5*Dir
            self.state.V = -(V0 +F)
            #self.setVel(-V0 -F)
            #self.setAcc(0)
            self.collideTimeout = 5

    def update(self):
        """Calculate the next state value (X[n+1] = A[n]*x[n] +B[n]*u[n]"""
        self.A = self._calcStateTransitionMatrix()
        self.B = self._calcInputMatrix()
        Ax = ml.MxV(self.A, self.state.getVector())
        Bu = ml.MxV(self.B, self.input.getVector())
        self.state.setFromVector(ml.addV(Ax, Bu))
        self.state.heading = ml.modulu(self.state.heading, 2*math.pi)
        if self.collideTimeout > 0:
            self.collideTimeout -= 1
        #print("Heading: %1.2f (rad)"%(self.state.heading))

    def _calcStateTransitionMatrix(self):
        """Returns the updated state transition matrix (A) of the model"""
        dt = self.dt
        heading = self.state.heading
        Cd = self.Cd #*self.getDirection()
        V = abs(self.getVel())
        A = [0]*5
        cos_heading = math.cos(heading)
        sin_heading = math.sin(heading)
        dtt = dt**2
        A[0] = [1, 0, cos_heading*dt, 0.5*cos_heading*dtt, 0]
        A[1] = [0, 1, sin_heading*dt, 0.5*sin_heading*dtt, 0]
        A[2] = [0, 0,     1,    dt, 0]
        A[3] = [0, 0, -0.5*Cd*V, 0, 0]
        A[4] = [0, 0,     0,     0, 1]
        return A

    def _calcInputMatrix(self):
        """Returns the updated input matrix (B) of the model"""
        dt = self.dt
        heading = self.state.heading
        V = self.state.V
        B = [0]*5
        B[0] = [0, 0, 0, 0,  0  ]
        B[1] = [0, 0, 0, 0,  0  ]
        B[2] = [0, 0, 0, 0,  0  ]
        B[3] = [0, 0, 0, 1,  0  ]
        B[4] = [0, 0, 0, 0, V*dt]
        return B
