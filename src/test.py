from dir_check import check_for_year
from data_extr import import_data
from data_assign import auto_assign


curr_year=2021
check_for_year(curr_year)
erntejahr = import_data(curr_year, total_ants=120, year_start=3)
erntejahr = auto_assign(erntejahr)

erntejahr.remove_transfer(990)