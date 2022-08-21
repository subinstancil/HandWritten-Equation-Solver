import pip
from sklearn.externals import joblib
import numpy as np
from integratedImageProcessing import *

mlp = joblib.load('NewMLPClassifier.pkl')
scaler = joblib.load('NewScaler.pkl')

def classify(img):
    size = img.shape
    box = resizeToSquare(img)
    x = box.flatten()
    x = np.append(x, size)
    x = x.reshape(1, -1)
    prediction = mlp.predict(scaler.transform(x))
    prob = np.amax(mlp.predict_proba(scaler.transform(x)))
    if prediction == 11: prediction = "+"
    elif prediction == 12: prediction = "-"
    elif prediction == 13: prediction = "*"
    else: prediction = str(prediction[0])
    return prob, prediction

def splitImg(img):
    img = img/255
    img = opening(img)
    img = 1 - img
    img = skeletonize(img)
    img = dilation(img)
    contours = measure.find_contours(img, 0)
 
    kMin = lambda x, y: [min(x[0], y[0]), min(x[1], y[1])]
    kMax = lambda x, y: [max(x[0], y[0]), max(x[1], y[1])]
    boxes = [reduce(kMin, contour)+reduce(kMax, contour) 
            for contour in contours]
    
    def overlapsInside(box, boxes, i):
        [ya, xa, yb, xb] = box
        for j in range(len(boxes)):
            if i == j: continue
            [y0, x0, y1, x1] = boxes[j]
            if ((x0 <= xa and xb <= x1) and (y0 <= ya and yb <= y1)):
                return True
        return False
    
    boundingBoxes = []
    i = 0
    while i < len(boxes):
        if not overlapsInside(boxes[i], boxes, i):
            boundingBoxes += [boxes[i]]
        i += 1
    boundingBoxes.sort(key = lambda x: x[1])
    if len(boundingBoxes) == 2:
        return (int(boundingBoxes[0][3]), int(boundingBoxes[1][1]))
    else:
     
        return (len(img)//2, len(img)//2)

def parseText(threshImg, boxCoords):
    assert(max(threshImg.flatten()) > 250)
    boxCoords.sort(key = lambda x: x[1])
    predictions = []
    for coords in boxCoords:
        [r0, c0, r1, c1] = list(map(int, coords))
        prob, prediction = classify(threshImg[r0:r1+1, c0:c1+1])
        size = (r1+1-r0)/(c1+1-c0)
       
        predictions.append(prediction)
    predictions, boxCoords = dealWithDivides(predictions, boxCoords)
    print("".join(predictions))
    return "".join(predictions)

def dealWithDivides(predictions, boxCoords, startIndex = 0):
    try:
        pos = predictions.index("-", startIndex)
    except:
        return predictions, boxCoords 
    
    start = pos
    def overlaps(target, focus):
       
        x0, x1, xa, xb = target[1], target[3], focus[1], focus[3]
        xmid = (x0+x1)/2
        return xmid > xa and xmid < xb
    while start > 0 and overlaps(boxCoords[start-1], boxCoords[pos]):
        start -= 1
    end = pos+1
    while end < len(predictions) and overlaps(boxCoords[end], boxCoords[pos]):
        end += 1
    if start == pos and end == pos+1:
        return dealWithDivides(predictions, boxCoords, pos+1)
    
    above, aboveBoxes, below, belowBoxes = [], [], [], []
    line = (boxCoords[pos][0] + boxCoords[pos][2]) / 2
    for i in range(start, end):
        if i == pos: continue
        mid = (boxCoords[i][0] + boxCoords[i][2]) / 2
        if mid < line:
            above.append(predictions[i])
            aboveBoxes.append(boxCoords[i])
        else:
            below.append(predictions[i])
            belowBoxes.append(boxCoords[i])
    if len(above) == 0 or len(below) == 0:
        return dealWithDivides(predictions, boxCoords, pos+1)
    
    aboveList, aboveBoxList = dealWithDivides(above, aboveBoxes)
    belowList, belowBoxList = dealWithDivides(below, belowBoxes)
    newEndPos = end + len(aboveList) + len(belowList)
    newPredictionList = (predictions[:start] + 
                         ["("] + aboveList + [")"] + ["/"] +
                         ["("] + belowList + [")"] + predictions[end:])
    newBoxCoords = (boxCoords[:start] + 
                         [None] + aboveBoxList + [None] + [None] +
                         [None] + belowBoxList + [None] + boxCoords[end:])
    return dealWithDivides(newPredictionList, newBoxCoords, newEndPos)


    # test comment
    # test comment 2
