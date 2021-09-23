import os
# import re

# pattern = "[^Distributor ID.*:].*$"
host_sys_info = os.system('lsb_release -a')
print(type(host_sys_info))
# OS_ID = re.findall(pattern,str(host_sys_info))
OS_ID = str(host_sys_info).replace("Distributor ID: ",'')
print(OS_ID)
if OS_ID == "Raspbian":
    print("I'm raspi")
    from picamera.array import PiRGBArray # Generates a 3D RGB array
    from picamera import PiCamera # Provides a Python interface for the RPi Camera Module
    import time # Provides time-related functions

import cv2 as cv

def open_cam_in_rasp():
    camera = PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 32
    raw_capture = PiRGBArray(camera, size=(640, 480))
    time.sleep(0.1)
    for frame in camera.capture_continuous(raw_capture, format="bgr", use_video_port=True):
        image = frame.array
     
        # Display the frame using OpenCV
        cv2.imshow("Frame", image)
     
        # Wait for keyPress for 1 millisecond
        key = cv2.waitKey(1) & 0xFF
     
        # Clear the stream in preparation for the next frame
        raw_capture.truncate(0)
     
        # If the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

def open_cam():
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        print("No cam")
        exit()
    while True:
        ret, frame = cam.read()
        if not ret:
            print("output streaming ended")
            break
        cv.imshow('CAM',frame)
        if cv.waitKey(1) == ord('q'):
            break
    cam.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    if OS_ID.replace(' ','') == "Raspbian":
        open_cam_in_rasp()
    else:
        open_cam()