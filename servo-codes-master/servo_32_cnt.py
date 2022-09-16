import serial

# Inside Driver directory
# make clean
# make -j
# sudo make load

# Change /dev/ttyUSB0 with whatever port it is
# Do "sudo chmod 776 /dev/ttyUSB0" in case it's not already, so that it is writable by user
# Have to do it each time it's connected

port = serial.Serial("/dev/ttyUSB0", 9600, timeout=0.1, write_timeout=0.1)

def move(servo: int, pos: int, spd: int):
     """Move servo to position

    Args:
        servo: servo motor number
        pos: position to go to, usually between 300 - 2500
        delay: Time taken for the traversal in miliseconds

    """
     port.write(f"#{servo}P{pos}T{spd}\r\n".encode())

# A better function can be written here which makes sure that small angle
# rotations don't take too much time, e.g., 1000 - 1200 should not take
# too long and 300 - 2500 should not be too fast
