import threading
import paho.mqtt.client as mqtt
import json
import random

class COM:
    def __init__(self, ip, port=1883, name=None, timeoutPeriod = 60, sendId = False):
        if name == None:
            name = str(random.randint(0, 1000))
        id = 0
        while True:
            try:
                self.client = mqtt.Client(name)
                break
            except:
                name = name+str(id)
                id+=1
        
        self.name = name
        self.sendId = sendId
        self.ip = ip
        self.port = port
        self.timeoutPeriod = timeoutPeriod
        try:
            if self.client.connect(self.ip, self.port, timeoutPeriod) != 0:
                raise Exception("[MQTT] Connection refused")
        except Exception as e:
            print(e)
            raise Exception("[MQTT] Could not connect to mqtt broker, wrong ip or port?")
        # self.client.loop_forever()
        
    def subscribe(self, topic):
        self.client.subscribe(topic, 0)
    
    def publish(self, topic, msg):
        if self.sendId:
            try:
                msg = json.loads(msg)
            except:
                pass
            
            if type(msg) == dict:
                if "senderId" in msg.keys():
                    raise Exception("[MQTT] cannot have senderId as a key in your dictionary")
                msg["senderId"] = self.name
                
            else:
                msg = {"senderId": self.name, "content": msg}
            
            msg = json.dumps(msg)

        self.client.publish(topic, msg)
    
    def disconnect(self):
        self.client.disconnect()
    
    def changeOnMessage(self, onMessage):
        self.client.on_message = onMessage
    
    def loop_forever(self):
        threading.Thread(target=self.client.loop_forever).start()
