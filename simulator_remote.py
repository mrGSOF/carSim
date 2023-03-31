import json
from modules import SimClass
import mqttCommunication as communication
from collections import deque

class Simulator(SimClass.Simulator_base):
    def __init__(self, fps, size=(340*2, 290*2), selfControl=True, imagePath=r"./images/car.png", imageWidth=None, imageHeight=None, bgColor=(255, 255, 255), sendMqtt=False):
        super().__init__(fps, size, imagePath, imageWidth, imageHeight, bgColor)
        self.que = deque(maxlen=10)
        self.vel = 0
        self.time = 0
        self.lastPos = None
        self.lastPacket = None
        self.sendMqtt = sendMqtt
        self.updateCallBack = self._sendOutputPacket
        if self.sendMqtt:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                self.broker = settings["mqtt"]["broker"]
                self.topic = settings["mqtt"]["topic"]
                
            self.mqtt = communication.COM(self.broker, name="ArduCarServer", sendId=True)
            self.mqtt.changeOnMessage(self._onInput)
            self.mqtt.subscribe(self.topic)
            self.mqtt.loop_forever()
    
    def _onInput(self, client, clientDat, msg):
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
                    self.vel = velocity
                    self.carMdl.setSteering(np.clip(float(steeringAngle), -2, 2))
                else:
                    print("json error")
                            
    def stop(self):
        self.mqtt.disconnect()
        super().stop()

    def _sendLastPacket(self):
        self.mqtt.publish(self.topic, {"len": len(str(self.lastPacket)), "data": self.lastPacket})

    def _sendPosPacket(self, pos, angle):
        self.lastPacket = {"pos": pos, "angle": angle}
        self._sendLastPacket()

    def _sendOutputPacket(self):
        self._sendPosPacket((self.carMdl.state.Px, self.carMdl.state.Py), self.carMdl.state.heading)

    def _readDirKeys(self, keys) -> None:
        """Sample the keys and update the variables of the car"""
        return

if __name__ == "__main__":
    pygame.init()
    sim = Simulator(30, imageWidth=40, selfControl=False, sendMqtt=True)
    try:
        sim.start()
    except KeyboardInterrupt:
        sim.stop()
