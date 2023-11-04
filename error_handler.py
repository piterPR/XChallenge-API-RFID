import serial

errorCodes = [
    "-100", # Sukces
    "-1",   # Błąd uwierzytelniania karty
    "-2",   # Timeout
    "-3",   # Problem z dostępem do danych karty
    "-4",   # Niepoprawny identyfikator użytkownika
    "-5",   # Za mało znaków
    "-6",   # Za dużo znaków
    "-7",   # Problem z zapisem danych do karty
    "-8",   # Sukces
    "-9",   # Błąd czytnika RFID
    "-10",  # Nie otworzono portu szeregowego
    "-11",  # Nie znaleziono podlaczonego ESP
    "-12",  # Pattern
    "-13",  # Brak wymaganych danych
    "-14"   # Nierozpoznany błąd
]

def buildResponseMessage(body, errCode, status = "Error"):
    return {"body": body, "status": status, "code": int(errCode)}

def check_is_error_code(stringValue):
    finded = None
    for value in errorCodes:
        if value in stringValue:
            finded = value
            break
    return finded

def error_handler(error):
    if isinstance(error, serial.serialutil.PortNotOpenError):
        message = buildResponseMessage("Nie otworzono portu szeregowego.", "-10")
        print(message)
        return message
    elif isinstance(error, MaxTimeoutError):
        message = buildResponseMessage("Przekroczono maksymalny czas oczekiwania na odpowiedź.", "-2")
        print(message)
        return message
    elif isinstance(error, NoCOMPortFindedError):
        message = buildResponseMessage("Nie znaleziono podlaczonego ESP", "-11")
        print(message)
        return message
    elif isinstance(error, WrongPatternError):
        message = buildResponseMessage(error.message, "-12")
        print(message)
        return message
    elif isinstance(error, RFIDCardError):
        message = error.message
        print(message)
        return message
    elif isinstance(error, NoSpecifiedParamsError):
        message = buildResponseMessage(error.message, "-13")
        print(message)
        return message
    else:
        message = buildResponseMessage("Wystąpił nieoczekiwany bład: " + str(error), "-14")
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
            self.message = buildResponseMessage("Sukces (ErrCode = -100)",errType, "Sukces")
        elif errType == "-1":
            self.message = buildResponseMessage("Błąd uwierzytelniania karty. (ErrCode = " + errType + ")",errType)
        elif errType == "-2":
            self.message = buildResponseMessage("Przekroczono maksymalny czas oczekiwania na odpowiedź. (ErrCode = " + errType + ")",errType)
        elif errType == "-3":
            self.message = buildResponseMessage("Wystąpił problem z dostępem do danych karty. (ErrCode = " + errType + ")",errType)
        elif errType == "-4":
            self.message = buildResponseMessage("Niepoprawny identyfikator użytkownika. (ErrCode = " + errType + ")",errType)
        elif errType == "-5":
            self.message = buildResponseMessage("Za mało znaków. (ErrCode = " + errType + ")",errType)
        elif errType == "-6":
            self.message = buildResponseMessage("Za dużo znaków. (ErrCode = " + errType + ")",errType)
        elif errType == "-7":
            self.message = buildResponseMessage("Wystąpił problem z zapisem danych do karty. Spróbuj ponownie. (ErrCode = " + errType + ")",errType)
        elif errType == "-9":
            self.message = buildResponseMessage("Błąd czytnika RFID (ErrCode = " + errType + ")",errType)
        pass

class NoSpecifiedParamsError(Exception):
    def __init__(self, paramName):
        self.message = "Brak parametru: " + paramName
        pass
