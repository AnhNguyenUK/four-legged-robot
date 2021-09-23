import cv2 as cv

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
    open_cam()