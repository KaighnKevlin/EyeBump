import cv2
import traceback, sys
import importlib
import utils

from detect import Detector
from state import State
from track import Tracker
import automation
 
def main(video_path, debug, recording_path):
    mask_path = "masks/will1-mask.png"
    parameters = importlib.import_module("parameters.will1")
    is_recording = recording_path != None
    
    
    if not parameters.debug:
        parameters.debug = debug
    try:
        if is_recording:
            cap = cv2.VideoCapture(-1)
        else:
            cap = cv2.VideoCapture(video_path)
        
        ret,frame = None,None
        for i in range(256): #magic
            ret, frame = cap.read()
        parameters.red_range,parameters.white_range = automation.findColorRanges(frame,debug)
        table_frame = frame.copy()
        if is_recording:
            out = cv2.VideoWriter(recording_path+".avi",-1, 30.0, (len(frame[0]),len(frame)))##magic
        frameNum = 0
        bumper_mask = cv2.imread(mask_path, 0)
        
        detector = Detector(bumper_mask,parameters)
        state = State(parameters)
        tracker = Tracker(state)
        
        while(cap.isOpened()):
            ret, frame = cap.read()	
            frameNum += 1
            if frameNum < 50:#magic
                continue
            final_display_frame = frame.copy()
            detected_circles = detector.detect(frame)
            tracker.track(detected_circles)
            state.scoreBalls()
            if state.gameIsOver():
                break
            state.draw(final_display_frame) 
            if is_recording:
                out.write(final_display_frame)
                utils.imshow('frame',final_display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
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

    
if __name__ == "__main__":
    args = sys.argv[1:]
    debug = False
    recording_path = None
    if '-h' in args:
        print "arguments: video_path" 
        print "Example: python main.py videos/will_table_1.avi"
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
    if len(args) != 1:
        raise ValueError("Invalid number of arguments.")
    main(sys.argv[1],debug,recording_path)
