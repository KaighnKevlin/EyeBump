import numpy as np

def distance(p1,p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) 
def manhattanDistance(p1,p2):
    return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
def getIntTuple(float_tuple):
    return (int(float_tuple[0]),int(float_tuple[1]))