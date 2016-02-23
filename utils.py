import numpy as np
import cv2

def distance(p1,p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) 
def manhattanDistance(p1,p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
def getIntTuple(float_tuple):
    return (int(float_tuple[0]),int(float_tuple[1]))
def updateBallPositions(state,ball_dict):
    for ball,pos in ball_dict.items():
        state.getBall(ball).updatePosition(pos)
def imshow(frame,image):
    print image.shape
    h,w = image.shape[0],image.shape[1]
    max_w = 1300.0
    max_h = 700.0
    image_resized = image
    if h > max_h or w > max_w:
        divisor = max(h/max_h,w/max_w)
        image_resized = cv2.resize(image,(int(w/divisor),int(h/divisor)))  
    cv2.namedWindow(frame, cv2.WINDOW_NORMAL)
    cv2.imshow(frame, image_resized)