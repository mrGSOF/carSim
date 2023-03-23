import json
import os
import cv2
import pygame
import time
import numpy as np
import base64
from modules import CarClass
import mqttCommunication as communication
from collections import deque
from GSOF_Cockpit import SingleIndicator as SI

class Simulator():
    def __init__(self, fps, size=(340*2, 290*2), selfControl=True, imagePath=r"./images", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255), sendMqtt=False):
        self.size = size   # a pixel is 5mm
        self.maxFPS = fps
        self.dt = 1/self.maxFPS
        self.carMdl = CarClass.Car(dt=self.dt, position=(100,100))
        self.accRate = 10             #< pix/sec^2/command
        self.steeringRate = 0.002     #< rad/sec/command
        self.bgColor = bgColor
        self.selfControl = selfControl
        self.run = False
        self.waitingForNextPacket = False
        self.que = deque(maxlen=10)
        
        self.vel = 0
        self.time = 0
        
        self.lastPos = None
        self.lastPacket = None

        self.clock = pygame.time.Clock()
        self.win = pygame.display.set_mode(size)

        self.car   = pygame.image.load( os.path.join(imagePath, "car.png") )

        self.track = pygame.transform.scale(
            #pygame.image.load( os.path.join(imagePath, "track.png")),
            pygame.image.load( os.path.join(imagePath, "region.png")),
            (size[0], size[0]))
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
        self.sendMqtt = sendMqtt
        if self.sendMqtt:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.broker = settings["mqtt"]["broker"]
                self.topic = settings["mqtt"]["topic"]
                
            self.mqtt = communication.COM(self.broker, name="ArduCarServer", sendId=True)
            self.mqtt.changeOnMessage(self._onMessage)
            self.mqtt.subscribe(self.topic)
            self.mqtt.loop_forever()
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
            "acceleration":acc,
            }
    
    def _onMessage(self, client, clientDat, msg):
        msg = msg.payload.decode("utf-8")
        data = json.loads(msg)
        dataLen = int(data["len"])
        senderId = data["senderId"]
        data = str(data["data"])
        
        
        if senderId != self.mqtt.name:
            if len(data) == dataLen:
                
                if data.strip()[0] == "{" and data[-1] == "}":
                    data = json.loads(data.replace("'", '"'))
                    steeringAngle = data["steering"]
                    velocity = data["velocity"]
                    distance = int(data["distance"])
                    time = int(data["time"])*self.maxFPS
                    if distance != -1:
                        time = int(abs((distance/velocity)*self.maxFPS))
                    self.que.append({"steering": steeringAngle, "velocity": velocity, "time": time})


                else:
                    print("json error")
                            


    def start(self):
        self.run = True
        self._runSimulator()

    def stop(self) -> None:
        self.run = False
        print("exiting this shithole")
        self.mqtt.disconnect()
        pygame.quit()

        
    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})

    def _sendPosPacket(self, pos, angle):
        img = pygame.surfarray.array3d(self.win)
        # img = img.reshape(img.shape[1], img.shape[0], img.shape[2])
        # cv2.imshow("asdSAD", img)
        # cv2.waitKey(1)
        # time.sleep(5)
        print(img.shape)
        # print(img)
        _, img = cv2.imencode(".jpg", img)
        with open("tmp.txt", "w")as f:
            f.write(str(list(img)))
        print(list(img))
        img = base64.b64encode(img).decode("utf-8")
            
        self.lastPacket = {"pos": pos, "angle": angle, "img": (img)}
        self._sendLastPacket()
    
    def _runSimulator(self):
        """
        Runs the simulator, updating the car model and drawing the screen.

        Parameters: 
            self (Simulator): The simulator object.

        Returns:
            None
        """
        while self.run:
            if self.time <= 0 and self.que:
                self.waitingForNextPacket = False
                packet = self.que.popleft()
                print(packet)
                self.time = packet["time"]
                self.vel = packet["velocity"]
                self.carMdl.setSteering(np.clip(float(packet["steering"]), -2, 2))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False
                if self.selfControl:
                    keys = pygame.key.get_pressed()
                    self._readDirKeys(keys)
            if self.time != 0:
                self.carMdl.setVel(float(self.vel))
                if self.time > 0:
                    self.time -= 1

            # print( self._isCollision() )
            if self._isCollision() != None:
                # print( self.carMdl.getPosition() )
                # print("Collision detected")
                self._bounceCar()

            self.carMdl.update()
            self._gaugesUpdate()
            
            self._draw()
            self.clock.tick(self.maxFPS)
            if not self.que and self.waitingForNextPacket == False and self.time <= 0:
                print("sending pos")
                self.waitingForNextPacket = True
                self._sendPosPacket((self.carMdl.state.Px, self.carMdl.state.Py), self.carMdl.state.heading)

        self.stop()
        
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

    def _gaugesUpdate(self) -> None:
        self.gauges['heading'].update(self.carMdl.getHeading(units="deg"))
        self.gauges['steeringWheel'].update(self.carMdl.getSteering(units="deg"))
        self.gauges['speedometer'].update(self.carMdl.getVel())
        self.gauges['acceleration'].update(self.carMdl.getAcc())

    def _draw(self):
        """Draw the car's glob"""
        car, carRect = self._rotCar()
        self.win.fill(self.bgColor) #< Fill the canvas with background color
        self.win.blit(self.track, (0,0))
        self.win.blit(car, carRect) #< Draw the car surface on the canvas
        overlap_surf = self._isCollision()
        if overlap_surf != None:
            self.win.blit(overlap_surf, (0,0))
        pygame.draw.circle(self.win, (255,0,0), (200,200), 2, width=0)
        for gauge in self.gauges:
            #print(gauge)
            self.gauges[gauge].draw()

        pygame.display.update()

    def _rotCar(self) -> list:
        """Rotate and position the car"s glob"""
        heading_deg = -self.carMdl.getHeading(units="deg")
        pos_pix = self.carMdl.getPosition()
        car = pygame.transform.rotate(self.car, heading_deg)
        self.car_mask = pygame.mask.from_surface(car)
        carRect = car.get_rect(center=pos_pix)
        return(car, carRect)

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

    def _bounceCar(self):
        V = 0.8*self.carMdl.getVel()
        if V:
            V *= -1
        self.carMdl.setVel(V)
        self.carMdl.setAcc(0)
            
if __name__ == "__main__":
    
    pygame.init()
    
    sim = Simulator(30, imageWidth=40, selfControl=False, sendMqtt=True)
    try:
        sim.start()
    except KeyboardInterrupt:
        sim.stop()