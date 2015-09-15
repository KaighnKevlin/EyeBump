 import pyttsx

class ShotCommenter():
    def __init__(self):
        self.engine = pyttsx.init()
    def comment(self, ball_id):
        self.printAndSayString("Ball "+str(ball_id)+" was shot.")
    def printAndSayString(self, str):
        print str
        self.engine.say(str)
        self.engine.runAndWait()
        
class ShotReader(object):
    def __init__(self):
        self.balls = [Ball2(i) for i in range(10)]
        #self.commenter = ShotCommenter()
    def read(self, shot_dict):
        #print 'reading shot...',[len(value) for key,value in shot_dict.items()]
        if min([len(value) for value in shot_dict.values()]) < 3:
            return
        else:
            shot_ball_id = self.firstBall(shot_dict)
            #print shot_dict.keys()
            #comment_queue.put("Ball "+str(shot_ball_id)+" was shot.")
            #self.commenter.comment(shot_ball_id)
            self.analyzeShot(shot_dict[shot_ball_id])
    def analyzeShot(self, position_history):
        if position_history[0][0] < 40:
            print 'less than forty'
        banked = False
        for x,y in position_history:
            if banked:
                'print banked'
            if y > 190:
                print '>190'
                banked = True
        print '\n\n\n'
        
    def firstBall(self,shot_dict):
        for ball_id, position_history in shot_dict.items():
            if distance(position_history[0],position_history[1]) >= 5:
                #print 'movement: ball ' + str(ball_id)
                return ball_id
                
        #print 'no movement???????????????????\n\n\n\n\n\n\n\nwhhhhhhhhhhhhhhhhhhhhhaaaaaaaaaaaaaaaaaaattttttttttttttttttttt\n\n\n\n\n\n\n\n'
        return 1012345678901234567890
        
        