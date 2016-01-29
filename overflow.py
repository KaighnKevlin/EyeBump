


import pyttsx

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


        all_balls = balls[Color.RED][:]
        all_balls.extend(balls[Color.WHITE])
        
        
        
                '''
        reader = PoolReader()
        #comment thread
        comment_queue = Queue.Queue()
        t = threading.Thread(target=doComment)
        thread_continue = True
        t.start()
        '''
         #reader = PoolReader(parameters)
       
            if frameNum > 100:#magic
                sendCoords(reader,all_balls)
        reader.drawShots(table_frame,parameters)
        if is_recording:
            for i in range(300):
                out.write(table_frame)       