import math
from modules import MathLib as ml

class State():
    """ The car's state variables """
    def __init__(self, Px, Py, V, heading):
        self.setFromVector( [Px,Py,V,heading] )

    def getVector(self):
        """ Returns a tuple of state variables (Px, Py, V, heading) """ 
        return (self.Px, self.Py, self.V, self.heading)

    def setFromVector(self, V):
        """ Store state variables as class members from list (Px, Py, V, heading) """
        self.Px = V[0]
        self.Py = V[1]
        self.V  = V[2]       #< Car's velocity (pix/s)
        self.heading = V[3]  #< Car heading (rad)
        
class Input():
    """ The car's input variables """
    def __init__(self, acc, steering):
        self.setFromVector( [acc,steering] )

    def getVector(self):
        """ Returns a tuple of input variables (0, 0, acc, steering) """ 
        return (0,0,self.acc, self.steering)

    def setFromVector(self, V):
        """ Store input variables as class members from list (acc, steering) """
        self.acc  = V[0]       #< Car's velocity (pix/s)
        self.steering = V[1]   #< Car's steering angle (rad)

class Car():
    def __init__(self, dt=0.05, port=None, position=[0,0], velocity=0, heading=0, Cd=0.05):
        self.state = State(position[0], position[1], velocity, heading) #< Car's state
        self.input = Input(acc=0, steering=0)                           #< Car's input
        self.Cd = Cd
        self.dt = dt
        self.Min = -0.5       #< Max steering angle (rad)
        self.Max = +0.5       #< Max steering angle (rad)
    
    def _start(self):
        raise Exception("this function does not exist in the simulator version of the car module")

    def addAcc(self, dAcc):
        """Add dAcc to the current accelaration input value (pix/s^2)"""
        self.input.acc += dAcc

    def setAcc(self, acc):
        """Set the accelaration input variable (pix/s^2)"""
        self.input.acc = acc

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

    def getPosition(self):
        """Returns the car's position (Px, Py)"""
        return (self.state.Px, self.state.Py)
    
    def getHeading(self, units='r'):
        """Returns the car's heading in rad or degrees"""
        heading = self.state.heading
        if units[0] == 'd':
            return ml.radToDeg(heading)
        return heading

    def update(self):
        """Calculate the next state value (X[n+1] = A[n]*x[n] +B[n]*u[n]"""
        self.A = self._calcStateTransitionMatrix()
        self.B = self._calcInputMatrix()
        Ax = ml.MxV(self.A, self.state.getVector())
        Bu = ml.MxV(self.B, self.input.getVector())
        self.state.setFromVector(ml.addV(Ax, Bu))
        self.state.heading = ml.modulu(self.state.heading, 2*math.pi)
        #print("Heading: %1.2f (rad)"%(self.state.heading))

    def _calcStateTransitionMatrix(self):
        """Returns the updated state transition matrix (A) of the model"""
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
        """Returns the updated input matrix (B) of the model"""
        dt = self.dt
        heading = self.state.heading
        V = self.state.V
        B = [0]*4
        B[0] = [0, 0, 0.5*(dt**2), 0]
        B[1] = [0, 0, 0.5*math.sin(heading)*(dt**2), 0]
        B[2] = [0, 0, dt, 0]
        B[3] = [0, 0, 0, V*dt]
        return B
