import os

from src.data_extr import check_csv, create_csv

def check_for_year(year) -> None:
    base_path = os.getcwd()
    year_str = str(year)
    if os.path.exists("".join([base_path,"/Jahre"])): # if "Jahre"-Folder exists
        if os.path.exists("".join([base_path,"/Jahre/",year_str])): # if jahr existis
            check_for_members(year)
            check_for_transfers(year)   
        else:
           make_year(year)

    else:
        os.mkdir("".join([base_path,"/Jahre"]))
        make_year(year)

def check_for_members(year)-> None:
    year_str = str(year)
    member_path = "".join([os.getcwd(),"/Jahre/",year_str,"/mitglieder.csv"])
    if os.path.exists(member_path): # falls mitgliedertabelle existiert
        res = check_csv(member_path, "member")
    else:
        create_csv(member_path,"member") # beispiel mitgliedertabelle wird erstellt

def check_for_transfers(year) -> None:
    year_str = str(year)
    transfer_path = "".join([os.getcwd(),"/Jahre/",year_str,"/ueberweisungen"])
    if os.path.exists(transfer_path): 
        # LATER: transfer docs to csv
        for doc in os.listdir(transfer_path):
            doc_path = "".join([transfer_path,"/",doc])
            if check_csv(doc_path,"transfer"):
                pass
            else:
                break
        
        if len(os.listdir(transfer_path))==0:
            path = "".join([transfer_path,"/umsaetze.csv"])
            create_csv(path,"transfer")

    else:
        os.mkdir(transfer_path)
        path = "".join([transfer_path,"/umsaetze.csv"])
        create_csv(path,"transfer")

def make_year(year) -> None:
    base_path = os.getcwd()
    year_str = str(year)
    year_path = "".join([base_path,"/Jahre/",year_str])
    os.mkdir(year_path)

    member_path = "".join([year_path,"/mitglieder.csv"])
    create_csv(member_path, "member")
    
    os.mkdir("".join([year_path,"/ueberweisungen"]))
    transfer_path = "".join([year_path,"/ueberweisungen/","umsaetze.csv"])
    create_csv(transfer_path,"transfer")