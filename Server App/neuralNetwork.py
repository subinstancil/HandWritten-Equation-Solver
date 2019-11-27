import numpy as np
from skimage import io

import csv
import os

X , y = [], []

def readCSVFile(path):
    with open(path, newline = '') as f:
        reader = csv.reader(f)
        return list(reader)

def add(classification, unprocessedFolder, processedFolder):
    imgsAndDigits = readCSVFile(classification)

    def parseName(imgName):
        return str(int(imgName[4:-4])) + "-"

    for i in range(len(imgsAndDigits)):
        imgName, digits = imgsAndDigits[i][0], imgsAndDigits[i][1:]
        prefix, suffix = parseName(imgName), ".jpg"
        print(digits)
        for (j, digit) in enumerate(digits):
            if digit == "?": continue
            if digit == "": break
            num = digit
            imgName = prefix + str(j) + suffix
        
            filePath = os.path.join(unprocessedFolder, imgName)
            img = io.imread(filePath)
            size = img.shape
            
            filePath = os.path.join(processedFolder, imgName)
            img = io.imread(filePath)
            x = img.flatten()
            x = np.append(x, size)
            X.append(x)
            try:
                num = int(num)
            except:
                if num == "+": num = 11
                elif num == "-": num = 12
                elif num == "*": num = 13
                else: raise Exception
            y0 = num
            y.append(y0)

add('totalDigit-classification.csv', 'unprocessedDigits', 'processedDigits')

X = np.array(X)
y = np.array(y)
print(X.shape)
print(y.shape)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y)

from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
scaler.fit(X_train)

X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)


from sklearn.neural_network import MLPClassifier
mlp = MLPClassifier(hidden_layer_sizes=(30), activation = 'logistic')

print("Training")
mlp.fit(X_train,y_train)
print("Trained")

predictions = mlp.predict(X_test)
probabilities = mlp.predict_proba(X_test)

from sklearn.metrics import classification_report,confusion_matrix
print(confusion_matrix(y_test,predictions))
print(classification_report(y_test,predictions))

print(y_test)
print(predictions)

from sklearn.externals import joblib
joblib.dump(mlp, 'NewMLPClassifier.pkl')
joblib.dump(scaler, 'NewScaler.pkl')
