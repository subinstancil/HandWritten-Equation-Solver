from tkinter import *
import os
from skimage import color, io
from skimage import transform
from PIL import Image, ImageTk
import numpy as np
from integratedImageProcessing import *
import imageio


import csv
def writeCSVFile(path, contents):
    with open(path, 'w', newline = '') as f:
        writer = csv.writer(f)
        for row in contents:
            writer.writerow(row)

def init(data, imageNo = 0, overallIdentified = []):
    
    data.modes = ['AOI', 'contours', 'classification']
    data.mode = 0
    data.points = []
    
    data.imageList = os.listdir('attachments')
    if '.DS_Store' in data.imageList: data.imageList.remove('.DS_Store')
    writeCSVFile('attachment3FileLocations', list(map(lambda x: [x], data.imageList)))
    
    data.imageNo = imageNo
    global overallImg
    medians = []
    overallImg = io.imread('attachments/'+data.imageList[data.imageNo])
    overallImg = color.rgb2gray(overallImg)
    overallImg *= 255

    global threshImg
    threshImg = (overallImg > 0.5 * 255).astype(float)
    threshImg *= 255
    
    global resizedImg
    height, width = overallImg.shape
    imWidth, imHeight = data.width * 3 // 4, data.height * 3 // 4
    data.ratio = min(imWidth/width, imHeight/height)
    imWidth, imHeight = int(data.ratio*width), int(data.ratio*height)
    resizedImg = transform.resize(overallImg / 255, (imHeight, imWidth)) * 255
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
    if data.mode == 4: pass
    data.cursorX, data.cursorY = event.x, event.y

def keyPressed(event, data):
    if data.mode == 4: pass
    global box
    global unprocessedBox

    if data.mode == 0:
        if event.keysym == 'p' and len(data.points) == 2:
            
            global resizedImg
            global overallImg
            global threshImg
            height, width = resizedImg.shape
            marginW = (data.width - width) // 2
            marginH = (data.height - height) // 2
            pts = list(map(lambda p: [p[0]-marginW, p[1]-marginH], data.points))
            resizedImg = resizedImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
            pts = (np.array(pts) * 1 / data.ratio).astype(int).tolist()
            overallImg = overallImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
            threshImg = threshImg[pts[0][1]:pts[1][1], pts[0][0]:pts[1][0]]
            data.mode = 1
            
            global againresizedImg
            height, width = overallImg.shape
            imWidth, imHeight = data.width * 3 // 4, data.height * 3 // 4
            data.ratio = min(imWidth/width, imHeight/height)
            imWidth, imHeight = int(data.ratio*width), int(data.ratio*height)
            againresizedImg = transform.resize(overallImg/255, (imHeight, imWidth))*255
            showContours(overallImg/255)
        if event.keysym == 'd':
            data.points = []
    elif data.mode == 1:
        if event.keysym == 'p':
            data.mode += 1
            print("ok")
            data.boxList = getBoxes(overallImg/255)
            data.mode = 2
            data.boxNo = 0
            [r0, c0, r1, c1] = list(map(int, data.boxList[data.boxNo]))
            box = threshImg[r0:r1+1, c0:c1+1]
            unprocessedBox = overallImg[r0:r1+1, c0:c1+1]
    elif data.mode == 2:
        try:
            try:
                num = int(event.keysym)
            except:
                print(event.keysym)
                assert(event.char == "+" or event.char == "*" or event.char == "-"
                or event.char == "?")
                num = event.char
            print("OK")
            fileName = (data.imageList[data.imageNo])[4:-4] +'-'+str(data.boxNo)+'.jpg'
            path = 'digits/'+fileName
          
            newBox = resizeToSquare(box)
            imageio.imwrite(path, newBox)
            
            otherPath = 'totalDigits/'+fileName
            imageio.imwrite(otherPath, unprocessedBox)

            data.identified.append(num)
            data.boxNo += 1
        except:
            if event.keysym == "BackSpace":
                if data.boxNo > 0:
                    data.boxNo -= 1
                    data.identified.pop()
            else:
                return
        if data.boxNo == len(data.boxList):
            data.overallIdentified.append(data.identified)
            if data.imageNo + 1 == len(data.imageList):
                print("Done")
                data.mode = 4
                print(data.overallIdentified)
                writeCSVFile("attachments3Digit-classification.csv", data.overallIdentified)
                return
            init(data, data.imageNo+1, data.overallIdentified)
            return
        [r0, c0, r1, c1] = list(map(int, data.boxList[data.boxNo]))
        box = threshImg[r0:r1+1, c0:c1+1]
        unprocessedBox = overallImg[r0:r1+1, c0:c1+1]
        print(data.identified)
    pass

def timerFired(data):
    pass

def redrawAll(canvas, data):
    if data.mode == 4: pass
    if data.mode == 0: return redrawAllMode0(canvas, data)
    if data.mode == 1: return redrawAllMode1(canvas, data)
    if data.mode == 2: return redrawAllMode2(canvas, data)

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

def redrawAllMode1(canvas, data):
    global photoImg
    global tkImg
    global againresizedImg

    photoImg = Image.fromarray(againresizedImg)

    tkImg = ImageTk.PhotoImage(photoImg)
    canvas.create_image(data.width/2, data.height/2, image = tkImg)

def redrawAllMode2(canvas, data):
    global box
    global photoImg
    global tkImg

    photoImg = Image.fromarray(box)

    tkImg = ImageTk.PhotoImage(photoImg)
    canvas.create_image(data.width/2, data.height/2, image = tkImg)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(0, 0, data.width, data.height,
                                fill='white', width=0)
        redrawAll(canvas, data)
        canvas.update()    

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
        redrawAllWrapper(canvas, data)
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 
    init(data)
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

run(600, 400)
