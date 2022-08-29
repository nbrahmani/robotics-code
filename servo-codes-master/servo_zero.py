from typing import List
import time
import sys

import numpy as np
from flask import Flask, request
from werkzeug import serving

from gpiozero import PWMLED


class Servo:
    def __init__(self, pin, frequency=50):
        self.cur_pos = .1
        self.pin = pin
        self.led = PWMLED(self.pin)
        self.wait = .1

    def rotate(self, value, steps):
        if steps is None:
            steps = 4
        steps = abs(self.cur_pos - value) * steps * 100
        ar = np.linspace(self.cur_pos, value, int(steps))
        print(ar)
        for x in ar:
            print(x)
            self.led.value = x
            self.cur_pos = x
            time.sleep(self.wait)

    def reset(self):
        self.led.off()

    def close(self):
        self.led.close()



class Service:
    def __init__(self, pins: List[int], frequency: int):
        self.pins = pins
        self.servos = {}
        for pin in self.pins:
            self.servos[pin] = Servo(pin, frequency=frequency)
        self.app = Flask("Servo")
        self.init_routes()

    def init_routes(self):
        @self.app.route("/rotate", methods=["GET"])
        def _set_duty():
            if "pin" not in request.args:
                return "Pin not given"
            if "value" not in request.args:
                return "Value not given"
            pin = int(request.args.get("pin"))
            value = float(request.args.get("value"))
            steps = request.args.get("steps")
            steps = steps and float(steps)
            self.servos[pin].rotate(value, steps)
            return f"Issued rotate command for pin: {pin} for value: {value}, steps: {steps}"

        @self.app.route("/reset", methods=["GET"])
        def _reset():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.servos[pin].reset()
            return f"Issued reset command for pin: {pin}"

        @self.app.route("/reset_all", methods=["GET"])
        def _reset_all():
            for pin in self.servos:
                self.servos[pin].reset()
            return "Issued reset command for all pins"

        @self.app.route("/close", methods=["GET"])
        def _close():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.servos[pin].close()
            return f"Issued close command for pin: {pin}"


    def start(self):
        serving.run_simple("0.0.0.0", 2233, self.app, threaded=True)


if __name__ == '__main__':
    pins = sys.argv[1].split(",")
    if len(sys.argv) > 2:
        frequency = int(sys.argv[2])
    else:
        frequency = 50
    service = Service([*map(int, pins)], frequency)
    service.start()
