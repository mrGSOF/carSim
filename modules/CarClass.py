import math
#from modules import MathLib as ml
import importlib.util, os, sys
mdl = ""
path = os.path.join(os.path.dirname(__spec__.origin), "", "MathLib.py" )
print(path)
spec = importlib.util.spec_from_file_location(mdl, path)
print(spec)
ml = importlib.util.module_from_spec(spec)
sys.modules[mdl] = ml
spec.loader.exec_module(ml)

g = 9.81
class State():
    """ The car's state variables """
    def __init__(self, Px, Py, V, A, heading, mass):
        self.setFromVector( [Px,Py,V,A,heading,mass] )

    def getVector(self):
        """ Returns a tuple of state variables (Px, Py, V, A, heading, N) """ 
        return (self.Px, self.Py, self.V, self.A, self.heading, self.mass)

    def setFromVector(self, V):
        """ Store state variables as class members from list (Px, Py, V, A, heading, N) """
        self.Px =      V[0]
        self.Py =      V[1]
        self.V  =      V[2]  #< Car's velocity (pix/s)
        self.A =       V[3]  #< Car accelaration (pix/s^2)
        self.heading = V[4]  #< Car heading (rad)
        self.mass    = V[5]  #< Car's normal force (kgf)
        
class Input():
    """ The car's input variables """
    def __init__(self, F, steering, deltaMass=0):
        self.setFromVector( [F,steering,deltaMass] )

    def getVector(self):
        """ Returns a tuple of input variables (0, 0, 0, F, steering) """ 
        return (0,0,0, self.F, self.steering, self.deltaMass)

    def setFromVector(self, V):
        """ Store input variables as class members from list (F, steering) """
        self.F  = V[0]       #< Car's velocity (pix/s)
        self.steering = V[1] #< Car's steering angle (rad)
        if len(V) > 2:
            self.deltaMass = V[2]
            #print(self.deltaMass)

class Car():
    def __init__(self, dt=0.05, port=None, position=[0,0], velocity=0, F=0, heading=0, mass=0.1, wheelRadius=0.1, rollResCoef=0.005, Cd=0.01):
        self.state = State(Px=position[0], Py=position[1],     #< Car's state
                           V=velocity, A=0, heading=heading,
                           mass=mass
                           )
        self.input = Input(F=0, steering=0, deltaMass=0 )      #< Car's input
        self.Cd = Cd                                           #< Coef' of air drag
        self.rollResCoef = rollResCoef
        self.wheelRadius = wheelRadius
        self.mass = mass
        self.surfArea = 0.05
        self.dt = dt
        self.Min = -0.5        #< Max steering angle (rad)
        self.Max = +0.5        #< Max steering angle (rad)
        self.MaxF = 10.0       #< Max propulsion force
        self.collideTimeout = 0
    
    def _start(self):
        raise Exception("this function does not exist in the simulator version of the car module")

    def addPower(self, dPwr):
        """Add dAcc to the current accelaration input value (pix/s^2)"""
        self.input.F += dPwr
        if self.input.F > self.MaxF:
            self.input.F = self.MaxF

    def setPower(self, pwr):
        """Set the accelaration input variable (pix/s^2)"""
        self.input.F = pwr
        if self.input.F < -self.MaxF:
            self.input.F = -self.MaxF

    def setVel(self, V):
        """Set the velovity state variable to V and zero the acc input (pix/sec)"""
        self.state.V = V
        self.setPower(0)

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

    def getPower(self):
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
            A = 0.8*V
            V0 = 5*Dir
            self.state.V = -(V0 +A)
            #self.setVel(-V0 -A)
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
        #print("V: %1.2f, A: %1.2f, P: %1.2f"%(self.state.V, self.state.A, self.input.F))

    def _calcStateTransitionMatrix(self):
        """Returns the updated state transition matrix (A) of the model"""
        V = abs(self.getVel())
        airDragA = 0.5*self.Cd*self.surfArea*V/self.state.mass
        rollResF = g*self.rollResCoef*self.state.mass/self.wheelRadius
        if ( (V == 0) and ( abs(self.input.F) < rollResF) ):
            rollResA = 0
            self.state.A = 0
        elif ( abs(self.input.F) > rollResF ) or (V > 0.5):
            rollResA = self.getDirection()*rollResF/(self.state.mass**2)
        else:
            rollResA = 0
            self.state.A = 0
            self.state.V = 0
            
        dt = self.dt
        heading = self.state.heading
        cos_heading = math.cos(heading)
        sin_heading = math.sin(heading)
        dtt = dt**2
        A = [0]*6
              #Px, Py,     V                  A         Heading  Mass
        A[0] = [1, 0, cos_heading*dt, 0.5*cos_heading*dtt, 0 ,    0    ] #Px
        A[1] = [0, 1, sin_heading*dt, 0.5*sin_heading*dtt, 0 ,    0    ] #Py
        A[2] = [0, 0,     1         ,        dt          , 0 ,    0    ] #V
        A[3] = [0, 0,  -airDragA    ,         0          , 0 ,-rollResA] #A
        A[4] = [0, 0,     0         ,         0          , 1 ,    0    ] #Heading
        A[5] = [0, 0,     0         ,         0          , 0 ,    1    ] #Mass
        #print(rollResF, self.input.F)
        #print( "airDrag,%1.1f, rollRes, %1.1f, V,%1.1f"%(airDragA, rollResA, V) ) 
        #print( "A,%s V,%1.1f"%(str(A[3]), V) ) 
        return A

    def _calcInputMatrix(self):
        """Returns the updated input matrix (B) of the model"""
        dt = self.dt
        heading = self.state.heading
        V = self.state.V
        mass = self.state.mass
        B = [0]*6
        B[0] = [0, 0, 0,       0,     0  , 0 ]
        B[1] = [0, 0, 0,       0,     0  , 0 ]
        B[2] = [0, 0, 0,       0,     0  , 0 ]
        B[3] = [0, 0, 0,    1/mass,   0  , 0 ]
        B[4] = [0, 0, 0,       0,    V*dt, 0 ]
        B[5] = [0, 0, 0,       0,     0  , dt]
        return B
