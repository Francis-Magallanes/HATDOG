import cv2
import numpy as np

radius_pointer = 4

colors = ([0, 255, 0], [0, 0, 255], [255, 0, 0])
# [0,255,0] - black color [0,0,255] - red color [255,0,0]- blue color


def checkforkeyevents(var):
    '''
    this will check for key events
    :param var: the content of the var that constains the ball point info
    :return: character that contains the ball point info
    '''
    key = cv2.waitKey(1) & 0xFF

    if(key == ord('b')):
        return "b"
    elif (key == ord('e')):
        return "e"
    else:
        return var

def manage_statusbar_2(srcimg, pointer_indicator , color):

    tip_string = "Tip: "

    if (pointer_indicator == "b"):
        tip_string += "Ballpen"

    elif (pointer_indicator == "e"):
        tip_string += "Eraser"

    cv2.putText(srcimg, tip_string, (0, 30), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 0, cv2.LINE_AA)

    #this display the color pallete the current color
    if(pointer_indicator == "b"):

        cv2.putText(srcimg, "Color:", (0, 60), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 0), 0, cv2.LINE_AA)

        x = 50
        width = 35
        spacing = 10

        y = 40
        height = 35

        for c in colors:

            if (color[0] == c[0] and color[1] == c[1] and color[2] == c[2]):
                cv2.rectangle(srcimg, (x, y), (x + width, y + height), c, 1)
            else:
                cv2.rectangle(srcimg, (x, y), (x + width, y + height), c, -1)

            x += width + spacing  # updating x for the next value of the x corrdinate

def checkforcolorchange(point, color):
    '''
    this will check if position of the pointer is in the color pallete to change the color
    :param point:farthest point
    :return: boolean and color
    '''

    x = 50
    width = 35
    spacing = 10

    y = 40
    height = 35


    for c in colors:

        if(point[0] > x and point[0] < x + width and point[1] > y and point[1] < y + height):
            return True, c

        x += width + spacing  # updating x for the next value of the x corrdinate

    return False, color

def conversion(srcimage):
    #this method will change the background in the white color to mimick the whiteboard setting
    #it will also change the green into black

    hsv = cv2.cvtColor(srcimage, cv2.COLOR_BGR2HSV)
    lower_green = np.array([25, 52, 15])
    upper_green = np.array([102, 255, 255])
    mask_1 = cv2.inRange(hsv, lower_green, upper_green)
    mask_1_inv = cv2.bitwise_not(mask_1)#making the roi black

    grayscale_whiteboard = cv2.cvtColor(srcimage, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(grayscale_whiteboard, 10, 255, cv2.THRESH_BINARY_INV)#making contents into black

    result_mask = cv2.bitwise_or(mask_1_inv, mask) #getting the roi from the mask
    result_mask_2 = cv2.bitwise_xor(result_mask, mask) # this will remove the roi from the mask
    output = cv2.bitwise_and(srcimage, srcimage, mask=result_mask_2) #putting the contents of image on the mask

    mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    whiteboard_content = cv2.addWeighted(mask, 1, output, 1, 0)

    return whiteboard_content

class Whiteboard():

    def __init__(self, row, col):
        '''
        :param row: the row size for the storage of the markings
        :param col: the column size of the storage of the markings
        '''
        self.__row = row
        self.__col = col
        self.__whiteboard = np.zeros((row, col, 3), np.uint8)
        self.__notwhiteboard = np.zeros((row, col, 3), np.uint8)
        self.__pointer_indicator = "b"
        self.__color_pointer = [0, 255, 0]
        self.__multiplier_radius = 10

    def MarkWhiteboard(self, point, isMarking):

        self.__notwhiteboard = np.zeros((self.__row, self.__col, 3), np.uint8) #this will reset

        self.__pointer_indicator = checkforkeyevents(self.__pointer_indicator)

        _, self.__color_pointer = checkforcolorchange(point, self.__color_pointer)

        if(isMarking):


            if(self.__pointer_indicator == "e"):

                cv2.circle(self.__whiteboard, point , radius_pointer * self.__multiplier_radius, (0,0,0), -1)
                cv2.circle(self.__notwhiteboard , point , radius_pointer * self.__multiplier_radius, (0,255,0), 1)
                cv2.circle(self.__notwhiteboard, point , radius_pointer , (0,255,0) , 1)
            else:

                cv2.circle(self.__whiteboard , point , radius_pointer , self.__color_pointer , -1)

        else:
            #this will indicate the pointer will not mark
            width = 2 * radius_pointer
            height = 2 * radius_pointer

            if (self.__pointer_indicator == "e"):

                cv2.circle(self.__notwhiteboard, point, radius_pointer * self.__multiplier_radius, (0, 255, 0), -1)
                cv2.circle(self.__notwhiteboard, point, radius_pointer, (0, 255, 0), 1)

            else:

                cv2.rectangle(self.__notwhiteboard, ( int(point[0] - (width/2)) , int(point[1] - (height/2))) , ( int(point[0] + (width/2)) ,int(point[1] + (height/2)))
                              , self.__color_pointer, -1)

        manage_statusbar_2(self.__notwhiteboard, self.__pointer_indicator, self.__color_pointer)
        merged = cv2.addWeighted(self.__notwhiteboard ,1, self.__whiteboard , 1 ,1 )

        whiteboard_content = conversion(merged)

        return whiteboard_content

    def ClearMarkings(self):
        self.__whiteboard = np.zeros((self.__row, self.__col, 3), np.uint8)
