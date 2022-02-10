import re

from src.classes import Year
from src.utils import clean_vzweck, standardise_str, get_num_id, save_year, ask_for_input, clear_console


def auto_assign(year_obj) -> Year:
    names_dict = {solawista.name: {"vorname":solawista.vorname, "id":solawista.id} for key, solawista in year_obj.solawistas.items()}
    id_list = [solawista for solawista in year_obj.solawistas]

    for key, transfer in year_obj.all_transfers.items():
        if transfer.sorted == "" and transfer.value >0:
            id_dict = try_assignment(transfer,id_list,names_dict)
            if id_dict['bool']:
                year_obj.solawistas[id_dict['id']].add_transfer(transfer)
            else:
                pass
        elif any(match_str in standardise_str(transfer.vzweck) for match_str in ['basislast', 'kunde', 'rechnung', 'abschluss','pacht']):
            month = transfer.get_month("str")
            transfer.set_sorted("a")
            year_obj.ausgaben[month][transfer.id] = transfer
    save_year(year_obj)
    return year_obj

def try_assignment(transfer, ids, names):
    id_dict = check_for_id_fit(transfer.vzweck,ids)
    if not id_dict['bool']:
        id_dict = check_for_name_fit(transfer.vzweck,names)
        if not  id_dict['bool']:
            id_dict = check_for_name_fit(str(transfer.for_from),names)
    return id_dict

def check_for_id_fit(str_vzweck, ids):
    t_vzweck = clean_vzweck(str_vzweck)
    id_pattern = re.compile("(\s|[^\w|-]){1,}\d{3}(\s|[^\w|,]){1,}") # definiert Muster (drei Zahlen umgeben von / oder Leerzeichen)

    if re.search(id_pattern, t_vzweck): # prüfe, ob Muster in Verwendungszweck
        input_str = re.search(id_pattern, t_vzweck).group()
        id_num = get_num_id(input_str)
        if id_num in ids:
            id_dict = {"bool":True,"id":id_num}
        else: 
            id_dict = {"bool":False}
    else:
        id_dict = {"bool":False}
    return id_dict


def check_for_name_fit(input_str, names_dict) -> dict:
    res = [surname for surname in names_dict.keys() if(standardise_str(surname) in standardise_str(input_str))]
    if len(res) > 1:
        res = [name for name in res if(standardise_str(names_dict[name]['vorname']) in standardise_str(input_str))]
    
    if len(res)==1:
        id_dict = {"bool":True,"id":names_dict[res[0]]["id"]}
    else:
        id_dict = {"bool":False}
    return id_dict

def manual_assign(year_obj) -> Year:
    for key, transfer in year_obj.all_transfers.items():
        if transfer.sorted == "":
            print(transfer)
            id_out = ask_for_input("classify")
            assign_to_container(year_obj,transfer,id_out)
        
            if id_out == "t":
                num_transfers = ask_for_input("num_splits")
                transfer.create_subtransfers(num_transfers)
                for key, subtransfer in transfer.subtransfers.items():
                    clear_console()
                    print(subtransfer)
                    sub_id_out = ask_for_input("classify")
                    assign_to_container(year_obj,subtransfer,sub_id_out)
                    subtransfer.set_sorted(sub_id_out)
            elif id_out == "":
                pass
            elif id_out == "x":
                save_year(year_obj)
                clear_console()
                break
            transfer.set_sorted(id_out)
            clear_console()
                
    save_year(year_obj)
    return year_obj

def assign_to_container(year_obj,transfer,id_out):
    month = transfer.get_month("str")
    if type(id_out) == int:
        transfer.count_towards = ask_for_input("purpose")
        year_obj.solawistas[id_out].add_transfer(transfer)
    elif id_out == "w":
        year_obj.warteschlange[month][transfer.id] = transfer
    elif id_out == "d":
        year_obj.darlehen[month][transfer.id] = transfer
    elif id_out == "a":
        month = transfer.get_month("str")
        year_obj.ausgaben[month][transfer.id] = transfer
    elif id_out == "g":
        year_obj.gehaelter[month][transfer.id] = transfer
    elif id_out == "z":
        year_obj.zuwendungen[month][transfer.id] = transfer