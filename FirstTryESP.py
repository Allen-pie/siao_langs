from machine import Pin
import time
import dht
import network
import requests


sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect('Mytend', 'bebent10')

while not sta_if.isconnected():
    pass

print('Network config:', sta_if.ifconfig())

led = Pin(4, Pin.OUT)
sensor = dht.DHT11(Pin(5))


def send_data_to_server(temperature, humidity):
    url = "http://192.168.1.14:7000/sensor1"
    headers = {"Content-Type": "application/json"}
    data = {
        "temperature": temperature,
        "humidity": humidity,
        "timestamp": "15-02-2025 10:00:30"
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        print("Response:", response.text)
        print("Done Sending Data to Server!")
    except Exception as e:
        print("Error Occurred:", e)

while True:
    try:
        sensor.measure()
        t = sensor.temperature()
        h = sensor.humidity()
        
        print("Temperature:", t)
        print("Humidity:", h)
        
        
        if t > 25:
            led.on()
        else:
            led.off()
        
        
        send_data_to_server(t, h)
        
        time.sleep(1)
    except Exception as e:
        print("Error:", e)