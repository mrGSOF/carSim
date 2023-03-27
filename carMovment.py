import time
import math
import json
import numpy as np
import mqttCommunication as communication
import pathfinder
import base64
import cv2
import compressing

class Car:
    def __init__(self, vel=40, targetPos = (600,100)):
        self.targetPos = None
        self.currentPos = None
        self.currentAngle = None
        self.lastPacket = None
        self.vel = vel
        self.run = False
        self.targetFinalPos = targetPos
        self.targetPoses = None
        
        self.decompresor = compressing.Decompressor()

        
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
        targetPoses = self.targetPoses
        
        if self.targetPoses == None:
            targetPoses = []
        if self.targetPos == None:
            targetPos = []
        else:
            targetPos = [list(self.targetPos),]
        self.lastPacket = {"steering": angle, "velocity": vel, "time": time, "distance": distance, "targetPoses": targetPos+targetPoses}
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
                    # try:
                    if True:
                        data = json.loads(data.replace("'", '"'))
                        self.currentPos = data["pos"]
                        self.currentAngle = self.getShortestAngle(data["angle"])
                        self.img = self.decompresor.decompress(data["img"])
                        # print(f"current pos is {self.currentPos}")
                        # print(f"target pos is {self.targetPos}")
                        # if (self.targetPoses):
                        #     print(f"{abs(self.targetPos[0]-self.currentPos[0]) >= 20} and {abs(self.targetPos[1]-self.currentPos[1]) >= 20}")
                        if (not self.targetPoses) or (abs(self.targetPos[0]-self.currentPos[0]) >= 20) or (abs(self.targetPos[1]-self.currentPos[1]) >= 20):
                            self.targetPoses = pathfinder.findPath(self.img, pos=(int(self.currentPos[0]), int(self.currentPos[1])), targetPos=(int(self.targetFinalPos[0]), int(self.targetFinalPos[1])), paddingSize=7, dev=True)
                            # print(f"target poses are {self.targetPoses}")
                            # print("got new target poses ;)")
                        if self.targetPoses:
                            self.targetPos = self.targetPoses.pop(0)
                        else:
                            print("[CarMovementServer] no more target poses")
                            # raise Exception("[CarMovementServer] destination unreachable")
                        self.calc()
                        
                    # except Exception as e:
                    #     print(f"[CarMovementServer] received invalid packet!, error is {e}")
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
            # if self.first:
            #     self.first = False

            #     print(f"[{self.targetPos}] angle {angle}, vel {self.vel}, divided {self.vel*(2.2)}, distance {distance}")
            # print(f"angle {(angle/abs(self.vel))} vel {self.vel} distance {distance}")
            # print(self.targetPos)
            dAngle = angle/abs(self.vel)
            radius = 1/dAngle
            sin = math.sin(math.degrees(dAngle/2))
            turnDistance = abs(self.vel*sin*2) # for angles smaller than 0.5 radians, the turn distance is very close to the r*angle
            # print(f"distance is {distance} and turnDistance is {turnDistance}")
            # print(f"radius is {radius}, vel is {self.vel}, sin is {sin}, and turnDistance is {turnDistance}")
            # print(f"turnDistance is {turnDistance}, and actual distance is {distance}")
            if turnDistance > distance:
                self._sendPosPacket(-1*(dAngle), -1*self.vel, distance=self.vel/2)
                self._sendPosPacket(dAngle, self.vel, distance=self.vel/2)
                
            else:
                self._sendPosPacket(dAngle, self.vel, distance=turnDistance)
                distance-=turnDistance
                print(distance)
                
                
            self._sendPosPacket(0, self.vel, distance=distance*0.95)
            
            if abs(self.currentPos[0]-self.targetPos[0]) < 20 and abs(self.currentPos[1]-self.targetPos[1]) < 20:
                self.targetPos = None
                if self.targetPoses:
                    self.targetPos = self.targetPoses.pop(0)
                else:
                    print("reached target pos, done")
                
                self._sendPosPacket(0, 0)
                time.sleep(0.1)
            
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