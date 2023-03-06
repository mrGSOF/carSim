from modules import MathLib as ml

class Steering():
    def __init__(self, angle=0, Min=-0.7, Max=0.7):
        self.set(angle)      #< Set steering angle (rad)
        self.Min = Min       #< Max steering angle (rad)
        self.Max = Max       #< Max steering angle (rad)

    def turn(self, dRad):
        self.angle = ml.clip(self.angle +dRad, self.Min, self.Max)
        self.R = ml.genR(self.angle)

    def set(self, angle):
        self.angle = angle           #< Steering angle (rad)
        self.R = ml.genR(self.angle) #< 2D rotation matrix
