from state import Color
import cv2
import utils

class Detector(object):
    def __init__(self,mask,parameters):
        self.mask = mask
        self.red_range = parameters.red_range
        self.white_range = parameters.white_range
        self.debug = parameters.debug
        self.min_area = parameters.min_area
        self.max_area = parameters.max_area
        self.max_ball_radius = parameters.max_ball_radius
        self.min_area_to_radius_sqaured_ratio = parameters.min_area_to_radius_sqaured_ratio
        self.drawn_circle_radius = parameters.drawn_circle_radius
    """
    Parameter: frame (destructible frame)
    """
    def detect(self,frame):
        hsv_frame = self.__getHSV(frame)
        ret = {}
        for color in [Color.RED, Color.WHITE]:
            contours = self.__getContours(hsv_frame, frame.copy(), color) 
            circles = self.__findBalllikeContoursPositions(frame.copy(), contours)
            ret[color] = circles
        return ret
    def __getContours(self,hsv_frame, contour_frame, color): 
        color_ranges = self.red_range if color == Color.RED else self.white_range
        final_mask = None
        for i,range in enumerate(color_ranges):
            lower = range[0]
            upper = range[1]
            current_mask = cv2.inRange(hsv_frame, lower, upper)
            if i == 0:
                final_mask = current_mask
            final_mask = cv2.bitwise_or(final_mask,current_mask)
        
        '''
        kernel = np.ones((2,2),np.uint8)
        erosion = cv2.erode(final_mask,kernel,iterations = 1)
        #dilation = cv2.dilate(erosion,kernel,iterations = 1)
        utils.imshow('erosion', erosion)
        #utils.imshow('dilation of erosion', dilation)
        '''
        _, contours, _ = cv2.findContours(final_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        if self.debug:
            img = cv2.drawContours(contour_frame, contours, -1, (0,255,0), 2)
            utils.imshow('contours', contour_frame)
        
        return contours
        
    def __getHSV(self,frame):
        frame_removedbumpers = cv2.bitwise_and(frame,frame, mask = self.mask)
        gaussblur = cv2.bilateralFilter(frame_removedbumpers,9,75,75)
        hsv = cv2.cvtColor(gaussblur, cv2.COLOR_BGR2HSV)	
        if self.debug:
            utils.imshow('hsv_blurred_frame',hsv)
            utils.imshow('frame_removed_bumpers',frame_removedbumpers)
        return hsv
        

    def __findBalllikeContoursPositions(self,frame_circles, contours):
        good_circles = []
        for i,cont in enumerate(contours):
            area = cv2.contourArea(cont)
            if area < self.min_area or area > self.max_area:
                 continue
            (x,y),r = cv2.minEnclosingCircle(cont)
            circle = Circle(x,y,r)
            if circle.r > self.max_ball_radius:
                continue
            if area / circle.r**2 < self.min_area_to_radius_sqaured_ratio:
                continue
                
            if self.debug:
                cv2.circle(frame_circles,(int(x),int(y)),self.drawn_circle_radius,(0,255,0),2)
                utils.imshow('contour circles',frame_circles)
            good_circles.append(circle)
        return good_circles
class Circle(object):
    def __init__(self,x,y,r):
        self.x = x
        self.y= y
        self.r = r
    def center(self):
        return (self.x,self.y)
    def intCenter(self):
        return (int(self.x),int(self.y))
    def __str__(self):
        return "("+str(self.x)+","+str(self.y)+","+str(self.r)+")"
        