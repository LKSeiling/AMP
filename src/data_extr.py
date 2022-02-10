import pandas as pd
import os

from src.classes import Year
from src.utils import handle_numbers, make_timeStamp

truth_dict = {
    "member": ['num','status','nachname','vorname','mail','phone','iban','year','year_start','year_end','ant','betrag','turnus','typ_einlage','depot','kommentar'],
    "transfer": ['Buchungstag','Valuta','Auftraggeber/Zahlungsempfänger','Empfänger/Zahlungspflichtiger','Konto-Nr.','IBAN','BLZ','BIC','Vorgang/Verwendungszweck','Kundenreferenz','Währung','Umsatz','InOut']
}

def check_csv(csv_path,tbl_type,verbose=True) -> bool:
    csv_df= pd.read_csv(csv_path)
    if isEmpty(csv_df):
        if verbose: print("Die Datei {} enthält keine Daten.\nBitte prüfen und diese Zelle nochmals ausführen.\n".format(csv_path))
        return False
    elif wrongHeader(csv_df,tbl_type):
        if verbose: print("Die Datei {} hat nicht die richtigen Spalten.\nSie darf nur die Spalten {} enthalten.\nBitte prüfen und diese Zelle nochmals ausführen.\n".format(csv_path, truth_dict[tbl_type]))
        return False
    else:
        if verbose: print("Die Datei {} enthält Daten und hat das richtige Format.\n".format(csv_path))
        return True

def isEmpty(csv_df) -> bool:
    if len(csv_df) < 2:
        return True
    return False

def wrongHeader(csv_df,tbl_type) -> bool:
    if any(csv_df.columns != truth_dict[tbl_type]):
        return True
    return False

def create_csv(csv_path, tbl_type) -> None:
    new_data = pd.DataFrame(columns=truth_dict[tbl_type])
    new_data.to_csv(csv_path, index=False,encoding="utf-8")

def import_data(curr_year,total_ants,year_start=1,year_end=12):
    year_str = str(curr_year)
    base_path = "".join([os.getcwd(),"/Jahre/",year_str])
    member_path = "".join([base_path,"/mitglieder.csv"])
    transfer_path = "".join([base_path,"/ueberweisungen/"])

    erntejahr = Year(curr_year,total_ants,year_start,year_end)
    erntejahr = import_solawistas(erntejahr, member_path,year_start,year_end)
    erntejahr = import_transfers(erntejahr,transfer_path)
    return erntejahr

def import_solawistas(year_obj,file_path,year_start,year_end) -> Year:
    member_data = pd.read_csv(file_path)
    for idx, row in member_data.iterrows():
        start_date = year_start if pd.isna(row['year_start']) else row['year_start']
        end_date = year_end if pd.isna(row['year_end']) else row['year_end']
        
        init_dict = {'id':row['num'],'status':row['status'],'name':row['nachname'],'vorname':row['vorname'],'depot':row['depot'],'seit':row['year'],'year_start':start_date,'year_end':end_date,'num_ant':row['ant'],'betrag':row['betrag'],'turnus':row['turnus'],'kontakt':{"mail":row['mail'],"phone":row['phone']},'iban':row['iban'],'typ_einlage':row['typ_einlage'],'kommentar':row['kommentar']}
        year_obj.add_solawista(init_dict,year_obj.value)
    return year_obj
    

def import_transfers(year_obj, file_path):
    if os.path.exists(file_path): 
        # later: add check if transfers are already known, only increment id-counter if not, set counter accordingly
        trnsfr_idx = 0
        for doc in os.listdir(file_path):
            doc_path = "".join([file_path,"/",doc])
            if check_csv(doc_path,"transfer",verbose=False):
                transfer_data = pd.read_csv(doc_path)
                for idx, row in transfer_data.iterrows():
                    betrag = handle_numbers(row['Umsatz'])
                    date = make_timeStamp(row['Buchungstag'])
                    if row['InOut'] == "S":
                        betrag = betrag*-1
                    init_dict = {'id':trnsfr_idx,'day':date,'value':betrag,'for_from':row['Empfänger/Zahlungspflichtiger'],'vzweck':row['Vorgang/Verwendungszweck'],'iban':row['IBAN'],'bic':row['BIC']}
                    year_obj.add_transfer(init_dict)
                    trnsfr_idx = trnsfr_idx + 1
            else:
                print("Dokument {0} kann nicht gelesen werden. Bitte öffne eine neue Zelle und gebe 'check_csv({0},'transfer')' ein, um die Datei erneut zu prüfen.".format(doc_path))
    return year_obj
