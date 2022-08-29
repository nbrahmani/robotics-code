from typing import List
import time
import sys

import numpy as np
from flask import Flask, request
from werkzeug import serving

import RPi.GPIO as GPIO
from gpiozero import PWMLED

GPIO.setmode(GPIO.BOARD)


class Servo:
    def __init__(self, pin):
        self.cur_pos = None
        self.pin = pin
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)
        self.delta = .2

    def init_position(self, duty):
        self.cur_pos = duty
        self.set_slowly_duty(duty)

    def set_slowly_duty(self, duty, delta=None, delay=None):
        delta = delta or self.delta
        delay = delay or .1
        if self.cur_pos is None or self.cur_pos == duty:
            self.set_duty(duty)
        else:
            while abs(self.cur_pos - duty) > delta:
                if self.cur_pos < duty:
                    self.cur_pos += delta
                else:
                    self.cur_pos -= delta
                self.set_duty(self.cur_pos)
                time.sleep(delay)

    def set_duty(self, duty):
        GPIO.output(self.pin, True)
        self.pwm.ChangeDutyCycle(duty)
        print(f"Setting duty: {duty}")

    def set_duty_zero(self):
        print(f"Resetting pin duty 0: {self.pin}")
        self.pwm.ChangeDutyCycle(0)

    def set_output_false(self):
        print(f"Resetting pin output false: {self.pin}")
        GPIO.output(self.pin, False)

    def pwm_stop(self):
        print("Stopping PWM")
        self.pwm.stop()

    def reset(self):
        print(f"Resetting pin {self.pin}")
        self.pwm.ChangeDutyCycle(0)
        GPIO.output(self.pin, False)


class Service:
    def __init__(self, pins: List[int], frequency: int):
        self.pins = pins
        self.servos = {}
        self.GPIO = GPIO
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)
            self.servos[pin] = Servo(pin)
        self.app = Flask("Servo")
        self.init_routes()

    def reset(self, pin: int):
        self.servos[pin].reset()

    def init_routes(self):
        @self.app.route("/set_duty", methods=["GET"])
        def _set_duty():
            if "pin" not in request.args:
                return "Pin not given"
            if "duty" not in request.args:
                return "Duty not given"
            pin = int(request.args.get("pin"))
            duty = int(request.args.get("duty"))
            delta = request.args.get("delta")
            delay = request.args.get("delay")
            delta = delta and float(delta)
            delay = delay and float(delay)
            self.servos[pin].set_slowly_duty(duty, delta, delay)
            return f"Issued set duty command for pin: {pin} for duty: {duty}, delta: {delta}, delay: {delay}"

        @self.app.route("/reset", methods=["GET"])
        def _reset():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.reset(pin)
            return f"Issued reset command for pin: {pin}"

        @self.app.route("/init_pos", methods=["GET"])
        def _init_pos():
            if "pin" not in request.args:
                return "Pin not given"
            if "duty" not in request.args:
                return "Duty not given"
            pin = int(request.args.get("pin"))
            duty = int(request.args.get("duty"))
            self.servos[pin].init_position(duty)
            return f"Issued init position command for pin: {pin}, duty: {duty}"

        @self.app.route("/duty_zero", methods=["GET"])
        def _set_duty_zero():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.servos[pin].set_duty_zero()
            return "True"

        @self.app.route("/set_output_false", methods=["GET"])
        def _set_output_false():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.servos[pin].set_output_false()
            return "True"

        @self.app.route("/pwm_stop", methods=["GET"])
        def _pwm_stop():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.servos[pin].pwm_stop()
            return "True"


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
