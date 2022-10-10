from time import sleep
import RPi.GPIO as GPIO

in1 = 24
in2 = 23
en = 25

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)

p=GPIO.PWM(en,1000)
p.start(25)

def forward():
	GPIO.output(in1,GPIO.HIGH)
	GPIO.output(in2,GPIO.LOW)
	print("forward")

def backward():
	GPIO.output(in1,GPIO.LOW)
	GPIO.output(in2,GPIO.HIGH)
	print("backward")

def stop():
	GPIO.output(in1,GPIO.LOW)
	GPIO.output(in2,GPIO.LOW)
	print("stop")

def slow():
	p.ChangeDutyCycle(25)

def medium():
	p.ChangeDutyCycle(50)

def high():
	p.ChangeDutyCycle(75)

def clean():
	GPIO.cleanup()

