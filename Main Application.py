import cv2
import numpy as np
import HandTrack as ht
import WhiteBoard as wb
from tkinter import *

def manage_statusbar_1(srcimg, isGettingSample , isMarking , isRecording):

    status_string = "Status: "

    if(isGettingSample):
        status_string += "-Getting Sample"
    else:
        status_string += "-Tracking"

        if (isMarking):
            status_string += "-Marking"
        else:
            status_string += "-No Marking"

    if (isRecording):
        status_string += "-Recording"
    else:
        status_string += "-No Recording"


    cv2.putText(srcimg, status_string , (0,15) , cv2.FONT_HERSHEY_PLAIN , 0.8 , (0,255,0) , 1 ,cv2.LINE_AA)

def ExecuteApplication():

    cv2.namedWindow("Hand Acknowledgement and Tracking that Documents and Overwrite Graphics", cv2.WINDOW_KEEPRATIO)
    cv2.namedWindow("Whiteboard", cv2.WINDOW_KEEPRATIO)


    root.destroy()
    handTrackObj = ht.HandTrack()

    cap = cv2.VideoCapture(0)

    #initialization of the marking object
    _, frame_first = cap.read()
    row, column,_ = frame_first.shape
    whiteboardObj = wb.Whiteboard(row,column)

    #initialization of the video writing
    video_writer = cv2.VideoWriter('recorded session.avi', cv2.VideoWriter_fourcc(*'XVID') , 15.0 , (column , row))

    isMarking = False
    isRecording = False

    while (True):

        # it will break the loop if one of the windows is closed by x button
        if (cv2.getWindowProperty('Hand Acknowledgement and Tracking that Documents and Overwrite Graphics',
                                  4) == -1
                or cv2.getWindowProperty("Whiteboard", 4) == -1):
            break

        # Capture frame-by-frameq
        ret, frame = cap.read()

        cv2.flip(frame, 1, frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        elif key == ord('g') :
            if(not handTrackObj.getIsThereHandHist()):
                handTrackObj.GetHandSample(frame)
                cv2.destroyWindow("Hand Acknowledgement and Tracking that Documents and Overwrite Graphics")

        elif key == ord('s'):
            isMarking = not isMarking

        elif key == ord('r'):
            if(handTrackObj.getIsThereHandHist()):
                isRecording = not isRecording

        elif key == ord('c'):
            whiteboardObj.ClearMarkings()

        if (handTrackObj.getIsThereHandHist()):
            isTherePoint, point = handTrackObj.ExecuteHandTrack(frame) #Execute HandTracking, it will return boolean whether there is farthest point. If there is,
                                                                      # it will return coordinates of the farthest point

            cv2.circle(frame, point , 5,(0,255,0) , -1) #this will mark the pointer in the hand tracking window
            manage_statusbar_1(frame, False, isMarking, isRecording)

            if(isTherePoint and point is not None):
                whiteboard = whiteboardObj.MarkWhiteboard(point , isMarking)
                cv2.imshow("Whiteboard", whiteboard)
                cv2.imshow("Hand Acknowledgement and Tracking that Documents and Overwrite Graphics", frame)

        else:
            manage_statusbar_1(frame, True, isMarking, isRecording)
            handTrackObj.DisplayRectForSampling(frame) #this will show the sampling location where the sample will get
            cv2.imshow("Hand Acknowledgement and Tracking that Documents and Overwrite Graphics", frame)

        #for the video recording
        if (isRecording and handTrackObj.getIsThereHandHist() ):
            video_writer.write(whiteboard)

    # When everything done, release the capture
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

def keyinfogui():
    gui = Tk(className= " Key Events and Keywords Info")
    gui.geometry("700x600")

    font_size_info = 12
    pad_y = 5
    Label(gui , text="Key Events", font=("Times New Roman", 18, 'bold')).pack(pady = pad_y)
    Label(gui, text="Key 'g' - It will get the sample from the squares for the hand tracking under the status of 'Getting sample' of the software", font=("Times New Roman", font_size_info, 'italic'), wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 's' - It will start marking or stop marking the whiteboard", font=("Times New Roman", font_size_info, 'italic'),wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 'e' - It will turn the tip into eraser to erase the markings ", font=("Times New Roman",font_size_info, 'italic'),wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 'b' - It will turn the tip into ballpen to mark the whiteboard depending on the status", font=("Times New Roman", font_size_info, 'italic'),wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 'c' - It will erase on the markings in the whiteboard", font=("Times New Roman", font_size_info , 'italic'),wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 'r' - It will start recording or stop recording the markings in the whiteboard", font=("Times New Roman", font_size_info, 'italic'),wraplength = 500).pack(pady=pad_y)
    Label(gui, text="Key 'q' - It will close/quit the software", font=("Times New Roman", font_size_info,'italic'),wraplength = 500).pack(pady=pad_y)



    Label(gui ,text="Key Words Info", font=("Times New Roman", 18, 'bold')).pack(pady = pad_y)
    Label(gui ,text="Getting sample - The software ask for the sample of the user's hand. Place your"
                              + " hand in the squares. Make sure all of the squares is occupied by the hand. Once"
                                + " it is ready, just press the key 'g'", font=("Times New Roman", font_size_info, 'italic') , wraplength = 500).pack(pady = pad_y)

    Label(gui , text="No Recording - The whiteboard is not being recorded", font=("Times New Roman", font_size_info, 'italic')).pack(pady = pad_y)
    Label(gui, text="Recording - The whiteboard is being recorded", font=("Times New Roman", font_size_info , 'italic')).pack(
        pady=pad_y)
    Label(gui, text="Tracking - The software tracks the hand and determines where the pointer finger is located", font=("Times New Roman", font_size_info,'italic')).pack(
        pady=pad_y)

    Button(gui, text="Back", font=("Times New Roman", 15 ), command=gui.destroy).pack(pady=pad_y)

    gui.mainloop()

def startinggui():

    global root
    root = Tk(className=" HATDOG")
    root.geometry("350x500")

    # for the framing
    topFrame = Frame(root)
    topFrame.pack()

    # for the title
    Label(topFrame, text="HATDOG", font=("Times New Roman", 30)).grid(row = 0 , column = 0 , pady = 10)
    Label(topFrame, text="Hand Acknowledgement and Tracking that Documents and Overwrite Graphics",
          font=("Times New Roman",  20) ,wraplength = 300, justify = RIGHT).grid(row = 1 , column = 0, pady = 40)

    # for the buttons
    Button(topFrame, text="Start Software", font=("Times New Roman", 15) , command = ExecuteApplication).grid(row = 2 , column = 0 , pady = 20)
    Button(topFrame, text="Key Events and Keywords Info", font=("Times New Roman", 15), command = keyinfogui).grid(row = 3 , column = 0)

    root.mainloop()

if(__name__ == '__main__'):
    startinggui()