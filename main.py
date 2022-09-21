import serial
import pandas as pd
from flask import Flask,json, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import serial.tools.list_ports




###########################################################################################################################################################################
# ENVS
###########################################################################################################################################################################


from flask import Flask, jsonify, request,render_template
import os

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
comPortESP = None

###########################################################################################################################################################################
# API
###########################################################################################################################################################################


@app.route('/referee/readRFIDTag', methods=['GET'])
def readRFIDTag():
    responseFromEsp = readTag(comPortESP)
    return responseFromEsp
    



@app.route('/referee/readLapTime', methods=['GET'])
def readLapTime():
    return "124542"


@app.route('/testLED_ON', methods=['GET'])
def testLED_ON():
    comPortESP = findComPort()
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'0')

@app.route('/testLED_OFF', methods=['GET'])
def testLED_OFF():
    comPortESP = findComPort()
    ser = serial.Serial(comPortESP, 115200)
    ser.write(b'1')
    
# @app.route('/flashDiode', methods=['GET'])
# def readLapTime():
#     return "124542"


###########################################################################################################################################################################
# FUNCIONS
###########################################################################################################################################################################


def readTag(COM_PORT="COM7"):
    ser = serial.Serial(COM_PORT, 115200)
    ser.write(b'2')    ## dwojka za odczyt RFID 
    to_continue = True
    while to_continue:
        response = ser.readline()
        str_response = str(response)
        print(str_response)
        stopUid = "b'UID:"
        stopTimeout = "b'nfcTimeout\r\n'"
        
        if(stopUid in str_response):
            if(stopTimeout in str_response):
                print("Timeout")
                to_continue = False
                ser.close()
                return jsonify("Timeout NFC")
            print(str_response)
            to_continue= False
            ser.close()
        str_response = str_response[55:70]
    return jsonify(str_response)


def findComPort(): 
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        if "Silicon Labs CP210x" in p.description: 
            print(p.name)
            return str(p.name)



if __name__ == "__main__":
    comPortESP = findComPort()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='127.0.0.1', port=port)
    







