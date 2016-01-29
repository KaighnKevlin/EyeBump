from state import Color
import utils

class Tracker(object):
    def __init__(self, state):
        self.state = state
        self.initialized = False
    def track(self,detected_circles):
        for color in [Color.RED,Color.WHITE]:
            self.__trackColor(detected_circles,color)
        self.initialized = True
    def __trackColor(self,detected_circles,color):
        circles = detected_circles[color]
        circles = [c for c in circles if self.state.validDetection(c)]
        balls = self.state.red_balls if color == Color.RED else self.state.white_balls
        if not self.initialized:
            Tracker.__initializeBallPositions(balls,circles)
        Tracker.__findMatchings(circles, balls) 
    @staticmethod
    def __initializeBallPositions(balls, circles):
        circles = sorted(circles, key=lambda c: c.x)#magic
        for i,ball in enumerate(balls):
            ball.updatePosition(circles[i].center())
    @staticmethod
    def __getBallClosestToPoint(point, available_balls):
        min = 1000
        for ball in available_balls:
            dist = utils.manhattanDistance(ball.position, point)
            if(dist < min): 
                best_ball = ball
                min = dist
        return min,best_ball
    @staticmethod   
    def __getCircleClosestToBall(ball, circles):
        min = 1000
        for circle in circles:
            dist = utils.manhattanDistance(ball.position,circle.center())
            if(dist < min): 
                best_circle = circle
                min = dist
        return best_circle,min
    @staticmethod
    def __findMatchings(circles_to_be_matched, balls):
        balls_in_play = [ball for ball in balls if not ball.scored]
        balls_is_matched = {}
        for ball in balls_in_play:
            balls_is_matched[ball] = False
        unmatched_circles = []
        
        #find close matchings
        for circle_id,circle in enumerate(circles_to_be_matched):
            center = circle.intCenter()
            min,closest_ball = Tracker.__getBallClosestToPoint(center, balls_in_play)
            if min < 10: #really? match 1st one < 10? #magic
                closest_ball.vanished_frames = 0
                balls_is_matched[closest_ball] = True
                closest_ball.updatePosition(circle.center())
            else:
                unmatched_circles.append(circle)
        
        #check vanished balls
        vanished_balls = [ball for ball in balls_in_play if not balls_is_matched[ball]]
        ball_to_circle = {}
        for ball in vanished_balls:
            ball.vanished_frames += 1
            if len(unmatched_circles) >= 1:
                ball_to_circle[ball] = Tracker.__getCircleClosestToBall(ball, unmatched_circles)
        ball_circle_pairs = ball_to_circle.items()
        #print ball_circle_pairs
        ball_circle_pairs.sort(key=lambda x:x[1][1])
        for ball, circle in ball_circle_pairs:
            circle = circle[0]
            if circle in unmatched_circles:
                if utils.manhattanDistance(ball.position, circle.center()) < ball.vanished_frames * 60:
                    ball.updatePosition(circle.center())
                    unmatched_circles.remove(circle)
            
