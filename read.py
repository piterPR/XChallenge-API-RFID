import serial
import time
import pandas as pd
import ast
from flask import Flask,json, render_template, request, jsonify
import string

ser = serial.Serial('COM7', 115200)




def readLastLine():
    global ser
    data='2'
    data_as_bytes = str.encode(data)
    ser.write(b'2')   
    to_continue = True
    while to_continue:
        response = ser.readline()
        str_response = str(response)
        print(str_response)
        stop = "b'UID:"
        if(stop in str_response):
            print(str_response)
            to_continue= False
            ser.close()
        str_response = str_response[55:70]
        print(str_response)

readLastLine()
