import time
import math
import json
import mqttComunication as comunication
from modules import codes

class Car:
    def __init__(self, vel=40):
        self.targetPos = None
        self.currentPos = None
        self.currentAngle = None
        self.lastPacket = None
        self.vel = vel
        self.run = False
        
        with open("settings.json", "r") as f:
            settings = json.load(f)
            self.topic = settings["mqtt"]["topic"]
            self.broker = settings["mqtt"]["broker"]

        self.mqtt = comunication.COM(self.broker, name="ArduCar", sendId=True)
        self.mqtt.changeOnMessage(self._onMessage)
        self.mqtt.subscribe(self.topic)
        self.mqtt.loop_forever()
    
    def _sendERROR(self):
        self.lastPacket = codes.carCodes.ERROR
        self._sendLastPacket()
        
    def _sendEndPacket(self):
        self.lastPacket = codes.carCodes.FINISHED
        self._sendLastPacket()
        
    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})
    
    def _sendPosPacket(self, angle, vel):
        self.lastPacket = {"steering": angle, "velocity": vel}
        self._sendLastPacket()

    def _onMessage(self, client, clientDat, msg):
        msg = msg.payload.decode("utf-8")
        data = json.loads(msg)
        dataLen = int(data["len"])
        senderId = data["senderId"]
        data = str(data["data"])
        if senderId != self.mqtt.name:
            if len(data) == dataLen:
                if data.isdigit():
                    data = int(data)
                    if data == codes.carCodes.ACKNOWLEGE:
                        
                        
                        pass #stop resending
                    elif data == codes.carCodes.FINISHED:
                        pass #car is done, if no packet is sent, resend the last packet
                    
                    elif data == codes.carCodes.ERROR:
                        self._sendLastPacket()
                        print("message not recieved properly, resending")
                        
                else:
                    if data.strip()[0] == "{" and data[-1] == "}":
                        data = json.loads(data.replace("'", '"'))
                        if data["type"] == "pos":
                            self.currentPos = data["pos"]
                            self.currentAngle = self.getShortestAngle(data["angle"])
                            self.calc()
                        elif data["type"] == "newPos":
                            self.targetPos = data["pos"]
                            
                        else:
                            self._sendERROR()
                    else:
                        self._sendERROR()
    def getShortestAngle(self, angle):
        if abs(angle) > math.pi:
            if angle > 0:
                angle = -2*math.pi + angle
            else:
                angle = 2*math.pi + angle
        return(angle)
    
    def calc(self):
        if self.targetPos != None and self.currentPos != None:
            # print(f"target pos is {self.targetPos}")
            # print(f"current pos is {self.currentPos}")
            targetAngle = (math.atan2((self.targetPos[1]-self.currentPos[1]), (self.targetPos[0]-self.currentPos[0])))
            angle = self.getShortestAngle(targetAngle-self.currentAngle)
            print(f"final angle is {angle}, current angle is {self.currentAngle}, target angle is {targetAngle}, ERROR is {targetAngle-angle}")
            self._sendPosPacket(angle/abs(self.vel), self.vel)
            # print(f"angle is {angle/self.vel}, and angle/vel is {angle/self.vel}")
            # self._sendPosPacket(0, self.vel)
            
            if abs(self.currentPos[0]-self.targetPos[0]) < 2 and abs(self.currentPos[1]-self.targetPos[1]) < 2:
                self.targetPos = None
                self._sendPosPacket(0, 0)
                self._sendEndPacket()
                time.sleep(0.5)
            
            # print(math.degrees(sim.carMdl.input.steering))
    def stop(self):
        self.run = False

if __name__ == "__main__":
    import sys
    car = Car()
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        car.mqtt.disconnect()
        time.sleep(0.5)
        sys.exit(0)