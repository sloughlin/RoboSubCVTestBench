#!/usr/bin/env python

'''
Simple "Square Detector" program.

Loads several images sequentially and tries to find squares in each image.
'''

# Python 2/3 compatibility
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import argparse


def angle_cos(p0, p1, p2):
    d1, d2 = (p0-p1).astype('float'), (p2-p1).astype('float')
    return abs( np.dot(d1, d2) / np.sqrt( np.dot(d1, d1)*np.dot(d2, d2) ) )

def find_circles(img, cnt):
    #find circles within square contours
    circles = []
    squareimg = img[int(cnt[0][1]):int(cnt[2][1]), int(cnt[0][0]):int(cnt[2][0])]
    # cv2.imshow("square", squareimg)
    # cv2.waitKey(0)
    circles = cv2.HoughCircles(squareimg, cv2.HOUGH_GRADIENT, dp=1, minDist=squareimg.shape[0]/2, param1=50.0, param2=25.0, minRadius=0, maxRadius=0)
    # move circles to correct places in original image
    if circles is not None:
        for i in range(len(circles)):
            if circles[i] is not None:
                for j in range(len(circles[i])):
                    #Add x coord of top left corner of square to x coord of circle center
                    circles[i][j][0] += cnt[0][0]
                    #Add y coord of top left corner of square to y coord of circle center
                    circles[i][j][1] += cnt[0][1]
    #print(circles)
    # if circles is not None:
    #     for i in circles[0, :]:
    #         #print i
    #         cv2.circle(squareimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
    #         cv2.circle(squareimg, (i[0], i[1]), 2, (0, 0, 255), 3)
    #     cv2.imshow("square", squareimg)
    #     cv2.waitKey(0)
    return circles


def find_squares(img):
    img = cv2.GaussianBlur(img, (5, 5), 0)
    squares = []
    circles = [] #list of lists, lines up w squares (ideally...)
    for gray in cv2.split(img):
        # cv2.imshow("gray",gray)
        # cv2.waitKey(0)
        for thrs in xrange(0, 255, 26):
            if thrs == 0:
                bin = cv2.Canny(gray, 0, 50, apertureSize=5)
                bin = cv2.dilate(bin, None)
            else:
                retval, bin = cv2.threshold(gray, thrs, 255, cv2.THRESH_BINARY)
            # cv2.imshow("thresh",bin)
            # cv2.waitKey(0)
            bin, contours, hierarchy = cv2.findContours(bin, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            for cnt in contours:
                cnt_len = cv2.arcLength(cnt, True)
                cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
                if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt):
                    cnt = cnt.reshape(-1, 2)
                    if cnt[0][0] == 0 and cnt[0][1] == 0:
                        #shitty way to not get a box w the whole image
                        break;
                    max_cos = np.max([angle_cos( cnt[i], cnt[(i+1) % 4], cnt[(i+2) % 4] ) for i in xrange(4)])
                    if max_cos < 0.1:
                        squares.append(cnt)
                        # print(cnt)
                        #if square found, look for circles in it
                        c = find_circles(bin, cnt)
                        if c is not None:
                            circles.append(c)

    return squares, circles

if __name__ == '__main__':
    from glob import glob
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--image", required=True, help="path to the input image")
    args = vars(ap.parse_args())
    for fn in glob(args["image"]):
        img = cv2.imread(fn)
        squares, circles = find_squares(img)
        cv2.drawContours( img, squares, -1, (0, 255, 0), 3 )
        numcircles = 0
        if circles is not None:
            #print(circles)
            for i in range(0,len(circles)):
                if circles[i] is not None:
                    numcircles += 1
                    for j in range(0,len(circles[i])):
                        if circles[i][j] is not None:
                            for k in range(len(circles[i][j])):
                                curr = circles[i][j][k];
                                cv2.circle(img, (curr[0], curr[1]), curr[2], (0, 255, 0), 2)
                                cv2.circle(img, (curr[0], curr[1]), 2, (0, 0, 255), 3)
                                #cv2.putText(img, str(numcircles), (curr[0],curr[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        print(len(squares))
        cv2.imshow('squares', img)
        ch = cv2.waitKey()
        if ch == 27:
            break
    cv2.destroyAllWindows()
