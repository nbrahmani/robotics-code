# MIT License
# Copyright (c) 2019 JetsonHacks
# See license
# Using a CSI camera (such as the Raspberry Pi Version 2) connected to a
# NVIDIA Jetson Nano Developer Kit using OpenCV
# Drivers for the camera and OpenCV are included in the base image

import cv2 as cv
import numpy as py
import os
import time


def focusing(val):
    value = (val << 4) & 0x3ff0
    data1 = (value >> 8) & 0x3f
    data2 = value & 0xf0
    os.system("i2cset -y 6 0x0c %d %d" % (data1, data2))


def sobel(img):
    img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    img_sobel = cv.Sobel(img_gray, cv.CV_16U, 1, 1)
    return cv.mean(img_sobel)[0]


def laplacian(img):
    img_gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)
    img_sobel = cv.Laplacian(img_gray, cv.CV_16U)
    return cv.mean(img_sobel)[0]


# gstreamer_pipeline returns a GStreamer pipeline for capturing from the CSI camera
# Defaults to 1280x720 @ 60fps
# Flip the image by setting the flip_method (most common values: 0 and 2)
# display_width and display_height determine the size of the window on the screen
def gstreamer_pipeline(capture_width=1280, capture_height=720, display_width=1280,
                       display_height=720, framerate=60, flip_method=0):
    return ('nvarguscamerasrc ! '
    'video/x-raw(memory:NVMM), '
    'width=(int)%d, height=(int)%d, '
    'format=(string)NV12, framerate=(fraction)%d/1 ! '
    'nvvidconv flip-method=%d ! '
    'video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! '
    'videoconvert ! '
    'video/x-raw, format=(string)BGR ! appsink'  % (capture_width,capture_height,framerate,flip_method,display_width,display_height))


def show_camera():
    max_index = 10
    max_value = 0.0
    last_value = 0.0
    dec_count = 0
    focal_distance = 10
    focus_finished = False
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    multiplier = 2
    display_width, display_height = 320 * multiplier, 180 * multiplier
    capture_width, capture_height = 320 * multiplier, 180 * multiplier  # 320, 180
    # width, height = 1280, 720
    fr = 60
    gp = gstreamer_pipeline(capture_width=capture_width, capture_height=capture_height,
                            display_width=display_width, display_height=display_height,
                            framerate=fr, flip_method=0)
    print(gp)
    cap = cv.VideoCapture(gp, cv.CAP_GSTREAMER)
    if cap.isOpened():
        window_handle = cv.namedWindow('CSI Camera', cv.WINDOW_AUTOSIZE)
        # Window
        while cv.getWindowProperty('CSI Camera',0) >= 0:
            ret_val, img = cap.read()
            cv.imshow('CSI Camera',img)

            if dec_count < 6 and focal_distance < 1000:
                #Adjust focus
                focusing(focal_distance)
                print("Val: %f"%(focal_distance))
                #Take image and calculate image clarity
                val = laplacian(img)
                # Find the maximum image clarity
                if val > max_value:
                    max_index = focal_distance
                    max_value = val

                #If the image clarity starts to decrease
                if val < last_value:
                    dec_count += 1
                else:
                    dec_count = 0
                #Image clarity is reduced by six consecutive frames
                if dec_count < 6:
                    last_value = val
                    #Increase the focal distance
                    focal_distance += 10

            elif not focus_finished:
                #Adjust focus to the best
                focusing(max_index)
                focus_finished = True
            # This also acts as
            keyCode = cv.waitKey(16) & 0xff
            # Stop the program on the ESC key
            if keyCode == 27:
                break
            elif keyCode == 10:
                max_index = 10
                max_value = 0.0
                last_value = 0.0
                dec_count = 0
                focal_distance = 10
                focus_finished = False
        cap.release()
        cv.destroyAllWindows()
    else:
        print('Unable to open camera')


def capture_images():
    max_index = 10
    max_value = 0.0
    last_value = 0.0
    dec_count = 0
    focal_distance = 10
    focus_finished = False
    j = 0
    # To flip the image, modify the flip_method parameter (0 and 2 are the most common)
    # width, height = 3264, 1848
    # fr = 21
    display_width, display_height = 640, 360
    capture_width, capture_height = 640, 360  # 320, 180
    # width, height = 1280, 720
    fr = 60
    cap = cv.VideoCapture(gstreamer_pipeline(capture_width=capture_width, capture_height=capture_height,
                                             display_width=display_width, display_height=display_height,
                                             framerate=fr, flip_method=0),
                          cv.CAP_GSTREAMER)
    try:
        if cap.isOpened():
            # Window
            for i in range(30):
                ret, img = cap.read()
                if not ret:
                    print("Could not capture image")
                    continue
                else:
                    print("Focusing")
                    focusing(focal_distance)
                    focal_distance += 20
                # if dec_count < 6 and focal_distance < 1000:
                #     # Adjust focus
                #     focusing(focal_distance)
                #     # Take image and calculate image clarity
                #     val = laplacian(img)
                #     # Find the maximum image clarity
                #     if val > max_value:
                #         max_index = focal_distance
                #         max_value = val

                #     # If the image clarity starts to decrease
                #     if val < last_value:
                #         dec_count += 1
                #     else:
                #         dec_count = 0
                #     # Image clarity is reduced by six consecutive frames
                #     if dec_count < 6:
                #         last_value = val
                #         # Increase the focal distance
                #         focal_distance += 50
                # elif not focus_finished:
                #     # Adjust focus to the best
                #     focusing(max_index)
                #     focus_finished = True
                time.sleep(.2)
                print(f"{i} iteration")
                cv.imwrite(f"bleh_{j:02d}.png", img)
                j += 1
            cap.release()
    except KeyboardInterrupt:
        cap.release()


if __name__ == '__main__':
    # capture_images()
    show_camera()
