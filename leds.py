import asyncio
import time
import adafruit_dotstar
import board
import random

DOTSTAR_DATA = board.D5
DOTSTAR_CLOCK = board.D6

global_state = "idle"

class LedControl():
    def __init__(self):
        global global_state
        global_state = "idle"
        self.dots =  adafruit_dotstar.DotStar(DOTSTAR_CLOCK, DOTSTAR_DATA, 3, brightness=0.2)
        self.dots.auto_write = False
        self.dots.fill((0, 0, 0))

    def set_state(self, newState):
        global global_state
        global_state = newState
    
    def delay_on_state(self, delay, state):
        global global_state
        if global_state == state:
            time.sleep(delay)
            self.dots.show()

    def idle(self):
        global global_state
        last_led = -1
        self.dots.fill((0, 0, 0))
        while global_state == "idle":
            # Python is weird - no do while
            while True:
                led = random.randrange(0, 3)
                if led != last_led:
                    break

            last_led = led
            for j in range(0, 256, 5):
                self.dots[led] = (0,j,0)
                self.delay_on_state(0.05, "idle")

            for j in range(0, 256, 5):
                self.dots[led] = (0,255 - j,0)
                self.delay_on_state(0.05, "idle")

    def listening(self):
        index = 0
        self.dots.fill((0, 0, 0))
        while global_state == "listening":            
            self.dots[2 - index] = (0,0,255)
            self.delay_on_state(0.150, "listening")
            self.dots[2 - index] = (0,0,0)
            index = (index + 1) % 3

    def speaking(self):
        while global_state == "speaking":
            for j in range(0, 256, 5):
                self.dots.fill((j, 0, j))
                self.delay_on_state(0.01, "speaking")

            for j in range(0, 255, 5):
                self.dots.fill((255 - j, 0, 255 - j))
                self.delay_on_state(0.01, "speaking")

    def run(self):
        while True:
            self.idle()
            self.listening()
            self.speaking()

        while True:
            global global_state
            print(global_state)
            time.sleep(1)
