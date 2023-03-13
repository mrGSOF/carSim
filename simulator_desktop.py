import json
import pygame
from modules import CarClass
import mqttComunication as comunication
from modules import codes

class Simulator():
    def __init__(self, fps, size=(500, 500), selfControll=True, imagePath=r"./images/car.png", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255), sendMqtt=False):
        self.size = size
        self.maxFPS = fps
        self.dt = 1/self.maxFPS
        self.carMdl = CarClass.Car(self.dt)
        self.accRate = 10             #< pix/sec^2/command
        self.steeringRate = 0.002     #< rad/sec/command
        self.bgColor = bgColor
        self.selfControll = selfControll
        self.run = False
        
        self.targetPoses = [(200, 200),(100, 100),(100, 0),(0, 0)]
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
                
            self.mqtt = comunication.COM(self.broker, name="ArduCarServer", sendId=True)
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
            print(senderId)
            if len(data) == dataLen:
                if data.isdigit():
                    data = int(data)
                    if data == codes.carCodes.ACKNOWLEGE:
                        print("message recieved")
                        pass #stop resending
                    
                    elif data == codes.carCodes.FINISHED:
                        if len(self.targetPoses) > 0:
                             self._sendNewPosPacket(self.targetPoses.pop(0))
                        else:
                            self._sendEndPacket()
                        
                    
                    elif data == codes.carCodes.ERROR:
                        self._sendLastPacket()
                        print("message not recieved properly, resending")
                    
                else:
                    if data.strip()[0] == "{" and data[-1] == "}":
                        data = json.loads(data.replace("'", '"'))
                        steeringAngle = data["steering"]
                        velocity = data["velocity"]
                        self.carMdl.setSteering(float(steeringAngle))
                        self.carMdl.setVel(float(velocity))
                    else:
                        print("json error")
                        self._sendERROR()
                            


    def start(self):
        self.run = True
        self._runSimulator()

    def stop(self):
        self.run = False

    def _sendERROR(self):
        self.lastPacket = codes.carCodes.ERROR
        self._sendLastPacket()
        
    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})

    def _sendPosPacket(self, pos, angle):
        self.lastPacket = {"type": "pos", "pos": pos, "angle": angle}
        self._sendLastPacket()

    def _sendNewPosPacket(self, pos):
        self.lastPacket = {"type": "newPos", "pos": pos}
        self._sendLastPacket()
    
    def _sendEndPacket(self):
        self.lastPacket = codes.carCodes.FINISHED
        self._sendLastPacket()
    
    def _runSimulator(self):
        self._sendNewPosPacket(self.targetPoses.pop(0))
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
            self._sendPosPacket((self.carMdl.state.Px, self.carMdl.state.Py), self.carMdl.state.heading)
        pygame.quit()
        
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
    sim = Simulator(30, imageWidth=30, sendMqtt=True)
    sim.start()
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
        sim.carMdl.setSteering((targetAngle-currentAngle))
        
        if abs(currentPos[0]-targetPos[0]) < 5 and abs(currentPos[1]-targetPos[1]) < 5:
            sim.carMdl.setVel(0)
        else:
            sim.carMdl.setVel(vel)
        
        # print(math.degrees(sim.carMdl.input.steering))
