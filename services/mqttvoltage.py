from paho.mqtt import client as mqtt_client
import requests

broker = 'broker.emqx.io'
port = 1883
topic = 'bmkg/ina219volt'

client = mqtt_client.Client("bmkguser123")
client.connect(broker, port)
client.subscribe(topic)

def on_message(client, userdata, message):
    print(message.topic+" "+str(message.payload))
    data = message.payload.decode('utf-8')
    volt = data.split(',')
    volt = ','.join(volt)
    response = requests.post(f"http://localhost:5000/genset/volt", data={"volt": volt})
    if response.ok : print(response.text) 
    else : print("error")
    
client.on_message = on_message
client.loop_forever()


