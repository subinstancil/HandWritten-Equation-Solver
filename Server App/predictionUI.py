

from tkinter import *
import os
from skimage import color, io
from skimage import transform
from PIL import Image, ImageTk
import numpy as np
from integratedImageProcessing import *
from imageParser import *
import imageio
from performCalculation import *
import sys

import csv
def writeCSVFile(path, contents):
    with open(path, 'w', newline = '') as f:
        writer = csv.writer(f)
        for row in contents:
            writer.writerow(row)

def init(data, imageNo = 0, dir = 'tests', overallIdentified = []):
    
    data.modes = ['AOI', 'contours', 'prediction']
    data.mode = 0
    data.points = []
    
    data.dir = dir
    data.imageList = os.listdir(dir)
    if '.DS_Store' in data.imageList: data.imageList.remove('.DS_Store')
    
    data.imageNo = imageNo
    global overallImg
    overallImg = io.imread(os.path.join(dir, data.imageList[data.imageNo]))
    overallImg = color.rgb2gray(overallImg)
    
    global threshImg
    threshImg = (overallImg > 0.5).astype(float)
    threshImg *= 255
    
    overallImg *= 255
    
    global resizedImg
    height, width = overallImg.shape
    imWidth, imHeight = data.width * 3 // 4, data.height * 3 // 4
    data.ratio = min(imWidth/width, imHeight/height)
    imWidth, imHeight = int(data.ratio*width), int(data.ratio*height)
    resizedImg = transform.resize(overallImg, (imHeight, imWidth))
    print(data.imageList[data.imageNo])
    data.cursorX, data.cursorY = 0, 0
    data.boxList = []
    data.identified = []
    data.overallIdentified = overallIdentified
    pass

def mousePressed(event, data):
    if data.mode == 4: pass
    if data.mode == 0: return mousePressedMode0(event, data)
    if data.mode == 1: pass
    if data.mode == 2: pass

def mousePressedMode0(event, data):
    height, width = resizedImg.shape
    marginW = (data.width - width) // 2
    marginH = (data.height - height) // 2
    if (len(data.points) < 2 and (marginW < event.x < data.width - marginW) 
        and (marginH < event.y < data.height - marginH)):
            if len(data.points) == 0: data.points.append([event.x, event.y])
            elif event.x > data.points[0][0] and event.y > data.points[0][1]:
                data.points.append([event.x, event.y])
            elif event.x < data.points[0][0] and event.y < data.points[0][1]:
                data.points = [[event.x, event.y]] + data.points


def mouseMotion(event, data):
    data.cursorX, data.cursorY = event.x, event.y

def keyPressed(event, data):
    if data.mode == 0: return keyPressedMode0(event, data)
    if data.mode == 1: return keyPressedMode1(event, data)
    if data.mode == 2: return keyPressedMode2(event, data)

def keyPressedMode0(event, data):
    if event.keysym == 'd': data.points = []
    if not (event.keysym == 'p' and len(data.points) == 2): return 

    global box
    global unprocessedBox
    global resizedImg
    global overallImg
    global threshImg

    height, width = resizedImg.shape
    marginW = (data.width - width) // 2
    marginH = (data.height - height) // 2
    pts = list(map(lambda p: [p[0]-marginW, p[1]-marginH], data.points))
    resizedImg = resizedImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
    pts = (np.array(pts) * 1 / data.ratio).astype(int).tolist()
    print(pts)
    overallImg = overallImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
    threshImg = threshImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
    data.mode = 1
    
    global againresizedImg
    height, width = overallImg.shape
    imWidth, imHeight = data.width * 3 // 4, data.height * 3 // 4
    data.ratio = min(imWidth/width, imHeight/height)
    imWidth, imHeight = int(data.ratio*width), int(data.ratio*height)
    againresizedImg = transform.resize(overallImg, (imHeight, imWidth))
    showContours(overallImg/255, False)

def keyPressedMode1(event, data):

    global box
    global unprocessedBox
    global resizedImg
    global overallImg
    global threshImg

    if event.keysym == 'p':
        data.mode += 1
        data.boxList = getBoxes(overallImg/255)
        data.mode = 2
        data.boxNo = 0
        [r0, c0, r1, c1] = list(map(int, data.boxList[data.boxNo]))
        box = threshImg
        unprocessedBox = overallImg
        data.expression = parseText(threshImg, data.boxList)
        data.calculation = mainEval(data.expression)

def keyPressedMode2(event, data):
    if event.keysym == "p" and data.imageNo != len(data.imageList) - 1:
        init(data, data.imageNo+1, dir = data.dir)
    else:
        print("Done")
        data.mode = 3

def timerFired(data):
    pass

def redrawAll(canvas, data):
    if data.mode == 0: return redrawAllMode0(canvas, data)
    if data.mode == 1: return redrawAllMode1(canvas, data)
    if data.mode == 2: return redrawAllMode2(canvas, data)
    if data.mode == 3: return redrawAllMode3(canvas, data)

def redrawAllMode0(canvas, data):
    global photoImg
    global tkImg
    global resizedImg

    photoImg = Image.fromarray(resizedImg)

    tkImg = ImageTk.PhotoImage(photoImg)
    canvas.create_image(data.width/2, data.height/2, image = tkImg)
    
    if len(data.points) == 2:
        canvas.create_rectangle(data.points[0][0], data.points[0][1], 
        data.points[1][0], data.points[1][1])
    elif len(data.points) == 1:
        canvas.create_rectangle(data.points[0][0], data.points[0][1], 
        data.cursorX, data.cursorY)
    instruction = "Select the area of interest, then press p to proceed"
    canvas.create_text(data.width - 10, data.height - 10, 
                       text = instruction, anchor = SE)

def redrawAllMode1(canvas, data):
    global photoImg
    global tkImg
    global againresizedImg

    photoImg = Image.fromarray(againresizedImg)

    tkImg = ImageTk.PhotoImage(photoImg)
    canvas.create_image(data.width/2, data.height/2, image = tkImg)
    canvas.create_text(data.width - 10, data.height - 10, text = "Press p to proceed", anchor = SE)

def redrawAllMode2(canvas, data):
    canvas.create_text(data.width/2, data.height/2, text = data.calculation ,font = "Arial 24 bold")
    canvas.create_text(data.width - 10, data.height - 10, text = "Press p to proceed", anchor = SE)

def redrawAllMode3(canvas, data):
    canvas.create_text(data.width/2, data.height/2, text = "Done", 
                       font = "Arial 24 bold")
    return "Done"

def run(width=300, height=300, dir = 'tests'):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        x = redrawAll(canvas, data)
        canvas.update()
        return x  

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def mouseMotionWrapper(event, canvas, data):
        mouseMotion(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        if redrawAllWrapper(canvas, data) == "Done":
            print("Done")
            root.quit()
            return
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 
    init(data, dir = dir)
    global root 
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Motion>", lambda event: mouseMotionWrapper(event, canvas, data)) 
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    root.mainloop()  
    print("bye!")

def main(userDir):
    run(600, 400, dir = userDir)

if __name__ == '__main__':
    main(sys.argv[1])
