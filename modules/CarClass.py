import math
from modules import SteeringClass
from modules import MathLib as ml

class Car():
    def __init__(self, dt, heading=0, velocity=0, position=[0,0]):
        self.heading = heading            #< Car heading (rad)
        self.Vmag = velocity              #< Car's velocity (pix/s)
        self.acc = 0                      #< Car's x/y velocity (pix/s)
        self.velocity = [velocity, 0]     #< Car's x/y velocity (pix/s)
        self.steering = SteeringClass.Steering(angle=0) #< Car's steering system
        self.pos = position               #< Car's x/y position (pix)
        self.Cd = 0.05
        self.dt = dt

    def addAcc(self, dAcc):
        self.acc += dAcc

    def setVel(self, Vmag):
        self.Vmag = Vmag
        self.acc = 0

    def turn(self, dRad):
        self.steering.turn(dRad)
        
    def update(self):
        self._calcNewVelocity()
        self._applyFriction()
        self._move()
    
    def _applyFriction(self):
        self.Vmag *= (1 -self.Cd)
        for i in range(len(self.velocity)):
            self.velocity[i] *= (1 -self.Cd)

    def _calcNewVelocity(self):
        self.Vmag += self.acc*self.dt
        new_vel = [self.Vmag, 0]
        R = ml.genR(self.heading)
        self.velocity = ml.MxV(R, new_vel)

    def _move(self):
        R = self.steering.R
        if self.Vmag > 0:
            self.velocity = ml.MxV(R, self.velocity)
            self.heading += self.steering.angle
        else: #if self.Vmag < 0:
            self.velocity = ml.MxV(ml.negR(R), self.velocity)
            self.heading -= self.steering.angle
            
        while self.heading > 2*math.pi:
            self.heading -= 2*math.pi
        while self.heading < -2*math.pi:
            self.heading += 2*math.pi
            
        #print("%1.2f"%(self.heading))
        for i in range(0,len(self.velocity)):
            self.pos[i] += self.velocity[i]*self.dt
            
