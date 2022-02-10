from copy import deepcopy
from os import remove
import pandas as pd

from src.utils import clean_vzweck, clear_console, standardise_str, ask_for_input, clear_console, get_subtransfer_value



global months_dict
months_dict = {"Januar":{},"Februar":{},"März":{},"April":{},"Mai":{},"Juni":{},"Juli":{},"August":{},"September":{},"Oktober":{},"November":{},"Dezember":{}}
global num_to_month 
num_to_month = {1:"Januar",2:"Februar",3:"März",4:"April",5:"Mai",6:"Juni",7:"Juli",8:"August",9:"September",10:"Oktober",11:"November",12:"Dezember"}


class Year:
    def __init__(self, year_val,total_ants,year_start,year_end) -> None:
        self.value = year_val
        self.anteile = total_ants
        self.solawistas = {}
        self.all_transfers = {}
        self.year_info = {"start":year_start,"end":year_end}

        self.warteschlange = deepcopy(months_dict)
        self.darlehen = deepcopy(months_dict)
        self.spenden = deepcopy(months_dict)
        self.zuwendungen = deepcopy(months_dict)

        self.ausgaben = deepcopy(months_dict)
        self.gehaelter = deepcopy(months_dict)

    def __str__(self):
        return """YEAR {val} (Monate {start} bis {end})
        ANTEILE: {calc_ant} von {ant}

        ANZAHL ALLER ÜBERWEISUNGEN: {all}
        davon NICHT ZUGEORDNET: {calc_unassigned}
        davon ZUGEORDET: {calc_assigned}
            davon in WARTESCHLANGE: {l_ws}
            
        """.format(val=self.value,start=self.year_info['start'], end=self.year_info['end'], calc_ant=self.get_filled_anteile(), ant=self.anteile, all=len(self.all_transfers),calc_assigned=len(self.all_transfers)-self.num_unsorted(), l_ws=len(self.warteschlange), calc_unassigned=self.num_unsorted())

    def __repr__(self):
        return """YEAR {val} (Monate {start} bis {end})
        ANTEILE: {calc_ant} von {ant}

        ANZAHL ALLER ÜBERWEISUNGEN: {all}
        davon NICHT ZUGEORDNET: {calc_unassigned}
        davon ZUGEORDET: {calc_assigned}
            davon in WARTESCHLANGE: {l_ws}
            
        """.format(val=self.value,start=self.year_info['start'], end=self.year_info['end'], calc_ant=self.get_filled_anteile(), ant=self.anteile, all=len(self.all_transfers),calc_assigned=len(self.all_transfers)-self.num_unsorted(), l_ws=len(self.warteschlange), calc_unassigned=self.num_unsorted())

    def add_solawista(self,init_dict,year_num,):
        solawista = Solawista(init_dict,year_num)
        self.solawistas[solawista.id] = solawista

    def add_transfer(self, init_dict):
        transfer = Transfer(init_dict)
        self.all_transfers[transfer.id] = transfer

    def num_unsorted(self) -> int:
        count=0
        for key, transfer in self.all_transfers.items():
            if transfer.sorted =="":
                count = count+1
        return count

    def get_filled_anteile(self) -> int:
        sum_betr = 0
        for idx,solawista in self.solawistas.items():
            sum_betr = sum_betr + solawista.num_ant
        return sum_betr

    def remove_transfer(self, trnsfr_id) -> None:
        if trnsfr_id in list(self.all_transfers.keys()):
            transfer = self.all_transfers[trnsfr_id]
            month = transfer.get_month("str")

            if type(transfer.sorted) == int:
                self.remove_from_solawista(transfer)
            
            elif transfer.sorted == "w":
                del self.warteschlange[month][transfer.id]
            elif transfer.sorted == "a":
                del self.ausgaben[month][transfer.id]
            elif transfer.sorted == "s":
                del self.spenden[month][transfer.id]
            elif transfer.sorted == "d":
                del self.darlehen[month][transfer.id]
            elif transfer.sorted == "g": 
                del self.gehaelter[month][transfer.id]
            elif transfer.sorted == "z": 
                del self.zuwendungen[month][transfer.id]
        
            elif transfer.sorted == "t":
                for subtransfer in transfer.subtransfers:
                    self.remove_subtransfer(subtransfer)
            
            transfer.reset()

        else:
            print("Es gibt keine Überweisung mit der ID {}".format(trnsfr_id))

    def move_transfer(self, trnsfr_id, loc_list) -> None:
        self.remove_transfer(trnsfr_id)
        trnsfr = self.all_transfers[trnsfr_id]

        if type(loc_list[0]) == int:
            trnsfr.count_towards = loc_list[1]
            self.solawistas[loc_list[0]].add_transfer(trnsfr)
        else:
            month = trnsfr.get_month("str")
            if loc_list[0] == "w":
                self.warteschlange[month][trnsfr.id] = trnsfr
            elif loc_list[0] == "a":
                self.ausgaben[month][trnsfr.id] = trnsfr
            elif loc_list[0] == "d":
                self.darlehen[month][trnsfr.id] = trnsfr
            elif loc_list[0] == "g":
                self.gehaelter[month][trnsfr.id] = trnsfr
            elif loc_list[0] == "z":
                self.zuwendungen[month][trnsfr.id] = trnsfr
        
        trnsfr.set_sorted(loc_list[0])

    
    def remove_from_solawista(self,transfer):
        month = self.solawistas[transfer.sorted].determine_month(transfer)
        if transfer.count_towards == "einlage":
            del self.solawistas[transfer.sorted].payments_einlage[month][transfer.id]
        elif transfer.count_towards == "anteil":
            del self.solawistas[transfer.sorted].payments[month][transfer.id]
        elif transfer.count_towards == "sonstige":
            del self.solawistas[transfer.sorted].payments_sonstige[transfer.id]

        solawista_id = transfer.sorted
        transfer.reset()
        self.solawistas[solawista_id].sum_up_transfers()

    def remove_subtransfer(self,subtransfer):
        month = subtransfer.get_month("str")

        if type(subtransfer.sorted) == int:
            self.remove_from_solawista(subtransfer)
        
        elif subtransfer.sorted == "w":
            del self.warteschlange[month][subtransfer.id]
        elif subtransfer.sorted == "a":
            del self.ausgaben[month][subtransfer.id]
        elif subtransfer.sorted == "s":
            del self.spenden[month][subtransfer.id]
        elif subtransfer.sorted == "d":
            del self.darlehen[month][subtransfer.id]
        elif subtransfer.sorted == "g": 
            del self.gehaelter[month][subtransfer.id]
        elif subtransfer.sorted == "z": 
            del self.zuwendungen[month][subtransfer.id]







class Solawista:
    def __init__(self, init_dict,year_num) -> None:
        self.id = init_dict["id"]
        self.status = init_dict['status']

        self.name = init_dict['name']
        self.vorname = init_dict['vorname']
        self.depot = init_dict['depot']
        self.seit = init_dict['seit']

        self.num_ant = init_dict['num_ant']
        self.betrag = init_dict['betrag']
        self.turnus = init_dict['turnus']

        self.year = year_num
        self.year_start=init_dict['year_start']
        self.year_end=init_dict['year_end']

        self.verteiler = []
        self.contact = init_dict['kontakt']
        self.iban = init_dict['iban']
        self.comments = []
        self.comments.append(init_dict['kommentar'])

        self.payments = {}
        self.months_paid = {}
        self.payments_einlage = {}
        self.payments_sonstige = {}

        self.typ_einlage = init_dict['typ_einlage']
        self.betrag_einlage = 0
        self.betrag_anteile = 0
        self.zahlungen_gesamt = 0

        self.transfers = [] # alle dieser Solawista zugewiesenen Überweisungen


    def __str__(self):
        return """SOLAWISTA DATEN FÜR DAS JAHR {year}
        {id}: {vorname} {nachname}
        -------------------------------
        Depot:{depot}, seit:{since}, status:{status}
        Anteile:{num_ant}, Gebot:{betrag}, Turnus:{turnus}, Typ Einlage:{typ_einlage}
        Telefon:{tel}, Email: {mail}
        Verteiler:{vert}
        IBAN:{iban}
        -------------------------------
        GESAMTBETRAG ANTEILE: {gesamt} von {expected}
        MONATE GEZAHLT:{months_paid}
        bisher zugewiesene ÜBERWEISUNGEN für ANTEILE: {transfers}

        BETRAG EINLAGE: {sum_einlage}
        bisher zugewiesene ÜBERWEISUNGEN für EINLAGE: {transfers_einlage}

        SONSTIGE Überweisungen: {other}

        ZAHLUNGEN GESAMT: {all_payments}
        -------------------------------
        Kommentare:{comments}


        """.format(year=self.year,id=self.id,vorname=self.vorname,nachname=self.name,depot=self.depot,since=self.seit,status=self.status,num_ant=self.num_ant,betrag=self.betrag,turnus=self.turnus,typ_einlage=self.typ_einlage,tel=self.contact['phone'], mail=self.contact['mail'], vert=self.verteiler,iban=self.iban,gesamt=self.betrag_anteile,expected=self.betrag*(len(self.months_paid)),months_paid=self.months_paid,sum_einlage=self.betrag_einlage,transfers_einlage=self.payments_einlage,all_payments=self.zahlungen_gesamt, transfers = self.payments,comments=self.comments,other=self.payments_sonstige)

    def __repr__(self):
        return """SOLAWISTA DATEN FÜR DAS JAHR {year}
        {id}: {vorname} {nachname}
        -------------------------------
        Depot:{depot}, seit:{since}, status:{status}
        Anteile:{num_ant}, Gebot:{betrag}, Turnus:{turnus}, Typ Einlage:{typ_einlage}
        Telefon:{tel}, Email: {mail}
        Verteiler:{vert}
        IBAN:{iban}
        -------------------------------
        GESAMTBETRAG ANTEILE: {gesamt} von {expected}
        MONATE GEZAHLT:{months_paid}
        bisher zugewiesene ÜBERWEISUNGEN für ANTEILE: {transfers}

        BETRAG EINLAGE: {sum_einlage}
        bisher zugewiesene ÜBERWEISUNGEN für EINLAGE: {transfers_einlage}

        SONSTIGE Überweisungen: {other}

        ZAHLUNGEN GESAMT: {all_payments}
        -------------------------------
        Kommentare:{comments}


        """.format(year=self.year,id=self.id,vorname=self.vorname,nachname=self.name,depot=self.depot,since=self.seit,status=self.status,num_ant=self.num_ant,betrag=self.betrag,turnus=self.turnus,typ_einlage=self.typ_einlage,tel=self.contact['phone'], mail=self.contact['mail'], vert=self.verteiler,iban=self.iban,gesamt=self.betrag_anteile,expected=self.betrag*(len(self.months_paid)),months_paid=self.months_paid,sum_einlage=self.betrag_einlage,transfers_einlage=self.payments_einlage,all_payments=self.zahlungen_gesamt, transfers = self.payments,comments=self.comments,other=self.payments_sonstige)

    def set_month_range(self):
        assert self.year_start>0 and self.year_end<13 and self.year_end > self.year_start
        if self.year_start!=1 or self.year_end!=12:
            red_dict = {k:months_dict[k] for k in list(months_dict)[self.year_start-1:self.year_end] if k in months_dict}
            self.payments = deepcopy(red_dict)
            self.payments_einlage = deepcopy(red_dict)
        else:
            self.payments = deepcopy(months_dict)
            self.payments_einlage = deepcopy(months_dict)
        self.months_paid = {k : False for k in self.payments}
            
    def add_transfer(self, transfer) -> None:
        if transfer.count_towards == "":
            transfer.count_towards = self.detect_transfer_purpose(transfer)

        if transfer.count_towards == "":
            pass
        else:
            transfer.set_sorted(self.id)
            self.transfers.append(transfer)
            self.sum_up_transfers()

    def add_verteiler(self, vert_str) -> None:
        self.verteiler.append(vert_str)

    def add_comment(self, comm_str) -> None:
        self.comments.append(comm_str)
    
    def sum_up_transfers(self) -> None:
        # resetting and running this loop everytime a transfer is added or removed from a solawista serves to ensure that the calculations are aways up to date with the currently associated data
        self.transfers = list(set(self.transfers))
        self.payments_einlage = {}
        self.payments_sonstige = {}

        sum_einlage, sum_beitraege, sum_total = 0,0,0
        self.set_month_range()

        for transfer in self.transfers:
            if transfer.count_towards == "einlage":
                sum_einlage = sum_einlage+transfer.value
                self.betrag_einlage = sum_einlage
                self.add_to_payments(transfer,einlage=True)
            elif transfer.count_towards == "anteil":
                sum_beitraege = sum_beitraege+transfer.value
                self.betrag_anteile = sum_beitraege
                self.add_to_payments(transfer)
            elif transfer.count_towards == "sonstige":
                self.payments_sonstige[transfer.id] = transfer.value
            sum_total = sum_total+transfer.value
            self.zahlungen_gesamt = sum_total
        
        self.update_months_paid()

    def add_to_payments(self,transfer, einlage=False) -> None:
        month_str = self.determine_month(transfer)
        if einlage:
            self.payments_einlage[month_str][transfer.id] = transfer.value    
        else:
            self.payments[month_str][transfer.id] = transfer.value

    def determine_month(self,transfer) -> str:
        year_num = transfer.get_year()
        year_strings = list(self.payments.keys())
        if year_num < self.year:
            return year_strings[0]
        else:
            month_str = transfer.get_month("str")
            if month_str in year_strings:
                return month_str
            else:
                return year_strings[0]

    
    def update_months_paid(self) -> None:
        for month_str, payment_dict in self.payments.items():
            month_sum = 0
            for key, value in payment_dict.items():
                month_sum = month_sum+value       
            num_months = int(month_sum/self.betrag)
            month_index = list(months_dict).index(month_str)+1
            if month_sum > 0 and num_months < 2:
                self.add_paid_months(1,month_index)
            elif num_months >= 2:
                self.add_paid_months(num_months,month_index)


    def add_paid_months(self,num_months,month_index,backwards=False) -> None:
        # sloppy recursion could very likely be improved

        if num_months == 0:
            pass
        else:
            months_to_fill = self.determine_months_to_fill(num_months)
            if month_index >= self.year_start and month_index <= self.year_end:
                month_str = num_to_month[month_index]
                if not self.months_paid[month_str]:
                    cur_month_str = num_to_month[month_index]
                    self.months_paid[cur_month_str] = True
                    self.add_paid_months(months_to_fill-1,month_index+1)
                else:
                    if backwards:
                        self.add_paid_months(months_to_fill,month_index-1,backwards=True)
                    else:
                        self.add_paid_months(months_to_fill,month_index+1)
            else:
                if month_index > self.year_end: 
                    self.add_paid_months(months_to_fill,month_index-1,backwards=True)
                elif month_index < self.year_start: 
                    self.add_paid_months(months_to_fill,month_index+1)
            

    def determine_months_to_fill(self,num_months) -> int:
        num_months_paid = sum(self.months_paid.values())
        months_to_fill = num_months
        if num_months > self.year_end-(self.year_start-1) - num_months_paid: 
            months_to_fill = self.year_end-(self.year_start-1) - num_months_paid
        return months_to_fill

    def detect_transfer_purpose(self,transfer) -> str:
        clean_str = standardise_str(clean_vzweck(transfer.vzweck))
        if "einlage" in clean_str:
            if (self.betrag_einlage <= 250 and self.typ_einlage == "voll") or  (self.betrag_einlage <= 50 and self.typ_einlage == "reduziert"):
                out_str = "einlage"
            else:
                out_str = "anteil"
        elif "solaw" in clean_str:
            out_str = "anteil"
        else:
            print("{solawista}\n\n{trnsfr}".format(solawista=self,trnsfr=transfer))
            out_str = ask_for_input("purpose")
            clear_console()
        return out_str


class Transfer:
    def __init__(self, init_dict) -> None:
        if init_dict:
            self.id = init_dict["id"]
            self.day = init_dict["day"]
            self.value = init_dict["value"]
            self.for_from = init_dict["for_from"]
            self.vzweck = init_dict["vzweck"]
            self.iban = init_dict["iban"]
            self.bic = init_dict["bic"]
            self.sorted = ""
            self.count_towards = ""
            self.subtransfers = {}
            self.is_subtransfer = False

    def __str__(self):
        return """ÜBERWEISUNG {id}
        Datum:{tag}\tBetrag:{betrag}
        Empfänger/Sender: {for_from}
        Verwendungszweck:
        {vzweck}

        IBAN:{iban}\tBIC:{bic}
        
        zugeordnet:{sorted}\tPosten:{towards}
        
        """.format(id=self.id,tag=self.day,betrag=self.value,for_from=self.for_from,vzweck=self.vzweck,iban=self.iban,bic=self.bic,sorted=self.sorted,towards=self.count_towards)

    def __repr__(self):
         return """ÜBERWEISUNG {id}
        Datum:{tag}\tBetrag:{betrag}
        Empfänger/Sender: {for_from}
        Verwendungszweck:
        {vzweck}

        IBAN:{iban}\tBIC:{bic}
        
        zugeordnet:{sorted}\tPosten:{towards}
        
        """.format(id=self.id,tag=self.day,betrag=self.value,for_from=self.for_from,vzweck=self.vzweck,iban=self.iban,bic=self.bic,sorted=self.sorted,towards=self.count_towards)

    def set_sorted(self,inpt) -> None:
        self.sorted = inpt

    def get_month(self,output_str="int") -> str:
        res = int(self.day.month)
        if "str":
            return num_to_month[res]
        else:
            return res
    
    def get_year(self) -> str:
        return int(self.day.year)

    def create_subtransfers(self, num):
        value_remaining = deepcopy(self.value)
        # get info for all but last subtransfer
        for i in range(1,num):
            sub_value = get_subtransfer_value(i,value_remaining)
            sub_id = "{}_{}".format(self.id,i)
            init_dict = {'id':sub_id, 'day':self.day, 'value':sub_value,'for_from':self.for_from, 'vzweck': self.vzweck, 'iban': self.iban, 'bic':self.bic}
            sub_transfer = Transfer(init_dict)
            sub_transfer.is_subtransfer = True
            self.subtransfers[sub_id] = sub_transfer
            value_remaining = value_remaining - sub_value

        # infer last subtransfer
        sub_id = "{}_{}".format(self.id,num)
        init_dict = {'id':sub_id, 'day':self.day, 'value':value_remaining, 'for_from':self.for_from, 'vzweck': self.vzweck, 'iban': self.iban, 'bic':self.bic}
        sub_transfer = Transfer(init_dict)
        sub_transfer.is_subtransfer = True
        self.subtransfers[sub_id] = sub_transfer


    def reset(self):
        self.subtransfers = {}
        self.count_towards = ""
        self.sorted = ""
