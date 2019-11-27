

from sklearn.externals import joblib

mlp = joblib.load('NewMLPClassifier.pkl')
scaler = joblib.load('NewScaler.pkl')

def classify(img, size):
    x = img.flatten()
    x = np.append(x, size)
    x = x.reshape(1, -1)
    prediction = mlp.predict(scaler.transform(x))
    if prediction == 11: prediction = "+"
    elif prediction == 12: prediction = "-"
    elif prediction == 13: prediction = "*"
    else: prediction = str(prediction[0])
    return mlp.predict_proba(scaler.transform(x)), prediction

from skimage import io
from skimage.morphology import *
from skimage import measure, feature
import matplotlib.pyplot as plt
import numpy as np




import csv
import os
def readCSVFile(path):
    with open(path, newline = '') as f:
        reader = csv.reader(f)
        return list(reader)

digits = readCSVFile("evenMoreDigit-classification.csv")

imgs = os.listdir('evenMoreDigits')
imgs = list(filter(lambda x: ".jpg" in x, imgs))

def parseName(fileName):
    fileName = fileName[:-4]
    return list(map(int, fileName.split("-")))

imgNos = list(map(parseName, imgs))

concerningImgs = []
normalImgs = []
excludeRows = []
for i in range(len(imgs)):
    imgName, [rowNo, colNo] = imgs[i], imgNos[i]
    if rowNo in excludeRows or digits[rowNo][colNo] in "-+": continue
    if digits[rowNo][colNo] == "?":
        concerningImgs.append(imgName)
    else:
        normalImgs.append(imgName)
print(concerningImgs)
for imgName in concerningImgs:
    img = io.imread(os.path.join("evenMoreUnprocessedDigits", imgName))
    img = img > 0.5 * 255
    print(np.amax(img.flatten()))

    for i in range(1):
        img = opening(img)
    img = 1 - img
    img = skeletonize(img)
    img = dilation(img)
    plt.imshow(img)
    plt.show()
    contours = measure.find_contours(img, 0)
   
    print(len(contours))
   
    for n, contour in enumerate(contours):
        plt.plot(contour[:, 1], contour[:, 0], linewidth=2)
    plt.show()



def getProbs(imgs):
    resultProbs = []
    resultPreds = []
    for imgName in imgs:
        img = io.imread(os.path.join("moreDigits", imgName))
        size = (io.imread(os.path.join("moreUnprocessedDigits", imgName))).shape
        probs, prediction = classify(img, size)
        resultProbs.append(np.amax(probs))
        resultPreds.append(prediction)
    return resultProbs, resultPreds

concerningProbs, concerningPreds = getProbs(concerningImgs)
normalProbs, normalPreds = getProbs(normalImgs)

concerningProbs, normalProbs = np.array(concerningProbs), np.array(normalProbs)

print("Concerning Probs: ")
print("Max, min, average: ", np.amax(concerningProbs), np.amin(concerningProbs), np.average(concerningProbs))

print("Normal Probs: ")
print("Max, min, average: ", np.amax(normalProbs), np.amin(normalProbs), np.average(normalProbs))


concerningSizes = []
normalSizes = []

import numpy as np
from skimage import io
import matplotlib.pyplot as plt

for imgName in concerningImgs:
    filePath = os.path.join('unprocessedDigits', imgName)
    img = io.imread(filePath)
   
    concerningSizes.append(img.shape[0]/img.shape[1])
    if img.shape[0]/img.shape[1] > 0.65: print(imgName, img.shape[0]/img.shape[1])
for imgName in normalImgs:
    filePath = os.path.join('unprocessedDigits', imgName)
    img = io.imread(filePath)
    if imgName == "0-9.jpg": print(img.shape)
    normalSizes.append(img.shape[0]/img.shape[1])

concerningSizes = np.array(concerningSizes)
normalSizes = np.array(normalSizes)

print(list(filter(lambda x: x > 0.65, concerningSizes)))

print("Concerning height-to-width: ")
print(np.amax(concerningSizes), np.average(concerningSizes), np.amin(concerningSizes))
print("Normal height-to-width: ")
print(np.amax(normalSizes), np.average(normalSizes), np.amin(normalSizes)) 
print(normalImgs[np.argmin(normalSizes)])  
normalSizes[np.argmin(normalSizes)] = np.average(normalSizes)
print(np.amin(normalSizes)) 
print(normalImgs[np.argmin(normalSizes)]) 

for i in range(len(normalImgs)):
    size, prob = normalSizes[i], normalProbs[i]
    if (size < 0.7 and prob < 0.8) or (size < 0.8 and prob < 0.5):
        print("Uh-oh: misclassified", normalImgs[i], size, prob, normalPreds[i])

for i in range(len(concerningImgs)):
    size, prob = concerningSizes[i], concerningProbs[i]
    if (size >= 0.7 or prob >= 0.8) and (prob >= 0.5 or size >= 0.8):
        print("Uh-oh: unclassified", concerningImgs[i], size, prob, concerningPreds[i])
