import arcpy
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
#import geopandas as gpd
import matplotlib.pyplot as plt
# import datetime
import locale
from utils.proses1_download_data_from_server import *
from utils.proses1_log_table import log_to_sde
from utils.proses1_raster_mosaic import copy_raster, add_raster_and_update_fields, delete_old_rasters
from utils.dasarian import get_current_dasarian
from utils.proses1_update_table_summary import update_table
from utils.proses1_clear_fgdb_temp import empty_fgdb
from utils.proses1_preprocess import Preprocessing
from utils.proses1_peta_laporan import PembuatanPetaLaporan
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
from utils.proses1_dataframe_process import dataframe_indo, dataframe_upt
from utils.proses1_data_process import interpolasi_bln, interpolasi_das
from dotenv import load_dotenv
from utils.proses1_authenticate import map_network_drive
import warnings
warnings.filterwarnings("ignore")
load_dotenv()

# Authenticate Fileserver
network_path = r'\\10.20.221.28\data_bmkg'
username = 'arcgis' 
password = '4rcG!$1kl1m2024'

map_network_drive(network_path, username, password)

# Environment ArcPY
arcpy.env.overwriteOutput = True

## Get time
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

date_input_bln, date_input_bln_str = first_date_of_previous_month()
date_input_das, date_input_das_str = first_date_of_dasarian()

year_bln = date_input_bln.year
month_bln = date_input_bln.strftime("%m")
month_name_bln = date_input_bln.strftime("%B")

year_das = date_input_das.year
month_das = date_input_das.strftime("%m")
month_name_das = date_input_das.strftime("%B")
current_dasarian, current_dasarian_text = get_current_dasarian(date_input_das)


# Get geodatabase
fgdb_temp = os.getenv("FGDB_TEMP")
output_table_name = "output_1_proses1_table"
output_feature_name = "output_2_proses1_feature_point"


## Input folder structure
main_folder = os.getenv("MAIN_FOLDER")
folder_bulanan = 'BULANAN'
file_name_bulanan = f'BlendGSMAP_POS.{year_bln}{month_bln}.xls'


# Output folder structure
output_folder = os.getenv("OUTPUT_FOLDER")
output_level_ind = 'INDONESIA'
output_level_prov = 'PROVINSI'
output_tipe_bln = 'ANALISIS_BULANAN'
output_tipe_das = 'ANALISIS_DASARIAN'

# Get full folder path
file_path_bulanan = os.path.join(main_folder, folder_bulanan)


# File input
file_input_bulanan = os.path.join(file_path_bulanan, file_name_bulanan)


# map project
map_project = os.getenv("APRX_PROJECT")



if __name__ == "__main__":
    
    log_to_sde(message = "PROSES ANALISIS BULANAN DIMULAI . . .", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

    print("Proses Download Data dimulai ... ")
    download_data(main_file_url_bln, secondary_file_url_bln, local_file_path_bln )
    print("Proses Download Data selesai ... ")

    if os.path.exists(file_input_bulanan):
        try:

            print("Proses Ekstraksi Table Excel dimulai ... ")
            start_time = datetime.datetime.now()
            # Memulai ekstraksi excel ke feature point
            preprocessing_bln = Preprocessing(fgdb_temp, file_input_bulanan)
            
            # # Panggil metode Get_Excel untuk mengonversi file Excel ke tabel
            point_bln = preprocessing_bln.Excel_to_Feature(output_table_name = output_table_name+'_bln', output_feature_name = output_feature_name+'_bln')
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            print(f"Proses Ekstraksi Table Excel Selesai selama: {duration.seconds} detik")
            print("\n")


            print("Proses 1 dimulai")
            start_time = datetime.datetime.now()
            print("Analisa Data Bulanan dimulai")

            poly_indo_ach, poly_indo_ash, raster_ACH_to_merge, raster_ASH_to_merge = interpolasi_bln(input_data= point_bln)
            

            end_time = datetime.datetime.now()
            duration = end_time - start_time

            print(f"Analisa Data Bulanan selesai selama: {(duration.total_seconds() % 3600) // 60} menit")
            print("\n")


            print("Proses Pembuatan Laporan dimulai")

            start_time = datetime.datetime.now()

            pelaporan = PembuatanPetaLaporan(map_project=map_project)

            peta1_bulanan = pelaporan.peta_1(periode_informasi='ANALISIS_BULANAN')

            peta2_bulanan = pelaporan.peta_2(periode_informasi='ANALISIS_BULANAN')

            infografis_ch = pelaporan.infografis_bln(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN')

            infografis_sh = pelaporan.infografis_bln(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN')

            laporan_ch = pelaporan.laporan_bln2(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN')

            laporan_sh = pelaporan.laporan_bln2(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN')


            end_time = datetime.datetime.now()
            duration2 = end_time - start_time


            print(f"Proses 1 selesai selama: {(duration2.total_seconds() % 3600) // 60} menit")
            print("\n")

            print("Mengupdate Tabel Summary")

            update_table(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN', periode='BULANAN')
            update_table(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN', periode='BULANAN')

            print("Update Tabel Summary selesai")

            print("\n")

            print("Hapus semua data temp")
            empty_fgdb(fgdb_temp)
            print("Data temp terhapus")

            log_to_sde(message = "PROSES ANALISIS BULANAN SELESAI", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
            
            sys.exit(0)

        
        except Exception as e:
            print(f"Error {e}")
            log_to_sde(message = f"Error {e}", status="ERROR", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
            
            sys.exit(1)
            

    
    else:
        print("Input Data Terbaru Tidak Ditemukan atau Belum Terupdate")
        log_to_sde(message = "Input Data Terbaru Tidak Ditemukan atau Belum Terupdate", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        
        sys.exit(0)

    

    

