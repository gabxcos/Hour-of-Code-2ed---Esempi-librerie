from tkinter import *
from tkinter import ttk


# elemento ROOT 
root = Tk()
root.title("Calcolatrice")
root.resizable(False, False)

# elemento FRAME
frame = ttk.Frame(root, padding=10)
frame.grid()

# --- STILI ----------------------------------------------
NUMBER_STYLE = ttk.Style() # PULSANTI NUMERICI
NUMBER_STYLE.configure('NUMBER.TButton', foreground="black", font=("Helvetica", 18)) 

OPERATOR_STYLE = ttk.Style() # PULSANTI DI OPERATORI
OPERATOR_STYLE.configure('OPERATOR.TButton', foreground="orange", font=("Helvetica", 20, "bold"))

LABEL_STYLE = ttk.Style() # TESTO DEL RISULTATO
LABEL_STYLE.configure('LABEL.TLabel', foreground="black", font=("Helvetica", 18))

# --- VARIABILI ------------------------------------------

# COSTANTI di CREAZIONE:
elements = ["7", "8", "9", "/", "4", "5", "6", "X", "1", "2", "3", "-", ",", "0", "=", "+"]
operators = ["/", "X", "-", "+", "="]

# Testo del risultato
shown_text = StringVar()
shown_text.set("0")

# Operandi e operatore scelti
operand1 = "0"
operator = ""
operand2 = ""

# --- FUNZIONI -------------------------------------------

# Funzioni di aggiornamento dello stato delle variabili
def updateOps(newOp):
    """Effettua il calcolo fra i due operandi, setta il nuovo operatore"""
    global shown_text, operand1, operator, operand2

    result = None
    try:
        result = eval(operand1+operator+operand2)
        operand1 = "{:.4f}".format(result) if (result-result//1)>0 else "{:d}".format(int(result)) # Formatta in base alla presenza o meno di cifre decimali
        operator = newOp if newOp!="=" else ""
        operand2 = "0" if newOp!="=" else ""

        print(result)
    except ZeroDivisionError:
        print("Non posso dividere per zero!")

def updateTextShown():
    """Aggiorna il testo mostrato nella Label"""
    global operand1, operator, operand2

    string = operand1
    if operator:
        string += " " + operator + "\n" + operand2

    shown_text.set(string)

# Funzioni di comando associate ai bottoni
def numberPress(num):
    """Per bottoni numerici: aggiorna l'operando correntemente esposto"""
    global operand1, operand2

    string = operand1 if operand2=="" else operand2 # decidi su quale operando si lavora

    # Aggiorna la stringa
    if string == "0" and num!=",":
        string = num
    elif num==",": 
        if not ("." in string):
            string = string+"."
    else:
        string = string+num
    
    # Imposta la stringa aggiornata sull'operando corretto
    if operand2=="":
        operand1 = string
    else:
        operand2 = string

def operatorPress(op):
    """Per bottoni di operazione: setta la modifica del secondo operando e/o calcola la funzione attualmente mostrata"""
    global operator, operand2

    # "X" in Python usa "*"
    if op=="X":
        op = "*"

    # Se non è settato alcun operatore, passiamo alla modifica del secondo operando
    if operator=="":
        if op!="=":
            operator = op
            operand2 = "0"
    # Altrimenti, effettuiamo il calcolo e settiamo il nuovo operatore
    else:
        updateOps(op)


def buttonPress(value):
    """Gestisce la pressione di un qualunque bottone, dato il suo valore"""
    global operand1, operator, operand2

    # Se il bottone premuto è un operatore
    if value in operators:
        operatorPress(value)
        print("premuto operatore")
    # Se il bottone premuto è numerico
    else:
        numberPress(value)
        print("premuto operand")

    # Aggiorna la Label
    updateTextShown()
    print("Premuto: "+value) # per Debug

def cancelPress():
    """Resetta tutte le variabili al loro posto"""
    global shown_text, operand1, operator, operand2
    
    shown_text.set("0")
    operand1 = "0"
    operator = ""
    operand2 = ""
    updateTextShown()


# --- POPOLAMENTO ----------------------------------------

# BOTTONE DI CANCELLAZIONE
cancel_button = ttk.Button(frame, text="Canc", style="OPERATOR.TButton", command=cancelPress)
cancel_button.grid(column=0, row=0, columnspan=1, padx=5, pady=5, ipady=10)

# RIGA DI TESTO DEL RISULTATO
result = ttk.Label(frame, textvariable=shown_text, style="LABEL.TLabel")
result.grid(column=1, row=0, columnspan=3, padx=5, pady=15, sticky="e") # prende le 4 colonne della prima riga, allineato a destra

# GRIGLIA DEI BOTTONI
buttons = []
for index, el in enumerate(elements):
    buttons.append(None)
    buttons[index] = ttk.Button(frame, text=el, style="OPERATOR.TButton" if (el in operators) else "NUMBER.TButton", command=lambda el=el : buttonPress(el))
    buttons[index].grid(column=index%4, row=(index//4)+1, padx=5, pady=5, ipady=10)


# --- MAINLOOP ------------------------------------------
root.mainloop()