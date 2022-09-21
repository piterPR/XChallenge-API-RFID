import serial

errorCodes = [
    "-1",
    "-2",
    "-3",
    "-4",
    "-5"
]

def check_is_error_code(stringValue):
    finded = None
    for value in errorCodes:
        if value in stringValue:
            finded = value
            break
    return finded

def error_handler(error):
    if isinstance(error, serial.serialutil.PortNotOpenError):
        message = "Nie otworzono portu szeregowego."
        print(message)
        return message
    elif isinstance(error, MaxTimeoutError):
        message = "Przekroczono maksymalny czas oczekiwania na odpowiedź."
        print(message)
        return message
    elif isinstance(error, WrongPatternError):
        message = "Niepoprawny format odpowiedzi. Spróbuj jeszcze raz."
        print(message)
        return message
    elif isinstance(error, RFIDCardError):
        print(error.message)
        return error.message
    elif isinstance(error, NoSpecifiedParamsError):
        print(error.message)
        return error.message
    else:
        message = "Wystąpił nieoczekiwany bład: " + str(error)
        print(message)
        return message

class MaxTimeoutError(Exception):
    pass

class WrongPatternError(Exception):
    pass

class RFIDCardError(Exception):
    def __init__(self, errType):
        self.message = "Nieoczekiwany bład karty RFID"
        print(errType)
        if errType == "-3":
            self.message = "Bład odczytytwania karty (złe hasło uwierzytelniania)."
        pass

class NoSpecifiedParamsError(Exception):
    def __init__(self, paramName):
        self.message = "Brak parametru: " + paramName
        pass
