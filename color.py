#importing Modules

import cv2
import numpy as np
import serial
import time
import winsound
ser = serial.Serial('COM5', 9600, timeout=0.1)

#Capturing Video through webcam.
TOTAL=7
BPM=0
temp=0
alarm=False
cap = cv2.VideoCapture(0)

while(1):
        rec_data = ser.readline()
        # print(rec_data)
        time.sleep(1)
        if(len(rec_data)>2):
                #print(rec_data)
                BPM = rec_data[rec_data.find(b'@') + 1:rec_data.find(b'-')]
                temp = rec_data[rec_data.find(b'-') + 1:rec_data.find(b'$')]
                BPM=BPM.decode('utf-8')
                temp = temp.decode('utf-8')
                print(BPM)
                print(temp)
        _, img = cap.read()
        img = np.array(img, dtype=np.uint8)

        #converting frame(img) from BGR (Blue-Green-Red) to HSV (hue-saturation-value)

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        #defining the range of Yellow color
        yellow_lower = np.array([136,87,111],np.uint8)
        yellow_upper = np.array([180,255,255],np.uint8)

        #finding the range yellow colour in the image
        yellow = cv2.inRange(hsv, yellow_lower, yellow_upper)

        #Morphological transformation, Dilation         
        kernal = np.ones((5 ,5), "uint8")

        blue=cv2.dilate(yellow, kernal)

        res=cv2.bitwise_and(img, img, mask = yellow)

        #Tracking Colour (Yellow) 
        contours,hierarchy=cv2.findContours(yellow,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        for pic, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if(area>300):
                        #print("det")
                        alarm=True
                        
                        x,y,w,h = cv2.boundingRect(contour)     
                        img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
                        cv2.putText(img, "Blood detected", (x-5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0))

        cv2.putText(img, "heartbeat: {}".format(BPM), (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(img, "temp: {}".format(temp), (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if img != None:
                cv2.imshow("Color Tracking",img)
                img = cv2.flip(img,1)
                cv2.imshow("red",res)
        if(alarm==True):
                alarm=False
                winsound.PlaySound('s.wav', winsound.SND_FILENAME)  ##windowns inbuilt
        if cv2.waitKey(10) & 0xFF == 27:
                cap.release()
                cv2.destroyAllWindows()
                break
