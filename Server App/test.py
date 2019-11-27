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
global overallImg
overallImg = io.imread("./androidFlask.jpg")
overallImg = color.rgb2gray(overallImg)
global threshImg
threshImg = (overallImg > 0.5).astype(float)
threshImg *= 255
overallImg *= 255
boxList = getBoxes(overallImg/255)
boxNo = 0
[r0, c0, r1, c1] = list(map(int, boxList[boxNo]))
box = threshImg
unprocessedBox = overallImg
expression = parseText(threshImg, boxList)
calculation = mainEval(expression)

cal=str(calculation)
print(cal)