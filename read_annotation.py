from detect import Detector
import toolMaskDrawer
import automation
import sys
import cv2
import importlib
from state import State,Color
import utils
import annotate

def main(video_path):
    file = open(annotate.getFileName(video_path))


    cap = cv2.VideoCapture(video_path)
    frameNum = 0
    cap.read()
    _, first_frame = cap.read()
    next_frame = 0
    ball_positions = None
    file_done = False
    parameters = importlib.import_module("parameters.will1")
    state = State(parameters)
    
    line = file.readline()
    next_frame,ball_positions = processLine(line)
    while(cap.isOpened()):
        frameNum += 1
        _, frame = cap.read()
        if frameNum >= next_frame and not file_done:
            if line == '':
                file_done = True
            if not file_done:
                utils.updateBallPositions(state,ball_positions)
                next_frame,ball_positions = processLine(line)
            line = file.readline()

        state.draw(frame,frame_number=frameNum)
        cv2.imshow('final',frame)
        if cv2.waitKey(0) == ord('q'):
            break
def processLine(line):
    d = {}

    linesplit = line.split(":")
    frameNum = int(linesplit[0])
    ball_positions = linesplit[1]
    ball_list = ball_positions.split("|")
    for ball_info in ball_list:
        ballsplit = ball_info.split("^")
        ball_num = int(ballsplit[0])
        coordinates_string = ballsplit[1].split(",")
        if 'H' in coordinates_string[1]:
            coordinates_string[1] = coordinates_string[1][:len(coordinates_string[1])-1]
        ball_pos = (int(coordinates_string[0][1:]),int(coordinates_string[1][:len(coordinates_string[1].strip('\n'))-1]))
        d[ball_num] = ball_pos
    return frameNum,d
    
    
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) != 1:
        raise ValueError("Invalid number of arguments.")
    main(args[0])