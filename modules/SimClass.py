import os
import pygame
from modules import CarClass
from GSOF_Cockpit import SingleIndicator as SI

class Simulator_base():
    def __init__(self, fps, size=(600, 750), imagePath=r"./images", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255)):
        self.size = size
        self.maxFPS = fps
        self.dt = 1/self.maxFPS
        self.carMdl = CarClass.Car(dt=self.dt, position=(60,60))
        self.pwrRate = 5              #< pix/sec^2/command
        self.steeringRate = 0.002     #< rad/sec/command
        self.bgColor = bgColor
        self.run = False
        self.updateCallBack = None

        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode(size)

        self.car   = pygame.image.load( os.path.join(imagePath, "car.png") )

        self.track = pygame.transform.scale(
            #pygame.image.load( os.path.join(imagePath, "track.png")),
            pygame.image.load( os.path.join(imagePath, "region.png")),
            (size[0], size[0]) )
        self.track_mask = pygame.mask.from_surface(self.track)

        carRect = self.car.get_rect()
        if imageWidth== None and imageHeight == None:
            carSize = (carRect[2], carRect[3])
            
        elif imageWidth == None:
            imageWidth = int(carRect[2]*imageHeight/carRect[3])

        else:
            imageHeight = int(carRect[3]*imageWidth/carRect[2])
            
        carSize = (imageWidth, imageHeight)
        self.car = pygame.transform.scale(self.car, carSize)
        self._rotCar()

        self.initCockpit( pos = (0, self.size[1]-150))

    def initCockpit(self, pos=(0,0)) -> None:
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
                                    "Kp":0.3,
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
                                       "Kp":0.2,
                                       "DegMinMax":(-270,270),
                                       "DegOffset":0,
                                       "DegModulu":360,
                                       }
                            )

        self.gauges = {
            "heading":head,
            "speedometer":spd,
            "steeringWheel":turn,
            "acceleration":acc,
            }

    def start(self) -> None:
        self.run = True
        self._runSimulator()

    def stop(self) -> None:
        self.run = False
    
    def _runSimulator(self) -> None:
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                self._readInputs()
                    
            if self._isCollision() != None:
                self.carMdl.collide()
            self.carMdl.update()
            self._gaugesUpdate()
            
            self._draw()
            if self.updateCallBack != None:
                self.updateCallBack()       #< Use callback function if exists 
            self.clock.tick(self.maxFPS)
        pygame.quit()

    def _readInputs(self) -> None:
        """ No nothing unless override by inheritance """
        return

    def _gaugesUpdate(self) -> None:
        self.gauges['heading'].update(self.carMdl.getHeading(units="deg"))
        self.gauges['steeringWheel'].update(self.carMdl.getSteering(units="deg"))
        self.gauges['speedometer'].update(self.carMdl.getVel())
        self.gauges['acceleration'].update(self.carMdl.getPower())

    def _draw(self):
        """Draw the car"s glob"""
        car, carRect = self._rotCar()
        self.win.fill(self.bgColor) #< Fill the canvas with background color
        self.win.blit(self.track, (0,0))
        self.win.blit(car, carRect) #< Draw the car surface on the canvas
        overlap_surf = self._isCollision()
        if overlap_surf != None:
            self.win.blit(overlap_surf, (0,0))
        for gauge in self.gauges:
            self.gauges[gauge].draw()

        pygame.display.update()

    def _rotCar(self) -> list:
        """Rotate and position the car"s glob"""
        heading_deg = -self.carMdl.getHeading(units="deg")
        pos_pix = self.carMdl.getPosition()
        car = pygame.transform.rotate(self.car, heading_deg)
        self.car_mask = pygame.mask.from_surface(car)
        carRect = car.get_rect(center=pos_pix)
        return (car, carRect)

    def _isCollision(self, x=16, y=10) -> bool:
        pos = self.carMdl.getPosition()
        offset = (int(pos[0] -x), int(pos[1]) -y)
        poi = self.track_mask.overlap(self.car_mask, offset)
        overlap_surf = None
        if poi != None:
            overlap_mask = self.track_mask.overlap_mask(self.car_mask, offset)
            overlap_surf = overlap_mask.to_surface(setcolor = (255, 0, 0))
            overlap_surf.set_colorkey((0, 0, 0))
        return overlap_surf
            
if __name__ == "__main__":
    pygame.init()
    sim = Simulator_base(30, imageWidth=30)
