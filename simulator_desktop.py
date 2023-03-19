import json
import pygame
import numpy as np
from modules import CarClass
import mqttCommunication as communication
from modules import codes

class Simulator():
    def __init__(self, fps, size=(340*2, 290*2), selfControl=True, imagePath=r"./images/car.png", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255), sendMqtt=False):
        self.size = size   # a pixel is 5mm
        self.maxFPS = fps
        self.dt = 1/self.maxFPS
        self.carMdl = CarClass.Car(self.dt)
        self.accRate = 10             #< cm/sec^2/command
        self.steeringRate = 0.0002     #< rad/sec/command
        self.bgColor = bgColor
        self.selfControl = selfControl
        self.run = False
        
        self.vel = 0
        self.time = 0
        
        self.lastPos = None
        self.lastPacket = None

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
                        time = distance/(velocity)
                    self.time = time
                    self.vel = np.clip(float(steeringAngle), -2, 2)
                    self.carMdl.setSteering(steeringAngle)

                else:
                    print("json error")
                            


    def start(self):
        self.run = True
        self._runSimulator()

    def stop(self):
        self.run = False
        print("exiting this shithole")
        self.mqtt.disconnect()
        pygame.quit()

        
    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})

    def _sendPosPacket(self, pos, angle):
        self.lastPacket = {"pos": pos, "angle": angle}
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
            self.carMdl.update()
            self._draw()
            self.clock.tick(self.maxFPS)
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

    def _draw(self):
        """Draw the car's glob"""
        car, carRect = self._rotCar()
        self.win.fill(self.bgColor) #< Fill the canvas with background color
        self.win.blit(car, carRect) #< Draw the car surface on the canvas
        pygame.draw.circle(self.win, (255,0,0), (200,100), 2, width=0)
        pygame.display.update()

    def _rotCar(self):
        """Rotate and position the car's glob"""
        heading_deg = -self.carMdl.getHeading(units='deg')
        pos_pix = self.carMdl.getPosition()
        car = pygame.transform.rotate(self.car, heading_deg)
        carRect = car.get_rect(center=pos_pix)
        return car, carRect

if __name__ == "__main__":
    
    pygame.init()
    
    sim = Simulator(30, imageWidth=40, selfControl=False, sendMqtt=True)
    try:
        sim.start()
    except KeyboardInterrupt:
        sim.stop()