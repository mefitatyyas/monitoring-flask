from paho.mqtt import client as mqtt_client
import requests
from PIL import Image, ImageDraw, ImageFont
import io

broker = 'broker.emqx.io'
port = 1883 
topic = 'bmkg/kirimcamera2'

client = mqtt_client.Client("bmkguser123")
client.connect(broker, port)
client.subscribe(topic)

def on_message(client, userdata, message):
    text = message.payload.decode('utf-8')
    response = requests.post(f"http://localhost:5000/genset/camera", data={"img":text})
    if response.ok : print(response.text) 
    else : print(response)
    
client.on_message = on_message
client.loop_forever()