import utils
import cv2

class State(object):
    def __init__(self,parameters):
        self.red_balls = [Ball(i,Color.RED,parameters) for i in range(5)]
        self.white_balls = [Ball(i,Color.WHITE,parameters) for i in range(5,10)]
        self.score = {
            Color.RED: 0, 
            Color.WHITE: 0
        }
        self.holes = [Hole(parameters.hole_1,parameters), Hole(parameters.hole_2, parameters)]
        self.drawn_circle_radius = parameters.drawn_circle_radius
    def validDetection(self,detected_circle):
        for hole in self.holes:
            if hole.invalidDetection(detected_circle):
                return False
        return True
    def gameIsOver(self):
        return self.score[Color.RED] >= 5 or self.score[Color.WHITE] >= 5
    def scoreBalls(self):
        for color in [Color.RED,Color.WHITE]:
            balls = self.red_balls if color == Color.RED else self.white_balls
            unscored_balls = [ball for ball in balls if not ball.scored]
            for ball in unscored_balls:
                for hole in self.holes:
                    if hole.ballScored(ball):
                        self.score[color] += 1
    
                    
    def draw(self,frame,frame_number=None):
        font = cv2.FONT_HERSHEY_SIMPLEX#magic
        for color in [Color.RED,Color.WHITE]:
            balls = self.red_balls if color == Color.RED else self.white_balls
            for ball in balls:
                if ball.scored:
                    continue
                pos = ball.getPositionInts()

                cv2.putText(frame,str(ball.id),(pos[0]+6,pos[1]-10), font, .7,(255,255,255),2,cv2.LINE_AA)
                #cv2.putText(frame,str(ball.moving),pos, font, .7,(255,255,255),2,cv2.LINE_AA)
                #cv2.putText(frame,str(ball.vanished_frames),pos, font, .7,(255,255,255),3,cv2.LINE_AA)
                        

                color = (200,0,0) if ball.moving else (0,255,0) if ball.vanished_frames == 0 else (0,255,255)#magic
                img = cv2.circle(frame,pos,self.drawn_circle_radius,color,2)
            if frame_number!=None:
                cv2.putText(frame,str(frame_number),(550,50), font, .7,(255,255,255),2,cv2.LINE_AA)#magic
            cv2.putText(frame, str(self.score[Color.WHITE])+' - '+str(self.score[Color.RED]),(450,450), font, .7,(255,255,255),2,cv2.LINE_AA)#magic
            cv2.imshow('final', img)
    def getBall(self,id):
        if id < 0 or id > 9:
            return None
        if id < 5:
            return self.red_balls[id]
        else:
            return self.white_balls[id-5]
    def getBalls(self):
        ret = self.red_balls
        ret.extend(white_balls)
        return ret
    def ballsState(self):
        d = {}
        for i in range(10):
            d[i] = self.getBall(i).getPositionInts()
        return d
class Ball(object):
    def __init__(self, id, color, parameters):
        self.id = id
        self.position = (-1,-1)
        self.scored = False
        self.vanished_frames = 0
        self.moving = False
        self.moving_timer = 0
        self.color = color
        self.stay_moving_threshold = parameters.stay_moving_threshold
        self.become_moving_threshold = parameters.become_moving_threshold
    
    def updatePosition(self, point):                    
        self.moving_timer -= 1
        if (self.moving and utils.manhattanDistance(self.position,point) >= self.stay_moving_threshold) or (not self.moving and utils.manhattanDistance(self.position,point) > self.become_moving_threshold):
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
        self.num_frames_cooldown = parameters.num_frames_cooldown*10
        self.cooldown_timer = 0
    def ballScored(self, ball):
        self.cooldown_timer -= 1
        if self.cooldown_timer > 0:
            return False
        if not ball.scored and utils.manhattanDistance(ball.position,self.position) < self.max_hole_distance:
            ball.scored = True
            ball.moving = False
            self.cooldown_timer = self.num_frames_cooldown
            return True
        return False
    def invalidDetection(self,detected_circle):
        return self.cooldown_timer > 0 and utils.manhattanDistance(detected_circle.center(), self.position) < self.max_hole_distance
            
class Color(object):
    RED = 0
    WHITE = 1

        
    



    
