import cv2
import numpy as np
import sys
import math

def hand_histogram(frame):
    #this function will create a histogram from the rectangle regions displayed in the screen
    global hand_rect_one_x, hand_rect_one_y

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    roi = np.zeros([90, 10, 3], dtype=hsv_frame.dtype)

    for i in range(total_rectangle):
        roi[i * 10: i * 10 + 10, 0: 10] = hsv_frame[hand_rect_one_x[i]:hand_rect_one_x[i] + 10,
                                          hand_rect_one_y[i]:hand_rect_one_y[i] + 10]

    hand_hist = cv2.calcHist([roi], [0, 1], None, [180, 256], [0, 180, 0, 256])

    return cv2.normalize(hand_hist, hand_hist, 0, 255, cv2.NORM_MINMAX)

def hist_masking(frame, hist):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    dst = cv2.calcBackProject([hsv], [0, 1], hist, [0, 180, 0, 256], 1)

    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    cv2.filter2D(dst, -1, disc, dst)

    ret, thresh = cv2.threshold(dst, 150, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=7)

    thresh = cv2.merge((thresh, thresh, thresh))

    return cv2.bitwise_and(frame, thresh)

def drawContours(imgsrc, imgPart):

    grayimage = cv2.cvtColor(imgPart,cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(grayimage, 0, 255, 0)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(imgsrc, contours, -1, (0, 255, 0), 3)

def draw_circles(frame, traverse_point):
    if traverse_point is not None:
        for i in range(len(traverse_point)):
            cv2.circle(frame, traverse_point[i], int(5 - (5 * i * 3) / 100), [0, 255, 255], -1)

def centroid(max_contour):
    moment = cv2.moments(max_contour)
    if moment['m00'] != 0:
        cx = int(moment['m10'] / moment['m00'])
        cy = int(moment['m01'] / moment['m00'])
        return cx, cy
    else:
        return None

def farthest_point(defects, contour, centroid):
    if defects is not None and centroid is not None:
        s = defects[:, 0][:, 0]
        cx, cy = centroid

        x = np.array(contour[s][:, 0][:, 0], dtype=np.float)
        y = np.array(contour[s][:, 0][:, 1], dtype=np.float)

        xp = cv2.pow(cv2.subtract(x, cx), 2)
        yp = cv2.pow(cv2.subtract(y, cy), 2)
        dist = cv2.sqrt(cv2.add(xp, yp))

        dist_max_i = np.argmax(dist)

        if dist_max_i < len(s):
            farthest_defect = s[dist_max_i]
            farthest_point = tuple(contour[farthest_defect][0])
            return farthest_point
        else:
            return None

def max_contour(contour_list):
    max_i = 0
    max_area = 0

    for i in range(len(contour_list)):
        cnt = contour_list[i]

        area_cnt = cv2.contourArea(cnt)

        if area_cnt > max_area:
            max_area = area_cnt
            max_i = i

    if(len(contour_list) == 0):
        return None
    else:
        return contour_list[max_i]

def contours(hist_mask_image):
    gray_hist_mask_image = cv2.cvtColor(hist_mask_image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray_hist_mask_image, 0, 255, 0)
    cont, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return cont

def resizeImage(img,percentscale):

    width = int(img.shape[1] * percentscale / 100)
    height = int(img.shape[0] * percentscale / 100)
    dim = (width, height)
    # resize image
    return cv2.resize(img, dim, interpolation=cv2.INTER_AREA)

class HandTrack:
    isThereHandHist = False

    def DisplayRectForSampling(self, frame):
        # the purpose of the method is to draw rectangle that will indicate the user will place there hand at the rectangles
        global total_rectangle, hand_rect_one_x, hand_rect_one_y, hand_rect_two_x, hand_rect_two_y
        total_rectangle = 9
        rows, cols, _ = frame.shape

        total_rectangle = 9

        hand_rect_one_x = np.array(
            [6 * rows / 20, 6 * rows / 20, 6 * rows / 20, 9 * rows / 20, 9 * rows / 20, 9 * rows / 20, 12 * rows / 20,
             12 * rows / 20, 12 * rows / 20], dtype=np.uint32)

        hand_rect_one_y = np.array(
            [9 * cols / 20, 10 * cols / 20, 11 * cols / 20, 9 * cols / 20, 10 * cols / 20, 11 * cols / 20,
             9 * cols / 20,
             10 * cols / 20, 11 * cols / 20], dtype=np.uint32)

        hand_rect_two_x = hand_rect_one_x + 10
        hand_rect_two_y = hand_rect_one_y + 10

        for i in range(total_rectangle):
            cv2.rectangle(frame, (hand_rect_one_y[i], hand_rect_one_x[i]),
                          (hand_rect_two_y[i], hand_rect_two_x[i]),
                          (0, 255, 0), 1)

        return frame

    def GetHandSample(self, frame):
        self.handHist = hand_histogram(frame)
        self.isThereHandHist = True

    def getIsThereHandHist(self):
        return self.isThereHandHist

    def ExecuteHandTrack(self, frame):
        bgSubtractor = cv2.createBackgroundSubtractorMOG2(history=5, varThreshold=20, detectShadows=False)

        hist_mask_image = hist_masking(frame, self.handHist)

        contour_list = contours(hist_mask_image)

        max_cont = max_contour(contour_list)

        if max_cont is None:
            return False, None
        else:
            cnt_centroid = centroid(max_cont)
            hull = cv2.convexHull(max_cont, returnPoints=False)
            defects = cv2.convexityDefects(max_cont, hull)
            far_point = farthest_point(defects, max_cont, cnt_centroid)
            return True, far_point
