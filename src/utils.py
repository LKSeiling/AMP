import os
import re
import pickle
import pandas as pd
from IPython.display import clear_output

def handle_numbers(num_string) -> float:
    res = num_string.replace(".","")
    res = float(res.replace(",","."))
    return res

def make_timeStamp(x):
    x_parts = x.split(".")
    return pd.Timestamp(day=int(x_parts[0]), month=int(x_parts[1]), year=int(x_parts[2]))

def clean_vzweck(input_str) -> str:
    split_str = input_str.split("\n")
    clean_str = "".join(split_str[1:])
    clean_str = clean_str.replace("'","").replace(".","")
    clean_str = re.sub('\W*EREF\W*.*', '', clean_str)
    return clean_str

def standardise_str(input_str) -> str:
    res_str = input_str.lower()
    res_str = res_str.replace("ü","ue").replace("ä","ae").replace("ö","oe")
    return res_str

def get_num_id(input_str) -> int:
    return int(re.search('\d{3}',input_str).group())

    
def ask_for_input(input_type):
    if input_type == "purpose":
        res = get_purpose()
    elif input_type == "year":
        res = get_year()
    elif input_type == "classify":
        res = classify_transfer()
    elif input_type == "num_splits":
        res = get_num_splits()
    else:
        res = None
    return res

def get_purpose() -> str:
    purp = input("Bitte gib den Posten für die angezeigte Überweisung an. ").lower()
    if (purp == "e") or (purp == "a") or (purp == "s") or (purp == ""):
        if purp == "e": out_str = "einlage"
        elif purp == "a": out_str = "anteil"
        elif purp == "s": out_str = "sonstige"
        else: out_str = purp
    else:
        print("Deine Eingabe muss entweder 'A', 'E', 'S' oder Enter sein. Bitte versuche es nochmal.")
        purp = get_purpose()
    return out_str

def get_year() -> int:
    year = input("Bitte wähle ein Jahr aus. ")
    try:
        year = int(year)
    except:
        print("Das Jahr, was du gewählt hast, kann nicht in eine Zahl konvertiert werden.")
        year = get_year()
    return year

def get_num_splits() -> int:
    inpt = input("In wie viele Teile soll die Überweisung geteilt werden?")
    try:
        inpt = int(inpt)
        if inpt < 0:
            print("Bitte gib eine ganze Zahl größer 0 an.")
            inpt = get_num_splits()
    except:
        print("Bitte gib eine ganze Zahl an.")
        inpt = get_num_splits()
    return inpt


def classify_transfer():
    inpt = input("Bitte ordne die angezeigte Überweisung entsprechend zu.\nGib 'x' ein, um die Zuordnung abzubrechen.").lower()
    try:
        inpt = int(inpt)
    except:
        if (inpt == "w") or (inpt == "t") or (inpt == "a") or (inpt == "d") or (inpt == "g") or (inpt == "") or (inpt == "x") or (inpt == "z"):
            pass
        else:
            print("Deine Eingabe muss entweder eine Zahl, 'T', 'W', 'D', 'A', 'G', 'X' oder Enter sein. Bitte versuche es nochmal.")
            inpt = classify_transfer()
    return inpt

def get_subtransfer_value(idx,max_val):
    inpt = input("Wie viel Geld soll auf die {}. Unterüberweisung entfallen?".format(idx))
    try:
        inpt = int(inpt)
        if max_val-inpt <= 0:
            print("Bitte gib eine ganze Zahl an, die kleiner ist als der restliche Betrag (maximal {}).".format(max_val))
            inpt = get_subtransfer_value(idx,max_val)
    except:
        print("Bitte gib eine ganze Zahl an.")
        inpt = get_subtransfer_value(idx,max_val)
    return inpt

def clear_console() -> None:
    clear_output()

def save_year(year) -> None:
    base_path = os.getcwd()
    file_str = '/{year}/{year}.pkl'.format(year=year.value)
    save_str = "".join([base_path,"/Jahre",file_str])
    with open(save_str, 'wb') as file:
        pickle.dump(year, file)

def read_year(year_num):
    base_path = os.getcwd()
    file_str = '/{year}/{year}.pkl'.format(year=year_num)
    load_str = "".join([base_path,"/Jahre",file_str])
    with open(load_str, 'rb') as file:
        return pickle.load(file)