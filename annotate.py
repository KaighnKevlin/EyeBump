from detect import Detector
import toolMaskDrawer
import automation
import sys
import cv2
import importlib
from state import State,Color
import utils

frame = None
id = None
state = None
current_positions = None
text_file = None
auto_recalc = False
def annotate(cap,text_file_path):
    frameNum = 0
    cap.read()
    _, first_frame = cap.read()
    mask = toolMaskDrawer.main('',image=first_frame)
    
    #need to massively change below lines
    parameters = importlib.import_module("parameters.will1")
    #parameters.red_range,parameters.white_range = automation.findColorRanges(first_frame,debug=True)
    detector = Detector(mask,parameters)
    global state
    state = State(parameters)
    global current_positions
    current_positions = {i:(-1,-1) for i in range(10)}
    global text_file
    text_file = open(text_file_path,"w")
    
    
    circles = detector.detect(first_frame)
    for color in [Color.RED,Color.WHITE]:
        colored_circles = sorted(circles[color], key=lambda c: c.x)#copied code from tracker v3

        balls = state.red_balls if color == Color.RED else state.white_balls
        for i,ball in enumerate(balls):
            ball.updatePosition(colored_circles[i].center())
            
    while(cap.isOpened()):
        global frame
        ret, frame = cap.read()	
        frameNum += 1
        state.draw(frame.copy(),frame_number=frameNum)
        if not handleInput(detector):
            break
        write(frameNum,state.ballsState())
    cv2.destroyAllWindows()
def handleInput(detector):
    while(True):
        k = cv2.waitKey(0)
        if k == ord('m'):           
            cv2.setMouseCallback('final',draw_circle)
        if k == ord('r'):
            cv2.setMouseCallback('final',no_callback)
            global id
            circles_d = detector.detect(frame)
            circles = circles_d[Color.RED] if id < 5 else circles_d[Color.WHITE]
            circles_dists = [utils.manhattanDistance(c.center(),state.getBall(id).position) for c in circles]
            match = circles[circles_dists.index(min(circles_dists))]
            state.getBall(id).updatePosition(match.center())
            redraw()
        if k == ord('g'):
            cv2.setMouseCallback('final',no_callback)
            return True
        if k == ord('s'):
            global id
            id = cv2.waitKey(0)
            while(id < 48 or id > 57):
                id = cv2.waitKey(0)
            id = int(chr(id))
        if k == 33:#!
            text_file.close()
            return False
                
def write(frame_num, ball_positions):
    first = True
    for i in range(10):
        if utils.manhattanDistance(ball_positions[i],current_positions[i]) != 0:
            if first:
                first = False
                text_file.write(str(frame_num)+':')
            else:
                text_file.write("|")
            ball_pos_split = str(ball_positions[i]).split()
            ball_coordinates = ball_pos_split[0]+ball_pos_split[1]
            text_file.write(str(i)+"^"+ball_coordinates)
            print str(frame_num),str(i),"^",ball_coordinates
            current_positions[i] = ball_positions[i]
    if not first:
        text_file.write('\n')
            
            
def no_callback(event,x,y,flags,param):
    pass
def draw_circle(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global state, id
        ball = state.getBall(id)
        ball.updatePosition((x,y))
        redraw()
def redraw():
    new_frame = frame.copy()
    state.draw(new_frame)
    cv2.imshow('final',new_frame)
def getFileName(video_path):
    name = video_path.split('.')[0]
    if '/' in list(name):
        name = name.split('/')[1]
    return "annotations/"+name+".txt"

if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        raise ValueError("Invalid number of arguments.")
    cap = cv2.VideoCapture(args[0])
    annotate(cap,getFileName(args[0]))