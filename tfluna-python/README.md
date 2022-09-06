## Code to control TFLuna Lidar.

### Links

https://makersportal.com/blog/distance-detection-with-the-tf-luna-lidar-and-raspberry-pi

### Connections (physical pins) 

(Pi)

* 1 => 2 (5V)
* 2 => 8
* 3 => 10
* 4 => 6 (GND)

(Jetson through UART controller)

* 1 => 5V
* 2 => TX
* 3 => RX
* 4 => GND

### Instructions

* add enable_uart=1 to /boot/config.txt
* reboot
* python3 test.py

###

* Working on pi, jetson
* UART
