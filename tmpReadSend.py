import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import time as tm
import random
import csv
import math
from statsmodels.graphics.gofplots import qqplot
import statsmodels.api as sm
import pandas as pd

gatherIntervalInMin = 0.2
lastTime = 0
filePath = "temperature.txt"
bits = 4096

def readTemperature(filePath, time):
    global lastTime
    global cntr
    if(time < lastTime + 0.1 and lastTime != 0):
        #print("last read less than 100ms ago ")
        exit;
    else:
        data = list(csv.reader(open(filePath)))
        x = random.randint(0, len(data)-1)
        tmpVal = data[x][0]

        lastTime = tm.time()
        return float(tmpVal)

def convertToC(inVal):
    out = (inVal/bits)*100-50
    return out

def gatherTwoMin():
    startTime = tm.time()
    data = []
    while tm.time() < syfjtartTime+gatherIntervalInMin*60:
        currentTemp = readTemperature(filePath, tm.time())
        if(currentTemp is not None):
            data.append(convertToC(currentTemp))
    return data

def calcMaxMinAvg(data):
    max = np.max(data)
    min = np.min(data)
    avg = np.mean(data)
    return max, min, avg

#print(calcMaxMinAvg(gatherTwoMin()))


#print(gatherTwoMin(tm.time()))
#tmpVal = readTemperature("temperature.txt", tm.time())
#print(tmpVal)
#tm.sleep(0.08)
#tmpVal1 = readTemperature("temperature.txt", tm.time())
#print(tmpVal1)
