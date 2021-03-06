import numpy as np

min_area = 100
max_area = 1000
max_ball_radius = 30
min_area_to_radius_sqaured_ratio = 1
drawn_circle_radius = 16
max_hole_distance = 7
stay_moving_threshold = 1
become_moving_threshold = 10
num_frames_cooldown = 100
debug = False

#red_range = np.array([[[158,90,66],[186,255,255]]])
#white_range = np.array([[[11,50,125],[47,133,255]]])
red_range = np.array([[[0,104,104],[11,255,255]]])
white_range = np.array([[[0,0,182],[176,84,255]]])

hole_1 = np.array([236,397])
hole_2 = np.array([267,7])               
