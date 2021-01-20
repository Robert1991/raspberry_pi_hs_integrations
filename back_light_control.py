import os
import paho.mqtt.client as mqtt
import json

auto_configure_prefix = "homeassistant"

device_id = "vHMX0L"
device_type = "Raspberry PI Model 3 B"
device_name = "Raspberry PI Touchscreen Panel"
device_firmware_version = "Raspbian GNU/Linux 10 (buster)"

light_id = "aWOY6O"
light_name = "touch_screen_back_light"
command_topic = auto_configure_prefix + "/light/" + light_name + "/set"
state_topic = auto_configure_prefix + "/light/" + light_name + "/state"
homeassistant_status_topic = "homeassistant/status"

auto_configure_json = {"unique_id": light_id,
                       "name": light_name,
                       "state_topic": state_topic,
                       "command_topic": command_topic,
                       "retain": True,
                       "device": {
                           "ids": [device_id],
                           "model": device_type,
                           "name": device_name,
                           "sw_version": device_firmware_version
                       }}
auto_configure_topic = auto_configure_prefix + "/light/" + light_name + "/config"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.publish(auto_configure_topic, json.dumps(auto_configure_json))
    client.subscribe(command_topic)
    client.subscribe(homeassistant_status_topic)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == command_topic:
        payload = str(msg.payload)
        if payload == "b'ON'":
            os.system(
                "sudo sh -c 'echo \"0\" > /sys/class/backlight/rpi_backlight/bl_power'")
            client.publish(state_topic, "ON")
        else:
            os.system(
                "sudo sh -c 'echo \"1\" > /sys/class/backlight/rpi_backlight/bl_power'")
            client.publish(state_topic, "OFF")
    elif msg.topic == "homeassistant/status":
        client.publish(auto_configure_topic, json.dumps(auto_configure_json))


homeassistant_broker = "homeassistant"
mqtt_user = "espUser"
mqtt_passwd = "esp123"

client = mqtt.Client()
client.username_pw_set(mqtt_user, password=mqtt_passwd)
client.on_connect = on_connect
client.on_message = on_message

client.connect(homeassistant_broker, 1883, 60)
client.loop_forever()
