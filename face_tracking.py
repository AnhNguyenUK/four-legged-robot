import subprocess
import re

# Get the Distro ID of the current Linux system, use to distinguish between host (developer env) and target (raspberry)

distro_id_line_pattern = "Distributor ID:.+?(?=n)."
process = subprocess.Popen(["lsb_release","-a"],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
host_sys_info = process.communicate()
OS_ID_LINE = re.findall(distro_id_line_pattern,str(host_sys_info[0]))
distro_ID = OS_ID_LINE[0].replace("Distributor ID:\\t",'')
distro_ID = distro_ID.replace("\\n",'')
print(distro_ID)

# -------------------- Import dependencies -----------------------------#
# For the raspberry pi env, the picamera lib is use to display the result from camera


if distro_ID == "Raspbian":
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
        cv.imshow("Frame", image)
     
        # Wait for keyPress for 1 millisecond
        key = cv.waitKey(1) & 0xFF
     
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
    # if distro_ID == "Raspbian":
    #     open_cam_in_rasp()
    # else:
    open_cam()