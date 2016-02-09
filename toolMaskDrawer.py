'''
Tool to draw a mask to mask out parts of the image that aren't the bumper pool table. Adapted from an opencv tutorial.
'''
import cv2
import numpy as np
import sys

drawing = False # true if mouse is pressed
mode = 0 # if True, draw rectangle. Press 'm' to toggle to curve
ix,iy = -1,-1
img = np.zeros((512,512,3), np.uint8)


# mouse callback function
def draw_circle(event,x,y,flags,param):
    global ix,iy,drawing,mode,img
    mod = mode % 3
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:

            if mod == 0:
                cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
            elif mod == 1:
                cv2.circle(img,(x,y),10,(0,255,0),-1)


    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mod == 0:
            cv2.rectangle(img,(ix,iy),(x,y),(0,255,0),-1)
        elif mod == 1:
            cv2.circle(img,(x,y),10,(0,255,0),-1)
        elif mod == 2:
            print 'clicked point:',(x,y)
def make_mask(img):
    lower = np.array([0,255,0])
    upper = np.array([0,255,0])

    mask = cv2.inRange(img, lower, upper)
    invertMask = cv2.bitwise_not(mask)
    res = cv2.bitwise_and(img, img, mask=invertMask)
    cv2.imshow('mask',invertMask)
    cv2.imshow('res', res)
    
    return invertMask
    
    
    cv2.waitKey(0)

def main(img_path,image=None,mask_path_prefix=None):
    global img, mode
    if image == None:
        img = cv2.imread(img_path)
    else:
        img = image
    cv2.namedWindow('image')
    cv2.setMouseCallback('image',draw_circle)

    while(1):
        cv2.imshow('image',img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('m'):
            mode +=1
        if k == ord('d'):
            mask = make_mask(img)
            if mask_path_prefix != None:
                cv2.imwrite('masks/'+mask_path_prefix+'-mask.png',mask)
            cv2.destroyAllWindows()
            return mask
        elif k == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print 'invalid number of arguments'
        sys.exit()
    main(sys.argv[1],sys.argv[2])