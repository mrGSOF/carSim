import pygame
from modules import CarClass

class Simulator():
    def __init__(self, fps, size=(500, 500), selfControll=True, imagePath=r"./images/car.png", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255)):
        self.size = size
        self.maxFPS = fps
        self.dt = 1/self.maxFPS
        self.carMdl = CarClass.Car(self.dt)
        self.accRate = 10             #< pix/sec^2/command
        self.steeringRate = 0.002     #< rad/sec/command
        self.bgColor = bgColor
        self.selfControll = selfControll
        self.run = False

        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode(size)


        self.car = pygame.image.load(imagePath)
        carRect = self.car.get_rect()
        if imageWidth== None and imageHeight == None:
            carSize = (carRect[2], carRect[3])
            
        elif imageWidth == None:
            imageWidth = int(carRect[2]*imageHeight/carRect[3])

        else:
            imageHeight = int(carRect[3]*imageWidth/carRect[2])
            
        carSize = (imageWidth, imageHeight)
        self.car = pygame.transform.scale(self.car, carSize)
##        self.car = pygame.Surface((10,10), pygame.SRCALPHA)
##        self.car.fill("Gray")


    def start(self):
        self.run = True
        self._runSimulator()

    def stop(self):
        self.run = False
    
    def _runSimulator(self):
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                if self.selfControll:
                    keys = pygame.key.get_pressed()
##                    self._readAccKeys(keys)
                    self._readDirKeys(keys)
                    
            self.carMdl.update()
            self._draw()
            self.clock.tick(self.maxFPS)
        pygame.quit()

##    def _readAccKeys(self, keys):
##        if keys[pygame.K_s]:
##            self.carMdl.velocity[1] += self.accRate.self.dt
##            
##        elif keys[pygame.K_w]:
##            self.carMdl.velocity[1] -= self.accRate.self.dt
##        
##        if keys[pygame.K_d]:
##            self.carMdl.velocity[0] += self.accRate.self.dt
##            
##        elif keys[pygame.K_a]:
##            self.carMdl.velocity[0] -= self.accRate.self.dt
        
    def _readDirKeys(self, keys):
        """Sample the keys and update the variables of the car"""
        if keys[pygame.K_q]:
            self.carMdl.addAcc(-self.accRate)
            
        elif keys[pygame.K_1]:
            self.carMdl.addAcc(+self.accRate)
        
        if keys[pygame.K_p]:
            self.carMdl.addSteering(+self.steeringRate)
            
        elif keys[pygame.K_i]:
            self.carMdl.addSteering(-self.steeringRate)

        if keys[pygame.K_o]:
            self.carMdl.setSteering(0)
        
        if keys[pygame.K_z]:
            self.carMdl.setVel(0)

    def _draw(self):
        """Draw the car's glob"""
        car, carRect = self._rotCar()
        self.win.fill(self.bgColor) #< Fill the canvas with background color
        self.win.blit(car, carRect) #< Draw the car surface on the canvas
        pygame.display.update()

    def _rotCar(self):
        """Rotate and position the car's glob"""
        heading_deg = -self.carMdl.getHeading(units='deg')
        pos_pix = self.carMdl.getPosition()
        car = pygame.transform.rotate(self.car, heading_deg)
        carRect = car.get_rect(center=pos_pix)
        return car, carRect

if __name__ == "__main__":
    import time
    import math
    import threading
    
    pygame.init()
    sim = Simulator(30, imageWidth=30)
    threading.Thread(target=sim.start).start()
    vel = 40
    targetPos = (500, 0)
    sim.carMdl.state.Px = 100
    sim.carMdl.state.Py = 100
    time.sleep(1.5)
    while True:
        time.sleep(0.01)
        currentPos = (sim.carMdl.state.Px, sim.carMdl.state.Py)
        currentAngle = sim.carMdl.state.heading
        targetAngle = (math.atan2((targetPos[1]-currentPos[1]), (targetPos[0]-currentPos[0])))
        print(targetAngle)
        sim.carMdl.setSteering((targetAngle-currentAngle))
        
        if abs(currentPos[0]-targetPos[0]) < 5 and abs(currentPos[1]-targetPos[1]) < 5:
            sim.carMdl.setVel(0)
        else:
            sim.carMdl.setVel(vel)
        
        # print(math.degrees(sim.carMdl.input.steering))
