from paho.mqtt import client as mqtt_client
import requests

broker = 'broker.emqx.io'
port = 1883
topic = 'bmkg/sistoringsuser'

client = mqtt_client.Client("bmkguser123123")
client.connect(broker, port)
client.subscribe(topic)

def on_message(client, userdata, message):
    # print(message.topic+" "+str(message.payload))
    data = message.payload.decode('utf-8')
    temp, hum, getstatus = data.split(',')
    print(temp, hum, getstatus)
    response = requests.get(f"http://localhost:5000/insert/{temp}/{hum}/{getstatus}")
    if response.ok : print(response.text) 
    else : print("error")
    
client.on_message = on_message
client.loop_forever()


