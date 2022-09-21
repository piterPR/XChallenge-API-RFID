import datetime
import serial
import pandas as pd
from flask import Flask,json, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import serial.tools.list_ports
import time
import sys
from error_handler import NoSpecifiedParamsError, RFIDCardError, WrongPatternError, WrongPatternError, error_handler, check_is_error_code, MaxTimeoutError
import re

###########################################################################################################################################################################
# ENVS AND SETUP AND PRE-FLIGHT CHECKS
###########################################################################################################################################################################


from flask import Flask, jsonify, request,render_template
import os

def findComPort(): 
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Silicon Labs CP210x" in p.description: 
            return str(p.name)

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
comPortESP = findComPort()
maxAwaitTimeInSeconds = 5

###########################################################################################################################################################################
# API ENDPOINTS
###########################################################################################################################################################################


@app.route('/referee/readRFIDTag', methods=['GET'])
def readRFIDTag():
    return readTag()

@app.route('/referee/writeRFIDTag', methods=['POST'])
def writedRFIDTag():
    data = request.get_json()
    return writeTag(data)

@app.route('/referee/readLapTime', methods=['GET'])
def readLapTime():
    return "124542"

@app.route('/testLED_ON', methods=['GET'])
def testLED_ON():
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'0')
    return "ON"

@app.route('/testLED_OFF', methods=['GET'])
def testLED_OFF():
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'1')
    return "OFF"

###########################################################################################################################################################################
# FUNCIONS
###########################################################################################################################################################################


def readTag():
    try:
        ser = serial.Serial(comPortESP, 115200)
        ser.write(b'2')    ## dwojka za odczyt RFID
    except Exception as e: return error_handler(e)
    beginTime = time.time()
    returnValue = None
    while returnValue == None and int(time.time() - beginTime) < maxAwaitTimeInSeconds:
        if ser.in_waiting:
            response = str(ser.readline())
            errorCode = check_is_error_code(response)
            if errorCode != None:
                return error_handler(RFIDCardError(errType=errorCode))
            print(response)
            stopUid = "b'UID:"
            if(stopUid in response):
                returnValue = response[55:58]
                print(returnValue)
                ser.close()
    if returnValue != None:
        if not re.search("^[0-9]{3}$", returnValue):
            return error_handler(WrongPatternError())
        return jsonify(returnValue)
    else:
        ser.close()
        return error_handler(MaxTimeoutError())

def writeTag(requestData):
    if not "uzytkownik_id" in requestData:
        return error_handler(NoSpecifiedParamsError(paramName="uzytkownik_id"))
    id = str(requestData["uzytkownik_id"])
    if not re.search("^[0-9]{1,3}$", id):
        return error_handler(WrongPatternError())
    while len(id) < 3: id = "0" + id
    try:
        ser = serial.Serial(comPortESP, 115200)
        ser.write(b'3')    ## trojka za zapis RFID
    except Exception as e: return error_handler(e)
    beginTime = time.time()
    returnValue = None
    ser.write(bytearray(id, 'utf-8'))
    if ser.in_waiting:
        response = str(ser.readline())
        print(response)
    # while returnValue == None and int(time.time() - beginTime) < maxAwaitTimeInSeconds:
    # if returnValue != None:
    #     # if not re.search("^[0-9]{3}$", returnValue):
    #     #     return error_handler(WrongPatternError())
    return jsonify("ASD")
    # else:
    #     ser.close()
    #     return error_handler(MaxTimeoutError())


if __name__ == "__main__":
    if comPortESP == None:
        print("Nie znaleziono podlaczonego ESP")
        sys.exit()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='127.0.0.1', port=port)







