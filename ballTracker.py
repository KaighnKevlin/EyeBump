import cv2
import numpy as np
import Queue
import threading
import time
import traceback, sys
import importlib
from analyze import *
import utils

'''
TODO
-sort balls with options
-remove all magic values
-rename windows appropriately
-place the score
-optimization
-class for contours?/everything?
-mask,video in parameters


-investigate contours
'''
'''
-shot chart, makes and misses
-new age, bump recognition
'''

class Ball(object):
    def __init__(self, id, color):
        self.id = id
        self.position = (-1,-1)
        self.scored = False
        self.vanished_frames = 0
        self.moving = False
        self.moving_timer = 0
        self.color = color
    
    def updatePosition(self, point, parameters):                    
        self.moving_timer -= 1
        
        if (self.moving and utils.manhattanDistance(self.position,point) >= parameters.stay_moving_threshold) or (not self.moving and utils.manhattanDistance(self.position,point) > parameters.become_moving_threshold):
            self.moving_timer = 5
            self.moving = True
            self.position = point
        else:
            self.moving = self.moving_timer > 0
    def getPositionInts(self):
        return (int(self.position[0]),int(self.position[1]))
    def __unicode__(self):
        return "Ball " + str(self.id)
        
class Hole(object):
    def __init__(self, position, parameters):
        self.position = position
        self.max_hole_distance = parameters.max_hole_distance
        self.num_frames_cooldown = parameters.num_frames_cooldown
        self.cooldown_timer = 0
    def checkBallsScored(self, balls, reader, game_score):
        self.cooldown_timer -= 1
        if self.cooldown_timer > 0:
            return False
        for ball in balls:
            if not ball.scored and utils.manhattanDistance(ball.position,self.position) < self.max_hole_distance:
                ball.scored = True
                ball.moving = False
                reader.ballScored(ball.id)
                game_score[ball.color] += 1
                self.cooldown_timer = self.num_frames_cooldown
                break
    def badCircle(self,circles):
        if self.cooldown_timer > 0:
            for circle in circles:
                x,y,r = circle
                if utils.manhattanDistance((x,y), self.position) < self.max_hole_distance:
                    circles.remove(circle)
            
class Color(object):
    RED = 0
    WHITE = 1

        
    
def getBallClosestToPoint(point, available_balls):
    min = 1000
    for ball in available_balls:
        dist = utils.manhattanDistance(ball.position, point)
        if(dist < min): 
            best_ball = ball
            min = dist
    return min,best_ball
    
def getCircleClosestToBall(ball, circles):
    min = 1000
    for circle in circles:
        x,y,r = circle
        dist = utils.manhattanDistance(ball.position, (x,y))
        if(dist < min): 
            best_circle = circle
            min = dist
    return best_circle,min

def findMatchings(circles_to_be_matched, balls_in_play, parameters):
    balls_is_matched = {}
    for ball in balls_in_play:
        balls_is_matched[ball] = False
    unmatched_circles = []
    
    #find close matchings
    for circle_id,circle in enumerate(circles_to_be_matched):
        x,y,r = circle
        center = (int(x),int(y))
        radius = int(r)
        min,closest_ball = getBallClosestToPoint(center, balls_in_play)
        if min < 10: #really? match 1st one < 10?
            closest_ball.vanished_frames = 0
            balls_is_matched[closest_ball] = True
            closest_ball.updatePosition((x,y), parameters)
        else:
            unmatched_circles.append(circle)
    
    #check vanished balls
    vanished_balls = [ball for ball in balls_in_play if not balls_is_matched[ball]]
    ball_to_circle = {}
    for ball in vanished_balls:
        ball.vanished_frames += 1
        if len(unmatched_circles) >= 1:
            ball_to_circle[ball] = getCircleClosestToBall(ball, unmatched_circles)
    ball_circle_pairs = ball_to_circle.items()
    #print ball_circle_pairs
    ball_circle_pairs.sort(key=lambda x:x[1][1])
    for ball, circle in ball_circle_pairs:
        circle = circle[0]
        if circle in unmatched_circles:
            x,y,r = circle
            center = (x,y)
            if utils.manhattanDistance(ball.position, center) < ball.vanished_frames * 60:
                ball.updatePosition(center, parameters)
                unmatched_circles.remove(circle)
        


def drawBallCircles(frame, balls, game_score, parameters):
    font = cv2.FONT_HERSHEY_SIMPLEX#magic
    for ball in balls:
        if ball.scored:
            continue
        pos = ball.getPositionInts()
        cv2.putText(frame,str(ball.id),(pos[0]+6,pos[1]-10), font, .7,(255,255,255),2,cv2.LINE_AA)
        #cv2.putText(frame,str(ball.moving),pos, font, .7,(255,255,255),2,cv2.LINE_AA)
        #cv2.putText(frame,str(ball.vanished_frames),pos, font, .7,(255,255,255),3,cv2.LINE_AA)
                

        color = (200,0,0) if ball.moving else (0,255,0) if ball.vanished_frames == 0 else (0,255,255)#magic
        img = cv2.circle(frame,pos,parameters.drawn_circle_radius,color,2)
    cv2.putText(frame, str(game_score[Color.WHITE])+' - '+str(game_score[Color.RED]),(450,450), font, .7,(255,255,255),2,cv2.LINE_AA)#magic
    cv2.imshow('final', img)
    

def gameIsOver(game_score):
    return game_score[Color.RED] == 5 or game_score[Color.WHITE] == 5
    

def getContours(hsv_frame, contour_frame, parameters, color): 
    color_ranges = parameters.color_ranges[color]
    color_masks = np.array([])
    final_mask = cv2.inRange(hsv_frame,np.array([0,0,0]), np.array([255,255,255]))
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
    cv2.imshow('erosion', erosion)
    #cv2.imshow('dilation of erosion', dilation)
	'''
    image, contours, hierarchy = cv2.findContours(final_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    
    if parameters.debug:
        drawContours(contour_frame, contours)
    
    return contours
    
def getHSV(frame, bumpermask, parameters):
    if parameters.debug:
        cv2.imshow('bumpermask',bumpermask)
    frame_removedbumpers = cv2.bitwise_and(frame,frame, mask = bumpermask)
    gaussblur = cv2.bilateralFilter(frame_removedbumpers,9,75,75)
    hsv = cv2.cvtColor(gaussblur, cv2.COLOR_BGR2HSV)	
    if parameters.debug:
        cv2.imshow('hsv blurred',hsv)
    return hsv
    
def drawContours(contour_frame, contours):
    img = cv2.drawContours(contour_frame, contours, -1, (0,255,0), 2)
    #cv2.putText(contour_frame,str(len(contours)),(150,200), cv2.FONT_HERSHEY_SIMPLEX, .7,(255,255,255),2,cv2.LINE_AA)
    #cv2.putText(contour_frame,str(len(contours)),(150,200), cv2.FONT_HERSHEY_SIMPLEX, .7,(255,255,255),2,cv2.LINE_AA)
    cv2.imshow('contours', contour_frame)

    
def findBalllikeContoursPositions(frame_circles, contours, parameters):
    good_circles = []
    for i,cont in enumerate(contours):
        area = cv2.contourArea(cont)
        if area < parameters.min_area or area > parameters.max_area:
             continue
        (x,y),radius = cv2.minEnclosingCircle(cont)
        #print "circle "+str(i)+": ",x,y,radius
        #print "    area: "+str(cv2.contourArea(cont))+", radius: ",str(radius)
        if radius > parameters.max_ball_radius:
            continue
        if area / radius**2 < parameters.min_area_to_radius_sqaured_ratio:
            continue
            
        if parameters.debug:
            cv2.circle(frame_circles,(int(x),int(y)),parameters.drawn_circle_radius,(0,255,0),2)
            cv2.imshow('contour circles',frame_circles)
        good_circles.append((x,y,radius))
    return good_circles
               
def initializeBallPositions(balls, circles, parameters):
    circles = sorted(circles, key=lambda tup: tup[0])#magic
    for i,ball in enumerate(balls):
        ball.updatePosition((circles[i][0],circles[i][1]), parameters)
def unscoredBalls(balls):
    return [ball for ball in balls if not ball.scored]
def getColor(ball_id, balls):
    for ball in balls:
        if ball_id == ball.id:
            return ball.color
    return -1
    

          
 
def main(args, debug, recording_path):
    video_path = args[0]
    mask_path = args[1]
    parameters = importlib.import_module(args[2])
    is_recording = recording_path != None
    
    if not parameters.debug:
        parameters.debug = debug
    try:
        balls = {
            Color.RED : [Ball(i,Color.RED) for i in range(5)],
            Color.WHITE : [Ball(i,Color.WHITE) for i in range(5,10)]
        }
        all_balls = balls[Color.RED][:]
        all_balls.extend(balls[Color.WHITE])
        game_score = {
            Color.RED: 0, 
            Color.WHITE: 0
        }
        holes = [Hole(parameters.hole_1,parameters), Hole(parameters.hole_2, parameters)]
        cap = cv2.VideoCapture(video_path)
        for i in range(10): #magic
            ret, frame = cap.read()
        table_frame = frame.copy()
        if is_recording:
            out = cv2.VideoWriter(recording_path+".avi",-1, 30.0, (len(frame[0]),len(frame)))##magic
        first = True
        frameNum = 0
        bumper_mask = cv2.imread(mask_path, 0)
        reader = PoolReader(parameters)
        
        
        '''
        reader = PoolReader()
        #comment thread
        comment_queue = Queue.Queue()
        t = threading.Thread(target=doComment)
        thread_continue = True
        t.start()
        '''
        while(cap.isOpened()):
            if gameIsOver(game_score):
                break

            ret, frame = cap.read()	
            frameNum = frameNum + 1
            if frameNum < 50:#magic
                continue
                
 
            hsv_frame = getHSV(frame,bumper_mask,parameters)
            contour_frame = frame.copy()
            circles_frame = frame.copy()
            final_display_frame = frame.copy()
            for color in [Color.RED, Color.WHITE]:
                contours = getContours(hsv_frame, contour_frame, parameters, color) 
                circles = findBalllikeContoursPositions(circles_frame, contours, parameters)

                for hole in holes:
                    hole.badCircle(circles)
                if first:#change name
                    initializeBallPositions(balls[color], circles, parameters)
                else:
                    findMatchings(circles, unscoredBalls(balls[color]), parameters) 
                drawBallCircles(final_display_frame, balls[color], game_score, parameters) 
                holes[color].checkBallsScored(unscoredBalls(balls[color]),reader,game_score)
            first = False
            
            if frameNum > 100:#magic
                sendCoords(reader,all_balls)
            
            if is_recording:
                out.write(final_display_frame)

            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        reader.drawShots(table_frame,parameters)
        if is_recording:
            for i in range(300):
                out.write(table_frame)

        
        cap.release()
        cv2.destroyAllWindows()


    except KeyboardInterrupt:
        print 'interrupt'
        thread_continue = False
    except:
        print 'exception'
        thread_continue = False
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,limit=5, file=sys.stdout)

def sendCoords(reader, balls):
    positions = [ball.position for ball in balls]
    movings = [ball.moving for ball in balls]
    reader.read(positions, movings)

    
if __name__ == "__main__":
    args = sys.argv[1:]
    debug = False
    recording_path = None
    if '-h' in args:
        print "arguments: video_path mask_path parameter_module is_recording_boolean" 
        print "Example: python ballTracker.py videos/will_table_1.avi masks/will1-mask.png parameters.will1"
        sys.exit()
    if '-d' in args:
        print 'Entering debug mode.'
        debug = True
        args.remove('-d')
    if '-r' in args:
        index = args.index('-r')
        if len(args) < index + 2:
            raise ValueError('Please specify the recording path after -r')
        print 'Recording video to ', args[index+1]
        recording_path = args[index+1]
        args.pop(index)
        args.pop(index)
    if len(args) != 3:
        raise ValueError("Invalid number of arguments.")
    main(sys.argv[1:],debug,recording_path)



   






########################################################################
'''#vanished_permanently
            for ball in balls:
                if not ball.scored:
                    #print ball
                    pos = ball.position
                    x,y = ball.getPositionInts()
                    rect = mask_green[y-3:y+3,x-3:x+3]
                    #print rect
                    #frame = cv2.rectangle(frame,(x-3,y+3),(x+3,y-3),(255,0,0),-1)
                    #mask_green = cv2.rectangle(mask_green,(x-5,y+5),(x+5,y-5),(255,0,0),-1)

                    #print ball.id
                    #print pos
                    #print rect
                    count = 0
                    for row in rect:
                        for pixel in row:
                            if pixel > 100:
                                count+=1
                    #print count
                    #print '-----'
                    #print 
                    if count/36 > .5:
                        ball.vanished_permanently = True
                    else:
                        ball.vanished_permanently = False
                '''
'''    
class TempBall(Ball):
    def __init__(self, pos):
        self.id = 11
        self.position = pos
        self.position_history = []
    def updatePosition(self,point):
        Base.updatePosition(self,point)
        self.position_history.append(point)
'''


