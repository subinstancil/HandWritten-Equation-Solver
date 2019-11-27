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


import flask
import werkzeug

def find(image):
	global overallImg
	overallImg = io.imread(image)
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
	return cal


app = flask.Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def handle_request():
    imagefile = flask.request.files['image']
    filename = werkzeug.utils.secure_filename(imagefile.filename)
    print("\nReceived image File name : " + imagefile.filename)
    imagefile.save(filename)
    print(filename)
    x=find(filename)
    print(x)
    return x

app.run(host="0.0.0.0", port=5000, debug=True)
