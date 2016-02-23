import cv2
import numpy as np
import sys
import utils

def nothing(x):
    pass

def main(argv):
    img_path = argv[0]
    img = cv2.imread(img_path)
    cv2.createTrackbar('H','bars',0,255,nothing)
    cv2.createTrackbar('S','bars',0,255,nothing)
    cv2.createTrackbar('V','bars',0,255,nothing)
    cv2.createTrackbar('H2','bars',255,255,nothing)
    cv2.createTrackbar('S2','bars',255,255,nothing)
    cv2.createTrackbar('V2','bars',255,255,nothing)
    while(1):
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break

        h = cv2.getTrackbarPos('H','bars')
        s = cv2.getTrackbarPos('S','bars')
        v = cv2.getTrackbarPos('V','bars')
        h2 = cv2.getTrackbarPos('H2','bars')
        s2 = cv2.getTrackbarPos('S2','bars')
        v2 = cv2.getTrackbarPos('V2','bars')
        lower = np.array([h,s,v])
        upper = np.array([h2,s2,v2])
        
        
        hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        utils.imshow('hsv',hsv)
        utils.imshow('mask',mask)
        res = cv2.bitwise_and(img,img,mask=mask)
        utils.imshow('bars',img)
        

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(sys.argv[1:])