import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)

from src.classes import Solawista, Year


global months_dict
months_dict = {"Januar":{},"Februar":{},"März":{},"April":{},"Mai":{},"Juni":{},"Juli":{},"August":{},"September":{},"Oktober":{},"November":{},"Dezember":{}}
global num_to_month 
num_to_month = {1:"Januar",2:"Februar",3:"März",4:"April",5:"Mai",6:"Juni",7:"Juli",8:"August",9:"September",10:"Oktober",11:"November",12:"Dezember"}

def payment_overview(year_obj,months=False) -> pd.DataFrame:
        res_dict = {}
        if months:
            red_months = {k:months_dict[k] for k in list(months_dict)[year_obj.year_info['start']-1:year_obj.year_info['end']] if k in months_dict}
            cols = ['vorname','name'] + list(red_months.keys()) + ['betrag_anteile','betrag_erwartet','betrag_einlage','zahlungen_gesamt']
            for key, solawista in year_obj.solawistas.items():
                expected = solawista.betrag*(len(solawista.months_paid))
                content_list = [solawista.vorname, solawista.name]+list(solawista.months_paid.values())+[solawista.betrag_anteile,expected,solawista.betrag_einlage,solawista.zahlungen_gesamt]
                res_dict[solawista.id] = content_list
        else:
            cols = ['vorname','name','betrag_anteile','betrag_erwartet','betrag_einlage','zahlungen_gesamt']
            for key, solawista in year_obj.solawistas.items():
                expected = solawista.betrag*(len(solawista.months_paid))
                content_list = [solawista.vorname, solawista.name, solawista.betrag_anteile,expected,solawista.betrag_einlage,solawista.zahlungen_gesamt]
                res_dict[solawista.id] = content_list

        return pd.DataFrame.from_dict(res_dict, orient='index',columns=cols)

def create_year_overview(year_obj):
    res_dict = {}
    cols = ['num','status','vorname','name','betrag_anteile','betrag_erwartet','diff','betrag_einlage','zahlungen_gesamt']
    for key, solawista in year_obj.solawistas.items():
                expected = solawista.betrag*(len(solawista.months_paid))*solawista.num_ant
                diff = solawista.betrag_anteile - expected

                content_list = [solawista.id, solawista.status, solawista.vorname, solawista.name, solawista.betrag_anteile,expected,diff,solawista.betrag_einlage,solawista.zahlungen_gesamt]
                res_dict[solawista.id] = content_list
    return pd.DataFrame.from_dict(res_dict, orient='index',columns=cols)
