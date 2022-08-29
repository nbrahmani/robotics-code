## Code to control TFLuna Lidar.

### Links

https://makersportal.com/blog/distance-detection-with-the-tf-luna-lidar-and-raspberry-pi

### Connections (physical pins)

* 1 => 2 (5V)
* 2 => 8
* 3 => 10
* 4 => 6 (GND)

Configuration pin towards 0x19

### Instructions

* add enable_uart=1 to /boot/config.txt
* reboot
* python3 test.py

###

* Working on pi, not on jetson
* UART
