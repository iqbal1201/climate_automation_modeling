'''
Script ini digunakan untuk menedefinisikan lokasi direktori output Proses I
'''


import datetime
from utils.dasarian import get_current_dasarian
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
from config import extent_pulau, pulau_feature, titik_grid, nama_prov
import os


# # Set time

# current_date = datetime.datetime.now()
# pseudo_today = current_date - datetime.timedelta(days=30)
# year_pseudo = pseudo_today.year
# year = current_date.year
# month_now = current_date.strftime("%m")
# month_pseudo = pseudo_today.strftime("%m")
# month_name = current_date.strftime("%B")
# month_name_pseudo = pseudo_today.strftime("%B")
# current_day = current_date.day


date_input_bln, date_input_bln_str = first_date_of_previous_month()
date_input_das, date_input_das_str = first_date_of_dasarian()

year_bln = date_input_bln.year
month_bln = date_input_bln.strftime("%m")
month_name_bln = date_input_bln.strftime("%B")

year_das = date_input_das.year
month_das = date_input_das.strftime("%m")
month_name_das = date_input_das.strftime("%B")
current_dasarian, current_dasarian_text = get_current_dasarian(date_input_das)


# Set folder structure
output_folder = os.getenv("OUTPUT_FOLDER")
output_level_ind = 'INDONESIA'
output_level_prov = 'PROVINSI'
output_tipe_bln = 'ANALISIS_BULANAN'
output_tipe_das = 'ANALISIS_DASARIAN'
output_tipe_peta1 = 'PETA_1'
output_tipe_peta2 = 'PETA_2'
output_tipe_csv = 'CSV'
output_tipe_infografis = 'INFOGRAFIS'
output_tipe_report = 'REPORT'
output_tipe_tiff = 'TIFF'
output_tipe_gdb = 'GDB'



# Data
pulau_kecil = ''


class ArchivingFolder():
    
    def __init__(self, output_folder):
        self.output_folder = output_folder

    
    def archive_prov(self, output_level_prov, output_tipe_periode, tipe, nama_prov, pulau_kecil):
        if output_tipe_periode == 'ANALISIS_DASARIAN':
            output_prov = os.path.join(self.output_folder, output_level_prov)
            output_prov_level1 = os.path.join(output_prov, f'{nama_prov[pulau_kecil]}')
            output_prov_level1_result = os.path.join(output_prov_level1, output_tipe_periode, tipe, f'{year_das}.{month_das}.DAS0{current_dasarian}' )
            if not os.path.exists(output_prov_level1_result):
                os.makedirs(output_prov_level1_result)
            return output_prov_level1_result
        else:
            output_prov = os.path.join(self.output_folder, output_level_prov)
            output_prov_level1 = os.path.join(output_prov, f'{nama_prov[pulau_kecil]}')
            output_prov_level1_result = os.path.join(output_prov_level1, output_tipe_periode, tipe, f'{year_bln}.{month_bln}' )
            if not os.path.exists(output_prov_level1_result):
                os.makedirs(output_prov_level1_result)
            return output_prov_level1_result

    
    def archive_indo(self, output_level_indo, output_tipe_periode, tipe):
        if output_tipe_periode == 'ANALISIS_DASARIAN':
            output_indo = os.path.join(self.output_folder, output_level_ind)
            output_indo_result = os.path.join(output_indo, output_tipe_periode, tipe, f'{year_das}.{month_das}.DAS0{current_dasarian}' )
            if not os.path.exists(output_indo_result):
                os.makedirs(output_indo_result)

            return output_indo_result


        else:
            output_indo = os.path.join(self.output_folder, output_level_ind)
            output_indo_result = os.path.join(output_indo, output_tipe_periode, tipe, f'{year_bln}.{month_bln}' )
            if not os.path.exists(output_indo_result):
                os.makedirs(output_indo_result)

            return output_indo_result
        

