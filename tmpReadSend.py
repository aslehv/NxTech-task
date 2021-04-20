import numpy as np
import time as tm
import random
import datetime
import csv
import requests


gatherIntervalInMin = 2 #For how many minutes should data be gathered each round
filePath = "temperature.txt" #Path to file for temperature reading
bits = 4096 #ADC resolution
url = "http://localhost:5000/api/temperature" #URL to REST API
errorUrl = "http://localhost:5000/api/temperature/missing" #URL to backup server on fail
lastTime = 0 #global var for readTemperature function

def readTemperature(filePath, time): #Reads random temp value from file and returns float
    global lastTime
    if(time < lastTime + 0.1 and lastTime != 0):
        #print("last read less than 100ms ago ")
        exit;
    else:
        data = list(csv.reader(open(filePath)))
        x = random.randint(0, len(data)-1)
        tmpVal = data[x][0]

        lastTime = tm.time()
        return float(tmpVal)

def convertToC(inVal): #converts value from readTemperature to Celsius where temp is 0+- 50C
    out = (inVal/bits)*100-50
    return out

def gatherData(): #Gather data to list for defined amount of minutes
    startSec = tm.time()
    startTime = datetime.datetime.utcnow().isoformat()
    data = []
    while tm.time() < startSec+gatherIntervalInMin*60:
        currentTemp = readTemperature(filePath, tm.time())
        if(currentTemp is not None):
            data.append(convertToC(currentTemp))
    return data, startTime, datetime.datetime.utcnow().isoformat()

def calcMaxMinAvg(data): #Return max, min and average from list input.
    max = np.max(data)
    min = np.min(data)
    avg = np.mean(data)
    return max, min, avg

def httpPost(payload, url): #Post data to url as defined return status code
    request = requests.post(url, json=payload)
    return request.status_code
def jsonMaker(max,min,avg,startTime,endTime): #Create object ready for json POST
    data = {
            "time": {
                    "start": str(startTime),
                    "end": str(endTime)
            },
            "min": np.round(float(min), 2),
            "max": np.round(float(max), 2),
            "avg": np.round(float(avg), 2)
    }
    return data
def archiver(jsonval, archive): #Keeps archive at max 10, adds latest reading.
    if(len(archive) > 9):
        archive.pop(0)
    archive.append(jsonval)
    return archive
    #print(archive, "len: ", len(archive))

def main(): #starts and runs the program in a while loop. Error handling included.
    archive = []
    lastOK = 0
    while True:
        data, startTime, endTime = gatherData()
        max, min, avg = calcMaxMinAvg(data)
        jsonval = jsonMaker(max,min,avg,startTime,endTime)
        archive = archiver(jsonval, archive)

        if lastOK >= 1:
            newReq = httpPost(archive[-1], url)
            print("Last failed, sending it now.")
            if newReq != 200:
                errpost = httpPost(archive, errorUrl)
                print("Resend failed, sending last 10 to alternative server.")
            else:
                print("Resend succesful!")
        post = httpPost(jsonval, url)
        #print(post)
        if post != 200:
            lastOK += 1
            print("Send failed, resending next round")
        else:
            lastOK = 0
            print("Data succesfully sent!")
        #print("archive length: ", len(archive))
        #print("lastOK counter:", lastOK)

main()
