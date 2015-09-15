import cv2
import numpy as np
import sys


def main(args):
    print 'start'
    video_path = args[0]
    video_prefix = args[1]
    cap = cv2.VideoCapture(video_path)
    frameNum= 0
    while(cap.isOpened()):
        ret, frame = cap.read()	
        frameNum= frameNum+ 1
        if(frameNum<=1590):
            continue
        
        cv2.imshow('frame',frame)
        key = cv2.waitKey(0)
        if key == ord('c'):
            print 'image ' + str(frameNum) + ' captured!'
            cv2.imwrite('frames/'+video_prefix+'-'+str(frameNum)+'.png',frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
             break
        

    cv2.destroyAllWindows()
    print 'finished'

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'invalid number of arguments'
        sys.exit()
    main(sys.argv[1:])

