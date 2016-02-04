import cv2
import sys
import numpy as np
import math
from detect import Circle
import utils
from sets import Set
class Contour(object):
    def __init__(self,contour):
        self.contour = contour
        self.area = cv2.contourArea(contour)
        (x,y),r = cv2.minEnclosingCircle(contour)
        self.circle = Circle(x,y,r)
        self.ratio = (self.area/(self.circle.r**2*math.pi))
        self.group = -1
def main(image):
    def ratio(contour):
        (x,y),r = cv2.minEnclosingCircle(contour)
        area = cv2.contourArea(contour)
        ratio = (area/(r**2*math.pi))
        return ratio
    def center(contour):
        (x,y),r = cv2.minEnclosingCircle(contour)
        return (x,y)
    def overlap(c1,c2):
        return inside(c1.circle.x,c1.circle.y,c2) or inside(c2.circle.x,c2.circle.y,c1)
    def inside(x,y,c2):
        return (c2.circle.x-x)**2+(c2.circle.y-y)**2 <= c2.circle.r**2
    def toRemove(c,contours):
        booleans = []
        for contour in contours:
            if overlap(c,contour):
                booleans.append(c.ratio < contour.ratio)
        return any(booleans)
    def collinear(c1,c2,c3):
        (x1,y1) = c1.circle.center()
        (x2,y2) = c2.circle.center()
        c = c3.circle
        (x3,y3,r3) = (c.x,c.y,c.r)
        s = (y2-y1)/(x2-x1)
        ps = -1 / s
        x_naut = (y3-y1+s*x1-ps*x3)/(s-ps)
        y_naut = s*(x_naut-x1)+y1
        dist = utils.distance((x_naut,y_naut),(x3,y3))
        return dist < (r3/2)
    def findLines(contour_tuples):
        sets = []
        for c1 in contour_tuples:
            for c2 in [x for x in contour_tuples if x is not c1]:
                for c3 in [x for x in contour_tuples if x is not c1 and x is not c2]:
                    if collinear(c1,c2,c3):
                        found = False
                        for set in sets:
                            if c1 in set or c2 in set or c3 in set:
                                for c in [c1,c2,c3]:
                                    set.add(c)
                                    found = True
                                  
                        if not found:
                            sets.append(Set([c1,c2,c3]))
                            '''
                        paint_frame = image.copy()
                        cv2.drawContours(paint_frame,[x.contour for x in [c1,c2,c3]],-1,(0,255,0),2)
                        cv2.imshow('painting',paint_frame)
                        cv2.waitKey(0)'''
        return sets
    #image_path = args[0]
    #image = cv2.imread(image_path)
    
    gray = image.copy()
    gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    new_gray = cv2.equalizeHist(gray)
    res = np.hstack((gray,new_gray))
    #cv2.imshow('res',res)
    #cv2.waitKey(0)
    
    
    
    edges = cv2.Canny(image,200,300)
    cv2.imshow('edges',edges)
    cv2.imshow('image',image)
    contour_frame = image.copy()
    _, contours, _ = cv2.findContours(edges.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    contours_tuples = [Contour(c) for c in contours]
    contours_tuples = [c for c in contours_tuples if c.ratio > .5 and c.area > 100]
    contours_2 = [c for c in contours_tuples if not toRemove(c,contours_tuples)]
    contours_tuples = contours_2
    contour_centers = np.array([np.array([c.circle.x,c.circle.y]) for c in contours_tuples])
    contour_centers = np.float32(contour_centers)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    ret,label,center=cv2.kmeans(contour_centers,3,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)    
    def modifyContours(centers):
        A = centers[label.ravel()==0]
        B = centers[label.ravel()==1]
        C = centers[label.ravel()==2]
        for point in centers:
            group = 0 if point in A else 1 if point in B else 2
            for contour in contours_tuples:
                if utils.manhattanDistance(point,contour.circle.center()) < 10:
                    contour.group = group
                    break
    def colorFun(contour):
        g = contour.group
        return (255,0,0) if g==0 else (0,255,0) if g==1 else (0,0,255)
    modifyContours(contour_centers)
    lines = []
    for i in [0,1,2]:
        lines.append(findLines([x for x in contours_tuples if x.group == i]))
    for sets in lines:
        for set in sets:
            paint_frame = image.copy()
            cv2.drawContours(paint_frame,[x.contour for x in set],-1,(0,255,0),2)
            cv2.imshow('painting',paint_frame)
            cv2.waitKey(0)
    contours = [c.contour for c in contours_tuples]
    '''
    for i,tuple in enumerate(contours_tuples):
        color = colorFun(tuple)
        contour_frame = image.copy()
        contour_frame = cv2.drawContours(contour_frame, contours, i, color, 2)
        cv2.imshow('contours', contour_frame)
        cv2.waitKey(0)
        '''
    contour_frame = image.copy()
    contour_frame2= image.copy()
    for i,tuple in enumerate(contours_tuples):
        contour_frame = cv2.drawContours(contour_frame,contours,i,colorFun(tuple),-1)
    for sets in [lines[1],lines[2]]:
        s = list(sets[0])
        s0 = s[0]
        for tuple in s:
            contour_frame2 = cv2.circle(contour_frame2,tuple.circle.intCenter(),int(tuple.circle.r/2),colorFun(s0),-1)
        #contour_frame2 = cv2.drawContours(contour_frame2,[x.contour for x in s],-1,colorFun(s0),-1)

    cv2.imshow('contours',contour_frame)
    cv2.imshow('contours2',contour_frame2)
    cv2.waitKey(0)
    
    white_mask = cv2.inRange(contour_frame2, (0,0,255),(0,0,255) )
    cv2.imshow('white_mask',white_mask)
    red_mask = cv2.inRange(contour_frame2, (0,255,0),(0,255,0))
    cv2.imshow('red_mask',red_mask)
    cv2.waitKey(0)
    
    gaussblur = cv2.bilateralFilter(image.copy(),9,75,75)
    hsv = cv2.cvtColor(gaussblur, cv2.COLOR_BGR2HSV)
    
    red_image = cv2.bitwise_and(hsv,hsv, mask = red_mask)
    white_image = cv2.bitwise_and(hsv,hsv, mask = white_mask)

    '''
    kernel = np.ones((5,5),np.uint8)
    red_image = cv2.erode(red_image,kernel,iterations = 2)
    '''
    cv2.imshow('white_image',white_image)
    cv2.imshow('red_image',red_image)
    cv2.waitKey(0)
    
    def getRange(image):
        acc = []
        for row in image:
            acc.extend([x for x in row if not any([x[0]==0,x[1]==0,x[2]==0])])
        minb = min(x[0] for x in acc)
        print minb
        ming = min(x[1] for x in acc)
        print ming
        minr = min(x[2] for x in acc)
        print minr
        maxb = max(x[0] for x in acc)
        print maxb
        maxg = max(x[1] for x in acc)
        print maxg
        maxr = max(x[2] for x in acc)
        print maxr
        a = 20
        #min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(image)
        #print min_val,max_val
        return (int(minb-a),int(ming-a),int(minr-a)),(int(maxb+a),int(maxg+a),int(maxr+a))
    

    r_lower,r_upper = getRange(red_image)
    w_lower,w_upper = getRange(white_image)
    reds = cv2.inRange(hsv, r_lower,r_upper)
    cv2.imshow('reds',reds)
    whites = cv2.inRange(hsv, w_lower,w_upper)
    cv2.imshow('whites',whites)
    cv2.waitKey(0)
    
    return np.array([[[r_lower,r_upper]],[[w_lower,w_upper]]])
    
    '''
    feature_params = dict( maxCorners = 100,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

    # Parameters for lucas kanade optical flow
    lk_params = dict( winSize  = (15,15),
                      maxLevel = 2,
                      criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

    # Create some random colors
    color = np.random.randint(0,255,(100,3))

    # Take first frame and find corners in it
    old_gray = cv2.cvtColor(image.copy(), cv2.COLOR_BGR2GRAY)
    p0 = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
    feature_frame = image.copy()
    for point in p0:
        print (point[0][0],point[0][1])
        feature_frame = cv2.circle(feature_frame,(point[0][0],point[0][1]),10,(255,0,0),1)
    cv2.imshow('features',feature_frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    '''
    '''
    edges_copy = edges.copy()
    circles = cv2.HoughCircles(edges_copy,cv2.HOUGH_GRADIENT,1,20,
                                param1=50,param2=30,minRadius=0,maxRadius=50)
    circles = np.uint16(np.around(circles))
    for i in circles[0,:]:
        print circles
        # draw the outer circle
        edges_copy = cv2.circle(edges_copy,(i[0],i[1]),i[2],(0,255,0),2)
        # draw the center of the circle
        edges_copy = cv2.circle(edges_copy,(i[0],i[1]),2,(0,0,255),3)

    cv2.imshow('detected circles',edges_copy)
    '''
    cv2.destroyAllWindows()

    
if __name__ == "__main__":
    main(sys.argv[1:])
