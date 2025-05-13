def printwarning(warning):
    print(f"Warining: {warning}")

def printerror(error):
    print(f"Error: {error}")

def printsth(func, sent):
    func(sent)

printsth(printwarning, "TEST")
printsth(printerror, "TEST")
