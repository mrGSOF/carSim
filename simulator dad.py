import pygame
from modules import CarClass
from GSOF_Cockpit import SingleIndicator as SI

class Simulator():
    def __init__(self, fps, size=(600, 650), selfControll=True, imagePath=r"./images/car.png", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255)):
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
        self.initCockpit( pos = (0, self.size[1]-150))

    def initCockpit(self, pos=(0,0)):
        #Scaling the indicators
        scale = 1.0
        gap = 0
        turn_size = (int(150*scale), int(150*scale))
        alt_size = (int(150*scale), int(150*scale))
        spd_size = (int(150*scale), int(150*scale))
        head_size = (int(150*scale), int(150*scale))
        acc_size = (int(150*scale), int(150*scale))
        background_size = (int(600*scale), int(450*scale))

        #Positioning the gauges
        turn_pos = (pos[0] +gap, pos[1] +gap)
        spd_pos =  (pos[0] +turn_size[0] +gap, turn_pos[1])
        head_pos = (spd_pos[0]  +spd_size[0]  +gap, turn_pos[1])
        acc_pos =  (head_pos[0] +head_size[0] +gap, turn_pos[1])

        folder = "./"
        head = SI.SingleIndicator( self.win, pos=head_pos, size=head_size,
                          imgList={"Frame":pygame.image.load("%s/GSOF_Cockpit/resources/HeadingIndicator_Background.png"%folder),
                                   "Ind":pygame.image.load("%s/GSOF_Cockpit/resources/HeadingWheel.png"%folder),
                                   },
                          coefList={"DegModulu":360,
                                    "DegOffset":-270,
                                    "InToDeg":1,
                                    "InOffset":0,
                                    "DegMinMax":(-720, 720),
                                    "Kp":0.5,
                                    }
                          )

        acc = SI.SingleIndicator( self.win, pos=acc_pos, size=acc_size,
                             imgList={"Frame":pygame.image.load("%s/skin/G_Meter200.png"%folder),
                                      "Ind":pygame.image.load("%s/skin/G_Meter_Ind200.png"%folder),
                                   },
                             coefList={
                                       "InToDeg":-0.5,
                                       "InOffset":0.0,
                                       "Kp":0.1,
                                       "DegMinMax":(-270,270),
                                       "DegOffset":129,
                                       "DegModulu":270,
                                       }
                            )

        spd = SI.SingleIndicator( self.win, pos=spd_pos, size=spd_size,
                             imgList={"Frame":pygame.image.load("%s/GSOF_Cockpit/resources/AirSpeedIndicator_Background.png"%folder),
                                      "Ind":pygame.image.load("%s/GSOF_Cockpit/resources/AirSpeedNeedle.png"%folder),
                                   },
                             coefList={
                                       "InToDeg":-1.0,
                                       "InOffset":0.0,
                                       "Kp":0.3,
                                       "DegMinMax":(-270,0),
                                       "DegOffset":180,
                                       "DegModulu":360,
                                       }
                            )

        turn = SI.SingleIndicator( self.win, pos=turn_pos, size=turn_size,
                             imgList={"Frame":pygame.image.load("%s/skin/Indicator_Background.png"%folder),
                                      "Frame_":pygame.image.load("%s/skin/G_Meter200.png"%folder),
                                      "Ind":pygame.image.load("%s/skin/SteeringWheel300.png"%folder),
                                   },
                             coefList={
                                       "InToDeg":-30.0,
                                       "InOffset":0.0,
                                       "Kp":0.5,
                                       "DegMinMax":(-270,270),
                                       "DegOffset":0,
                                       "DegModulu":360,
                                       }
                            )

        self.gauges = {
            "heading":head,
            "speedometer":spd,
            "steeringWheel":turn,
            "accelaration":acc,
            }
        self.start()

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
            self.gaugesUpdate()
            
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

    def gaugesUpdate(self):
        self.gauges['heading'].update(self.carMdl.getHeading(units="deg"))
        self.gauges['steeringWheel'].update(self.carMdl.getSteering(units="deg"))
        self.gauges['speedometer'].update(self.carMdl.getVel())
        self.gauges['accelaration'].update(self.carMdl.getAcc())

    def _draw(self):
        """Draw the car"s glob"""
        car, carRect = self._rotCar()
        self.win.fill(self.bgColor) #< Fill the canvas with background color
        self.win.blit(car, carRect) #< Draw the car surface on the canvas
        for gauge in self.gauges:
            #print(gauge)
            self.gauges[gauge].draw()

        pygame.display.update()

    def _rotCar(self):
        """Rotate and position the car"s glob"""
        heading_deg = -self.carMdl.getHeading(units="deg")
        pos_pix = self.carMdl.getPosition()
        car = pygame.transform.rotate(self.car, heading_deg)
        carRect = car.get_rect(center=pos_pix)
        return car, carRect

if __name__ == "__main__":
    pygame.init()
    sim = Simulator(30, imageWidth=30)
