#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from snipsTools import SnipsConfigParser
from leds import LedControl
import threading

#from hermes_python.hermes import Hermes
import os
import re
import queue
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from types import SimpleNamespace
from pprint import pprint

import json
import asyncio

CONFIGURATION_ENCODING_FORMAT = "utf-8"

CONFIG_INI =  "config.ini"

_id = "snips-skill-adafruit-voice-bonnet"  

class Skill_AdafruitBonnet:
    def __init__(self):
        try:
            config = SnipsConfigParser.read_configuration_file(CONFIG_INI)
        except :
            config = None
            print("Config could not be loaded")

        username = None
        password = None        
        self.mqtt_addr = "127.0.0.1"
        self.mqtt_port = 1883
        self.verbose = False
        self.site_id = "default"

        self.leds = LedControl()

        if config:
            if config.get('MQTT', None) is not None:
                self.mqtt_addr = config.get('MQTT').get('hostname', self.mqtt_addr)
                self.mqtt_port = config.get('MQTT').get('port', self.mqtt_port)

            if config.get('debug', None) is not None:
                self.verbose = config.get('debug').get('verbose', self.verbose)
            
        if self.verbose:
            print("Verbose Logging Enabled")
        
        self.loop = asyncio.get_event_loop()
        self.site_id = config.get('global').get("siteid", self.site_id)
        print("Site ID is " + self.site_id)
        
        t = threading.Thread(target=self.leds.run, args=())
        t.daemon = True
        t.start()

        self.start_blocking()

    def on_connect(self, client, userdata, flags, reason_code, properties):
        """Called when connected to MQTT broker."""
        client.subscribe("hermes/hotword/#")
        client.subscribe("hermes/asr/#")
        client.subscribe("hermes/tts/#")

        print("Connected. Waiting for events.")


    def on_disconnect(self, client, userdata, flags, rc):
        """Called when disconnected from MQTT broker."""
        client.reconnect()


    def on_message(self, client, userdata, msg):
        """Called each time a message is received on a subscribed topic."""
        try:
            payloadStr = msg.payload.decode('utf-8')
        except (UnicodeDecodeError, AttributeError):
            payloadStr = msg.payload

        payload = json.loads(payloadStr, object_hook=lambda d: SimpleNamespace(**d))
        # ignore messages not for us
        if payload.siteId != self.site_id:
            if self.verbose:
                print("Ignoring message for site id" + payload.siteId)
            return
        
        if self.verbose:
            print("Got Topic " + msg.topic)
        
        if msg.topic == "hermes/hotword/toggleOn":
            self.leds.set_state("idle")
        if msg.topic == "hermes/asr/startListening":
            self.leds.set_state("listening")
        if msg.topic == "hermes/tts/say":
            self.leds.set_state("speaking")
        if msg.topic == "hermes/tts/sayFinished":
            self.leds.set_state("idle")    
        
    # --> Register callback function and start MQTT
    def start_blocking(self):
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = self.on_connect
        client.on_disconnect = self.on_disconnect
        client.on_message = self.on_message

        client.connect(self.mqtt_addr, self.mqtt_port)
        client.loop_forever()
        
  
if __name__ == "__main__":
    Skill_AdafruitBonnet()
