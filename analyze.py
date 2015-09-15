#####################pool reader
from ballTracker import Color
import cv2
import utils
'''
-katsiss
-wrong hole
-new age
-bump
'''

class PoolReader(object):
    def __init__(self, parameters):
        self.balls = [Ball(i,Color.RED) for i in range(5)]
        self.balls.extend([Ball(i,Color.WHITE) for i in range(5,10)])
        self.frameNum = 0
        self.shot_summaries = []
        self.hole_positions = [parameters.hole_1, parameters.hole_2]
    def read(self, positions, movings):
        if not any(movings):
            self.__cut()
            self.frameNum = 0
            for i in range(len(positions)):
                if not movings[i]:
                    self.balls[i].updateOldPosition(positions[i])
        else:
            for i in range(len(positions)):
                if movings[i]:
                    self.balls[i].updatePosition(self.frameNum,positions[i], movings[i])
            self.frameNum += 1
    def ballScored(self, ball_id):
        self.balls[ball_id].scored = True
    def getShotSummaries(self):
        return self.shot_summaries
    def __cut(self):
        if max([len(ball.position_history.frames) for ball in self.balls]) == 0:
            return
        moved_balls = [ball for ball in self.balls if len(ball.position_history.frames) > 0]  
        self.__analyzeHistories(moved_balls)
        for ball in self.balls:
            ball.clearHistory()
    def __analyzeHistories(self,moved_balls):
        shot_ball = self.__ballShot(moved_balls)
        starting_point = shot_ball.old_history.frames[0].ball_position
        self.shot_summaries.append(ShotSummary(shot_ball, starting_point,shot_ball.scored))
        self.__analyzeHistory(shot_ball)
    def __analyzeHistory(self,ball):
        print 'analyzing history!'
        frames = ball.position_history.frames
        #print frames
        for frame in frames:
            x,y = frame.ball_position
            if y >= 275:
                pass
                #print 'below white new age threshold'
            if x <= 70:
                pass
                #print 'bounced off right cushion'
            if utils.manhattanDistance((x,y),self.hole_positions[0]) < 40:
                pass
                #print utils.manhattanDistance((x,y),self.hole_positions[0])
               
            
    def __ballShot(self,moved_balls):
        for ball in moved_balls:
            if ball.position_history.frames[0].frameNum == 0:
                return ball
    def drawShots(self,draw_frame,parameters):
        color_dict = {
            Color.RED : (0,0,255),
            Color.WHITE : (255,255,255)
        }
        for shot in self.shot_summaries:
            #cv2.putText(table_frame,'x',getIntTuple(scoring_position), cv2.FONT_HERSHEY_SIMPLEX, .7,color_dict[getColor(ball_id,all_balls)],2,cv2.LINE_AA)
            if shot.was_scored:
                draw_frame = cv2.circle(draw_frame,utils.getIntTuple(shot.starting_point),parameters.drawn_circle_radius,color_dict[shot.ball.color],2)
            else:
                draw_frame = cv2.circle(draw_frame,utils.getIntTuple(shot.starting_point),parameters.drawn_circle_radius/3,color_dict[shot.ball.color],2)
        cv2.imshow('shot chart', draw_frame)
        cv2.waitKey(0)
class Ball(object):
    def __init__(self, id, color):
        self.id = id
        self.position_history = History(id)
        self.old_history = History(id)
        self.moving = False
        self.scored = False
        self.color = color
    def updatePosition(self,frameNum,pos,is_moving):
        self.moving = is_moving
        self.position_history.addFrame(Frame(frameNum,pos))
    def updateOldPosition(self,pos):
        if len(self.old_history.frames) >= 5:#magic
            self.old_history.frames.pop(0)
        self.old_history.addFrame(Frame(-1,pos))
    def clearHistory(self):
        self.position_history.clear()
class History(object):
    def __init__(self, ball_id):
        self.ball_id = ball_id
        self.frames = []
    def addFrame(self,frame):
        self.frames.append(frame)
    def clear(self):
        self.frames[:] = []
        
class Frame:
    def __init__(self, frameNum, ball_position):
        self.frameNum = frameNum
        self.ball_position = ball_position

class ShotSummary:
    def __init__(self, ball, starting_point, was_scored):
        self.ball = ball
        self.starting_point = starting_point
        self.was_scored = was_scored
#####################


def doComment():
    engine = pyttsx.init()
    while(not gameIsOver() and thread_continue):
        if not comment_queue.empty():
            comment = comment_queue.get()
            engine.say(comment)
            engine.runAndWait()
        else:
            time.sleep(.3)
    engine.say("Game over.")
    engine.runAndWait()