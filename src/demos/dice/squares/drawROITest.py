import cv2
import numpy as np
 
if __name__ == '__main__' :
 
    # Read image
    im = cv2.imread("detect_blob.png")
     
    # Select ROI
    r = cv2.selectROI(im)
     
    # Crop image
    # r = [72, 100, 135, 118]
    #      x1  y1  x2-x1 y2-y1
    imCrop = im[int(r[1]):int(r[1]+r[3]), int(r[0]):int(r[0]+r[2])]
    #				y1     y2              x1        x2
    print(r)
    # Display cropped image
    cv2.imshow("Image", imCrop)
    cv2.waitKey(0)