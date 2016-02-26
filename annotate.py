from detect import Detector
import toolMaskDrawer
import automation
import sys
import cv2
import importlib
from state import State,Color
import utils
import read_annotation

class BallInfo(object):
    def __init__(self,ball):
        self.ball = ball
        self.position = ball.position
        self.hidden = False
    def flagged(self):
        ret = utils.manhattanDistance(self.position,self.ball.position) != 0 or self.hidden != self.ball.hidden
        self.position = self.ball.position
        self.hidden = self.ball.hidden
        return ret
    def getWrite(self):
        hidden = "H" if self.ball.hidden else ""
        return str(self.ball.id)+"^"+str(self.ball.getPositionInts())+ hidden


frame = None
frameNum = None
id = None
state = None
detector = None
cont = False
ball_infos = None
text_file = None
auto_recalc = False
def annotate(cap,text_file_path):
    global frameNum
    frameNum = 0
    cap.read()
    _, first_frame = cap.read()
    mask = toolMaskDrawer.main('',image=first_frame)
    
    #need to massively change below lines
    parameters = importlib.import_module("parameters.will1")
    #parameters.red_range,parameters.white_range = automation.findColorRanges(first_frame,debug=True)
    global detector
    detector = Detector(mask,parameters)
    global state
    state = State(parameters)
    #global current_positions
    #current_positions = {i:(-1,-1) for i in range(10)}
    global ball_infos
    ball_infos = [BallInfo(state.getBall(i)) for i in range(10)]
    global text_file
    initial_frameNum = 0
    if cont:
        read_file = open(text_file_path,"r")
        remember_line = ''
        d = {}
        while(True):
            line = read_file.readline()
            if line == '':
                break
            remember_line = line
            _, d = read_annotation.processLine(line)
            for k,v in d.items():
                print k,v
                ball_infos[k].ball.position = v
                ball_infos[k].position = v
        initial_frameNum = int(remember_line.split(':')[0])
        text_file = open(text_file_path,"a")
    else:
        text_file = open(text_file_path,"w")
    
    
    circles = detector.detect(first_frame)
    if not cont:
        for color in [Color.RED,Color.WHITE]:
            colored_circles = sorted(circles[color], key=lambda c: c.x)#copied code from tracker v3

            balls = state.red_balls if color == Color.RED else state.white_balls
            for i,ball in enumerate(balls):
                if i >= len(colored_circles):
                    break
                ball.position = colored_circles[i].center()
    while(initial_frameNum!=frameNum):
        ret,frame = cap.read()
        frameNum+=1
    while(cap.isOpened()):
        global frame, frameNum
        ret, frame = cap.read()	
        frameNum += 1
        redraw()
        if not handleInput():
            break
        write()
    cv2.destroyAllWindows()
def handleInput():
    cv2.setMouseCallback('final',draw_circle)
    global id, auto_recalc
    for i in range(10):
        ball = state.getBall(i)
        ball.updatePosition(ball.position)
    if id != None and auto_recalc:
        recalc(id)
    while(True):
        k = cv2.waitKey(0)
        if k == ord('r'):
            auto_recalc = not auto_recalc
            #cv2.setMouseCallback('final',no_callback)
        if k == ord('f'):
            recalc(id)
        if k == ord('u'):
            state.drawn_circle_radius += 1
        if k == ord('d'):
            if state.drawn_circle_radius <= 0:
                continue
            state.drawn_circle_radius -= 1
        if k == ord('g'):
            #cv2.setMouseCallback('final',no_callback)
            redraw()
            return True
        if k == ord('h'):
            ball = state.getBall(id)
            ball.hidden = not ball.hidden
        if k >= 48 and k <= 57:
            global id
            id = int(chr(k))
        if k == 33:#!
            text_file.close()
            return False
        redraw()
def write():
    first = True
    for info in ball_infos:
        if info.flagged():
            if first:
                first = False
                text_file.write(str(frameNum)+':')
            else:
                text_file.write("|")
            print str(frameNum)+":"+info.getWrite()
            text_file.write(info.getWrite())
    if not first:
        text_file.write('\n')         

def no_callback(event,x,y,flags,param):
    pass
def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global state, id
        ball = state.getBall(id)
        ball.position = (x,y)
        redraw()
def redraw():
    new_frame = frame.copy()
    global frameNum
    state.draw(new_frame,frame_number=frameNum,line_width=1)
    cv2.imshow('final',new_frame)
def recalc(ball_id):
    global detector
    circles_d = detector.detect(frame)
    circles = circles_d[Color.RED] if ball_id < 5 else circles_d[Color.WHITE]
    circles_dists = [utils.manhattanDistance(c.center(),state.getBall(ball_id).position) for c in circles]
    match = circles[circles_dists.index(min(circles_dists))]
    state.getBall(ball_id).position = match.center()
    redraw()
def getFileName(video_path):
    name = video_path.split('.')[0]
    if '/' in list(name):
        name = name.split('/')[1]
    return "annotations/"+name+".txt"

if __name__ == "__main__":
    args = sys.argv[1:]
    if '-c' in args:
        args.remove('-c')
        cont = True
    if len(args) != 1:
        raise ValueError("Invalid number of arguments.")
    cap = cv2.VideoCapture(args[0])
    annotate(cap,getFileName(args[0]))