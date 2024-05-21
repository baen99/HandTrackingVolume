import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


######################
# define width and height of camera picture
wCam, hCam = 640, 480
######################


cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0

detector = htm.handDetector(detectionConfidence=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol, maxVol = volRange[0], volRange[1]

# initialize values for the volume and the heigth of the volume bar
vol = 0
volBar = 400
volPer = 0
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)
    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2] # index 4 is tip of thumb
        x2, y2 = lmList[8][1], lmList[8][2] # index 8 is tip of zeigefinger
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 15, (255,0,255), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255,0,255), cv2.FILLED)
        cv2.line(img, (x1,y1), (x2,y2), (255,0,255), 3)
        cv2.circle(img, (cx, cy), 10, (255,0,255), cv2.FILLED)

        length = math.hypot(x2-x1, y2-y1)

        # Hand range 50 to 280
        handMin, handMax = 50, 280
        # Volume range -63.5 to 0.0
        # conversion between them
        vol = np.interp(length, [handMin,handMax], [minVol,maxVol])
        #print(int(length), vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length < 50:
            cv2.circle(img, (cx, cy), 10, (0,255,0), cv2.FILLED)


        # create and display volume bar
        volBar = np.interp(length, [handMin,handMax], [400,150])
        cv2.rectangle(img, (50,150), (85,400), (255,0,0), 3)
        cv2.rectangle(img, (50,int(volBar)), (85,400), (255,0,0), cv2.FILLED)
        volPer = np.interp(length, [handMin,handMax], [0,100])
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)
    
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 3)

    cv2.imshow("WebCam", img)
    cv2.waitKey(1) # wait 1 ms