from typing import List
import sys

from flask import Flask, request
from werkzeug import serving

import serial


class SC08A:
    def __init__(self, portname, debug=False):
        self.port = serial.Serial(portname, 9600, timeout=0.1, write_timeout=0.1)
        self.init_all_motors()
        self.debug = debug

    def init_all_motors(self):
        self.port.write(bytes([0b11000000, 1]))

    def on_motor(self, channels: int):
        first_byte = 0b11000000 | channels
        self.port.write(bytes([first_byte, 1]))

    def off_motor(self, channels: int):
        first_byte = 0b11000000 | channels
        self.port.write(bytes([first_byte, 0]))

    def set_pos_speed(self, channels: int, pos: int, speed: int):
        byte_1 = 0b11100000 | channels
        str_pos = bin(0b10000000000000 | pos)[3:]
        byte_2 = '0' + str_pos[:7]
        if self.debug:
            print("byte_2", byte_2, int(byte_2, 2))
        byte_2 = int(byte_2, 2)  # type: ignore
        byte_3 = '00' + str_pos[7:]
        if self.debug:
            print("byte_3", byte_3, int(byte_3, 2))
        byte_3 = int(byte_3, 2)  # type: ignore
        byte_4 = speed
        self.port.write(bytes([byte_1, byte_2, byte_3, byte_4]))  # type: ignore

    def get_pos(self, channel: int):
        self.port.write(bytes([0b10100000 | channel]))
        high, low = self.port.read(2)
        return int(bin(0b10000000 | high)[3:] + bin(0b1000000 | low)[3:], 2)

    def shutdown(self):
        self.port.close()


class Service:
    def __init__(self, pins: List[int], port: str):
        self.pins = pins
        self.port = port
        self.controller = SC08A(port)
        self.controller.init_all_motors()
        self.app = Flask("Servo")
        self.init_routes()

    def init_controller(self):
        self.controller = SC08A(port)
        self.controller.init_all_motors()

    def init_routes(self):
        @self.app.route("/set_pos", methods=["GET"])
        def _set_pos():
            if "pin" not in request.args:
                return "Pin not given"
            if "pos" not in request.args:
                return "pos (position) not given"
            if "speed" not in request.args:
                print("speed not given. Will use 50")
                speed = 50
            else:
                speed = int(request.args.get("speed"))
            pin = int(request.args.get("pin"))
            pos = int(request.args.get("pos"))
            self.controller.set_pos_speed(pin, pos, speed)
            return f"Setting position for motor: {pin} at: {pos} and speed: {speed}"

        @self.app.route("/get_pos", methods=["GET"])
        def _get_pos():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            return str(self.controller.get_pos(pin))

        @self.app.route("/reset", methods=["GET"])
        def _reset():
            if "pin" not in request.args:
                return "Pin not given"
            pin = int(request.args.get("pin"))
            self.controller.off_motor(pin)
            return f"Turning motor {pin} OFF"

        @self.app.route("/reset_all", methods=["GET"])
        def _reset_all():
            for pin in self.pins:
                self.controller.off_motor(pin)
            return "Issued OFF command for all motors"

        @self.app.route("/close", methods=["GET"])
        def _close():
            _reset_all()
            self.controller.shutdown()
            return "Stopped all motors and turned off the controller"

        @self.app.route("/start", methods=["GET"])
        def _start():
            self.init_controller()
            return "Initialized the controller"

    def start(self):
        serving.run_simple("0.0.0.0", 2233, self.app, threaded=True)


if __name__ == '__main__':
    pins = sys.argv[1].split(",")
    port = sys.argv[2]
    service = Service([*map(int, pins)], port)
    service.start()
