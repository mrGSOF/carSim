import time
import math
import json
import mqttCommunication as communication

class Car:
    def __init__(self, vel=40, targetPoses=[(200, 200),(100, 100),(100, 0),(0, 0)]):
        self.targetPos = None
        self.currentPos = None
        self.currentAngle = None
        self.lastPacket = None
        self.vel = vel
        self.run = False
        self.targetPoses = targetPoses
        if self.targetPoses:
            self.targetPos = self.targetPoses.pop(0)
        else:
            raise Exception("[carMovement] targetPoses cannot be empty")
        
        ## debugging variables ###
        self.first = True
        ### end ###
                
        with open("settings.json", "r") as f:
            settings = json.load(f)
            self.topic = settings["mqtt"]["topic"]
            self.broker = settings["mqtt"]["broker"]

        self.mqtt = communication.COM(self.broker, name="ArduCar", sendId=True)
        self.mqtt.changeOnMessage(self._onMessage)
        self.mqtt.subscribe(self.topic)
        self.mqtt.loop_forever()
        
    
        
    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})
    
    def _sendPosPacket(self, angle, vel, time=-1, distance=-1):
        self.lastPacket = {"steering": angle, "velocity": vel, "time": time, "distance": distance}
        self._sendLastPacket()

    def _onMessage(self, client, clientDat, msg):
        msg = msg.payload.decode("utf-8")
        data = json.loads(msg)
        dataLen = int(data["len"])
        senderId = data["senderId"]
        data = str(data["data"])
        if senderId != self.mqtt.name:
            if len(data) == dataLen:
                    
                if data.strip()[0] == "{" and data[-1] == "}":
                    try:
                        data = json.loads(data.replace("'", '"'))
                        self.currentPos = data["pos"]
                        self.currentAngle = self.getShortestAngle(data["angle"])
                        self.calc()
                        
                    except:
                        print("[CarMovementServer] received invalid packet!")
                else:
                    print("[CarMovementServer] received invalid packet!")

    def getShortestAngle(self, angle):
        if abs(angle) > math.pi:
            if angle > 0:
                angle = -2*math.pi + angle
            else:
                angle = 2*math.pi + angle
        return(angle)
    
    def calc(self):
        if self.targetPos != None and self.currentPos != None:

            targetAngle = (math.atan2((self.targetPos[1]-self.currentPos[1]), (self.targetPos[0]-self.currentPos[0])))
            angle = self.getShortestAngle(targetAngle-self.currentAngle)
            distance = math.sqrt((self.targetPos[1]-self.currentPos[1])**2 + (self.targetPos[0]-self.currentPos[0])**2)
            # print(f"final angle is {angle}, current angle is {self.currentAngle}, target angle is {targetAngle}, ERROR is {targetAngle-angle}")
            if self.first:
                self.first = False

                print(f"[{self.targetPos}] angle {angle}, vel {self.vel}, divided {self.vel*(2.2)}, distance {distance}")
            print(f"angle {(angle/abs(self.vel))} vel {self.vel} distance {distance}")
            self._sendPosPacket(-1*(angle/abs(self.vel)), -1*self.vel, distance=self.vel/2)
            self._sendPosPacket(angle/abs(self.vel), self.vel, distance=self.vel/2)
            self._sendPosPacket(0, self.vel, distance=distance*0.9)
            print("done and icbm")
            
            if abs(self.currentPos[0]-self.targetPos[0]) < 10 and abs(self.currentPos[1]-self.targetPos[1]) < 10:
                self.targetPos = None
                if self.targetPoses:
                    self.targetPos = self.targetPoses.pop(0)
                    
                    self.first = True
                
                self._sendPosPacket(0, 0)
                time.sleep(0.5)
            
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