import cv2
import numpy as np
import time
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume


######################################
wCam, hCam = (1280, 720)
#####################################

cap= cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0
detector = htm.handDetector(detectionCon=0.7)



devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange= volume.GetVolumeRange()          #Giai am thanh
minVol= volRange[0]         #loa be'
maxVol= volRange[1]         #loa lon
volBar = 400
volPer =0

while True:
    success, img= cap.read()
    #Find hand
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw= False)
    if len(lmList) != 0:

        #print(lmList[4], lmList[8])  #mediapipe: location finger: 4 thumb finger 8 index finger

        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1+x2)//2 , (y1+y2)//2

        cv2.circle(img,(x1,y1),15,(255,0,255),cv2.FILLED)       #15cen, purple color, fill color
        cv2.circle(img,(x2,y2),15,(255,0,255),cv2.FILLED)
        cv2.line(img,(x1,y1),(x2,y2),(255,0,255),3)             #Draw a line from thumb to index finger
        cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)


        length = math.hypot(x2- x1,y2- y1)          # Do k/c giua 2 dau ngon tay
        #print(length)

        #Hand range 50-300
        #Volume range -96 -0

        vol = np.interp(length,[50,300], [minVol, maxVol])
        volBar = np.interp(length, [50, 300], [400, 150])      #Thanh am luong
        volPer = np.interp(length, [50, 300], [0, 100])       #Ti le phan tran Percentage 0-100
        print(int(length),vol)                      #in khoang cach tay so vs gia tri giai am thanh
        volume.SetMasterVolumeLevel(vol, None)      #Gia tri loa chay tu -96 den 0

        if length<150:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)   #K/c < 150 thi fill green

    cv2.rectangle(img,(50,150),(85,400), (255,255,255), 3)        #creat a rectangle, size (w,h), color, canny
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED) #The same width, hight change vol, filled
    cv2.putText(img,f'{int(volPer)} %', (40,450), cv2.FONT_HERSHEY_COMPLEX,1, (255,0,0), 3)
    cv2.putText(img, f'Vol', (40, 490), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 250, 0), 3)


    cTime = time.time()
    fps = 1/ (cTime - pTime)
    pTime = cTime

    cv2.putText(img,f'FPS:{int(fps)}', (40,50), cv2.FONT_HERSHEY_COMPLEX,1, (255,0,0), 3)
    cv2.putText(img,f'MSSV:1755252021600013', (940, 670), cv2.FONT_HERSHEY_COMPLEX, 0.8, (50, 255, 255), 1)
    cv2.putText(img,f'NGUYEN XUAN BAO', (950, 710), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 250, 0), 3)
    cv2.putText(img,f'CHINH VOLUME BANG NGON TAY', (800, 40), cv2.FONT_HERSHEY_COMPLEX, 0.8, (200, 0, 150), 3)
    cv2.imshow('Volume Hand Control', img)
    cv2.waitKey(1)