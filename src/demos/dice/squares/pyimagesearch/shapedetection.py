import cv2
import numpy

class ShapeDetection:
	def __init__(self):
		pass
	def detect(self, c):
		shape = "unidentified"
		peri = cv2.arcLength(c, True)
		approx = cv2.approxPolyDP(c, 0.4 * peri, True)
		#approx contains list of vertices
		if len(approx) == 3:
			shape = "triangle"
		elif len(approx) == 4:
			(x, y, w, h) = cv2.boundingRect(approx)
			ar = w / float(h)
			shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"
			self.detect_circles(c)
		elif len(approx) == 5:
			shape = "pentagon"
		else:
			shape = "circle"
		return shape
	def detect_circles(self, cnt):
		circles = []
		squareimg = img[int(cnt[0][1]):int(cnt[2][1]), int(cnt[0][0]):int(cnt[2][0])]
		circles = cv2.HoughCircles(squareimg, cv2.HOUGH_GRADIENT, dp=1, minDist=squareimg.shape[0]/4, param1=50.0, param2=25.0, minRadius=0, maxRadius=squareimg.shape[0]/4)
		if circles is not None:
			for i in circles[0, :]:
				print i
				cv2.circle(squareimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
				cv2.circle(squareimg, (i[0], i[1]), 2, (0, 0, 255), 3)
	        cv2.imshow("square", squareimg)
	        cv2.waitKey(0)
	    # return circles


	