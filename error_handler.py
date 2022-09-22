import serial

errorCodes = [
    "-100",
    "-1",
    "-2",
    "-3",
    "-4",
    "-5",
    "-6",
    "-7",
    "-8",
    "-9",
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
    elif isinstance(error, NoCOMPortFindedError):
        message = "Nie znaleziono podlaczonego ESP"
        print(message)
        return message
    elif isinstance(error, WrongPatternError):
        print(error.message)
        return error.message
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
    def __init__(self, rejectedValue):
        self.message = "Niepoprawny format odpowiedzi. Spróbuj jeszcze raz. Przkazana wartość -> " + rejectedValue
    pass

class NoCOMPortFindedError(Exception):
    pass

class RFIDCardError(Exception):
    def __init__(self, errType):
        self.message = "Nieoczekiwany bład karty RFID. ErrCode = " + errType 
        if errType == "-100" or errType == "-8":
            self.message = "Sukces (ErrCode = " + errType + ")"
        elif errType == "-1":
            self.message = "Błąd uwierzytelniania karty. (ErrCode = " + errType + ")"
        elif errType == "-2":
            self.message = "Przekroczono maksymalny czas oczekiwania na odpowiedź. (ErrCode = " + errType + ")"
        elif errType == "-3":
            self.message = "Wystąpił problem z dostępem danych karty. (ErrCode = " + errType + ")"
        elif errType == "-4":
            self.message = "Niepoprawny identyfikator użytkownika. (ErrCode = " + errType + ")"
        elif errType == "-5":
            self.message = "Za mało znaków. (ErrCode = " + errType + ")"
        elif errType == "-6":
            self.message = "Za dużo znaków. (ErrCode = " + errType + ")"
        elif errType == "-7":
            self.message = "Wystąpił problem z zapisem danych do karty. Spróbuj ponownie. (ErrCode = " + errType + ")"
        elif errType == "-9":
            self.message = "Błąd czytnika RFID (ErrCode = " + errType + ")"
        pass

class NoSpecifiedParamsError(Exception):
    def __init__(self, paramName):
        self.message = "Brak parametru: " + paramName
        pass
