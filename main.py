import serial
from flask import Flask, request, jsonify
from flask_cors import CORS
import serial.tools.list_ports
import time
import sys
from error_handler import NoCOMPortFindedError, NoSpecifiedParamsError, RFIDCardError, WrongPatternError, buildResponseMessage, error_handler, check_is_error_code, MaxTimeoutError
import re

###########################################################################################################################################################################
# ENVS AND SETUP AND PRE-FLIGHT CHECKS
###########################################################################################################################################################################


def findComPort():
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Silicon Labs CP210x" in p.description:
            return str(p.name)


app = Flask(__name__)
cors = CORS(app)
host = "127.0.0.1"
port = 5000
app.config['CORS_HEADERS'] = 'Content-Type'
comPortESP = findComPort()
maxAwaitTimeInSeconds = 5
maxLapTimeInSeconds = 240

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


@app.route('/referee/eraseRFIDTag', methods=['GET'])
def eraseRFIDTag():
    return eraseRFIDTag()


@app.route('/referee/readOneGate', methods=['GET'])
def readOneGate():
    return readOneGate()


@app.route('/referee/readTwoGates', methods=['GET'])
def readTwoGates():
    return readTwoGates()


@app.route('/testLED_ON', methods=['GET'])
def testLED_ON():
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'1')
    return buildResponseMessage("ON", "-100", "Sukces")


@app.route('/testLED_OFF', methods=['GET'])
def testLED_OFF():
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'0')
    return buildResponseMessage("OFF", "-100", "Sukces")

###########################################################################################################################################################################
# FUNCIONS
###########################################################################################################################################################################


def openSerialPort():
    ser = serial.Serial(comPortESP, 115200)
    time.sleep(0.1)
    while(ser.in_waiting):
        ser.readline()
    return ser


def readTag():
    try:
        ser = openSerialPort()
        ser.write(b'2')  # dwojka za odczyt RFID
    except Exception as e:
        return error_handler(e)
    beginTime = time.time()
    returnValue = None
    while returnValue == None and int(time.time() - beginTime) < maxAwaitTimeInSeconds:
        if ser.in_waiting:
            response = str(ser.readline())
            print(response)
            errorCode = check_is_error_code(response)
            stopUid = "b'UID:"
            if(stopUid in response):
                returnValue = response[55:58]
                print(returnValue)
            else:
                if errorCode != None:
                    return error_handler(RFIDCardError(errType=errorCode))
    if returnValue != None:
        ser.close()
        if not re.search("^[0-9]{3}$", returnValue):
            return error_handler(WrongPatternError(returnValue))
        return buildResponseMessage({"uzytkownik_id": int(returnValue)}, "-100", "Sukces")
    else:
        ser.close()
        return error_handler(MaxTimeoutError())


def writeTag(requestData):
    if not "uzytkownik_id" in requestData:
        return error_handler(NoSpecifiedParamsError(paramName="uzytkownik_id"))
    id = str(requestData["uzytkownik_id"])
    if not re.search("^[0-9]{1,3}$", id):
        return error_handler(WrongPatternError(id))
    while len(id) < 3:
        id = "0" + id
    try:
        ser = openSerialPort()
        ser.write(b'3')  # zapis RFID
    except Exception as e:
        return error_handler(e)
    beginTime = time.time()
    returnValue = None
    ser.write(bytearray(id, 'utf-8'))
    while returnValue == None and int(time.time() - beginTime) < maxAwaitTimeInSeconds:
        if ser.in_waiting:
            response = str(ser.readline())
            print(response)
            errorCode = check_is_error_code(response)
            if errorCode == "-100":
                ser.close()
                return readTag()
            elif errorCode != None:
                return error_handler(RFIDCardError(errType=errorCode))
    ser.close()
    return error_handler(MaxTimeoutError())


def eraseRFIDTag():
    try:
        ser = openSerialPort()
        ser.write(b'4')  # cz za zapis RFID
    except Exception as e:
        return error_handler(e)
    beginTime = time.time()
    returnValue = None
    while returnValue == None and int(time.time() - beginTime) < maxAwaitTimeInSeconds:
        if ser.in_waiting:
            response = str(ser.readline())
            print(response)
            errorCode = check_is_error_code(response)
            if errorCode != None:
                return error_handler(RFIDCardError(errType=errorCode))
    if returnValue != None:
        ser.close()
        return buildResponseMessage(returnValue, "-100", "Sukces")
    else:
        ser.close()
        return error_handler(MaxTimeoutError())


def readOneGate():
    try:
        ser = openSerialPort()
        ser.write(b'5')  # trojka za zapis RFID
    except Exception as e:
        return error_handler(e)
    beginTime = time.time()
    returnValue = None
    awaitTime = maxAwaitTimeInSeconds
    while returnValue == None and int(time.time() - beginTime) < awaitTime:
        if ser.in_waiting:
            response = str(ser.readline())
            print(response)
            errorCode = check_is_error_code(response)
            if errorCode != None:
                return error_handler(RFIDCardError(errType=errorCode))
            if "Odliczam czas" in response:
                awaitTime = maxLapTimeInSeconds
                beginTime = time.time()
                ser.write(b'1')
            elif "Czas przejazdu" in response:
                returnValue = response[18:].split('.')[0]
                print(str(returnValue))
    if returnValue != None:
        if not re.search("^[0-9]{4,}$", returnValue):
            return error_handler(WrongPatternError(returnValue))
        ser.write(b'0')
        ser.close()
        return buildResponseMessage({"czas_przejazdu": returnValue}, "-100", "Sukces")
    else:
        ser.close()
        return error_handler(MaxTimeoutError())


def readTwoGates():
    try:
        ser = openSerialPort()
        ser.write(b'6')
    except Exception as e:
        return error_handler(e)
    beginTime = time.time()
    returnValue = None
    while returnValue == None and int(time.time() - beginTime) < maxLapTimeInSeconds:
        if ser.in_waiting:
            response = str(ser.readline())
            print(response)
            errorCode = check_is_error_code(response)
            if errorCode != None:
                return error_handler(RFIDCardError(errType=errorCode))
            if "Odliczam czas" in response:
                ser.write(b'1')
            elif "Czas przejazdu" in response:
                returnValue = response[18:].split('.')[0]
                print(str(returnValue))
    if returnValue != None:
        if not re.search("^[0-9]{4,}$", returnValue):
            return error_handler(WrongPatternError(returnValue))
        ser.write(b'0')
        ser.close()
        return buildResponseMessage({"czas_przejazdu": returnValue}, "-100", "Sukces")
    else:
        ser.write(b'0')
        ser.close()
        return error_handler(MaxTimeoutError())


if __name__ == "__main__":
    if comPortESP == None:
        error_handler(NoCOMPortFindedError())
        sys.exit()
    from waitress import serve
    print("Server is listening on " + host + ":" + str(port))
    testLED_OFF()
    serve(app, host=host, port=port)
