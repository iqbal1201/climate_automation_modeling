import arcpy
import sys
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
# import datetime
import locale
from utils.proses1_download_data_from_server import *
from utils.proses1_log_table import log_to_sde
from utils.proses1_raster_mosaic import copy_raster, add_raster_and_update_fields, delete_old_rasters
from utils.dasarian import get_current_dasarian
from utils.proses1_clear_fgdb_temp import empty_fgdb
from utils.proses1_update_table_summary import update_table
from utils.proses1_preprocess import Preprocessing
from utils.proses1_peta_laporan import PembuatanPetaLaporan
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
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
folder_dasarian = 'DASARIAN'
file_name_dasarian = f'BlendGSMAP_POS.{year_das}{month_das}dec0{current_dasarian}.xls'

# Output folder structure
output_folder = os.getenv("OUTPUT_FOLDER")
output_level_ind = 'INDONESIA'
output_level_prov = 'PROVINSI'
output_tipe_bln = 'ANALISIS_BULANAN'
output_tipe_das = 'ANALISIS_DASARIAN'

# Get full folder path
file_path_dasarian = os.path.join(main_folder, folder_dasarian)

# File input
file_input_dasarian = os.path.join(file_path_dasarian, file_name_dasarian)





# map project
map_project = os.getenv("APRX_PROJECT")


if __name__ == "__main__":
    log_to_sde(message = "PROSES ANALISIS DASARIAN DIMULAI . . .", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
    

    print("Proses Download Data dimulai ... ")
    download_data(main_file_url_das, secondary_file_url_das, local_file_path_das )
    print("Proses Download Data selesai ... ")

    if os.path.exists(file_input_dasarian):
        try:

            print("Proses Ekstraksi Table Excel dimulai ... ")

            # Memulai ekstraksi excel ke feature point
            start_time = datetime.datetime.now()
            preprocessing_das = Preprocessing(fgdb_temp, file_input_dasarian)

            # # Panggil metode Get_Excel untuk mengonversi file Excel ke tabel
        
            point_das = preprocessing_das.Excel_to_Feature(output_table_name = output_table_name+'_das', output_feature_name = output_feature_name+'_das')
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            print(f"Proses Ekstraksi Table Excel Selesai selama: {duration.seconds} detik")
            print("\n")


            print("Proses 1 dimulai")
            start_time = datetime.datetime.now()
            print("Analisa Data Dasarian dimulai")

            poly_indo_ach, poly_indo_ash, raster_ACH_to_merge, raster_ASH_to_merge = interpolasi_das(input_data= point_das)
            

            end_time = datetime.datetime.now()
            duration = end_time - start_time

            print(f"Analisa Data Dasarian selesai selama: {(duration.total_seconds() % 3600) // 60} menit")
            print("\n")


            print("Proses Pembuatan Laporan Dasarian dimulai")

            start_time = datetime.datetime.now()

            pelaporan = PembuatanPetaLaporan(map_project=map_project)

            peta1_bulanan = pelaporan.peta_1(periode_informasi='ANALISIS_DASARIAN')

            peta2_bulanan = pelaporan.peta_2(periode_informasi='ANALISIS_DASARIAN')

            infografis_ch = pelaporan.infografis_das(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN')

            infografis_sh = pelaporan.infografis_das(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN')

            laporan_ch = pelaporan.laporan_das2(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN')

            laporan_sh = pelaporan.laporan_das2(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN')


            end_time = datetime.datetime.now()
            duration2 = end_time - start_time


            print(f"Proses 1 selesai selama: {(duration2.total_seconds() % 3600) // 60} menit")


            print("Mengupdate Tabel Summary")

            update_table(feature = poly_indo_ach, tipe_informasi='ANALISIS_CURAH_HUJAN', periode='DASARIAN')
            update_table(feature = poly_indo_ash, tipe_informasi='ANALISIS_SIFAT_HUJAN', periode='DASARIAN')

            print("Update Tabel Summary selesai")
            print("\n")


            # print("Mengupdate Mosaic Raster CH")
            # mosaic_data_ch = os.getenv("MOSAIC_DAS_ACH")

            # for raster_path, area in raster_ACH_to_merge:
            #     add_raster_and_update_fields(raster_path, area, mosaic_data_ch)

            # time.sleep(20)

            # two_months_ago = datetime.datetime.now() - datetime.timedelta(days=90)

            # # Format the date in the required format for the SQL clause
            # formatted_date = two_months_ago.strftime('%Y-%m-%d %H:%M:%S')

            # arcpy.management.RemoveRastersFromMosaicDataset(
            #     in_mosaic_dataset=mosaic_data_ch,
            #     where_clause=f"date <= timestamp '{formatted_date}'",
            #     update_boundary="UPDATE_BOUNDARY",
            #     mark_overviews_items="MARK_OVERVIEW_ITEMS",
            #     delete_overview_images="DELETE_OVERVIEW_IMAGES",
            #     delete_item_cache="DELETE_ITEM_CACHE",
            #     remove_items="REMOVE_MOSAICDATASET_ITEMS",
            #     update_cellsize_ranges="UPDATE_CELL_SIZES")

            # #delete_old_rasters(mosaic_data_ch)

            # arcpy.management.CalculateStatistics(
            #     in_raster_dataset=mosaic_data_ch,
            #     x_skip_factor=1,
            #     y_skip_factor=1,
            #     ignore_values=[],
            #     skip_existing="OVERWRITE")
            
            # arcpy.management.SetRasterProperties(
            #         in_raster=mosaic_data_ch,
            #         data_type="GENERIC",
            #         statistics="1 0 10000 # #",
            #         stats_file=None,
            #         nodata=None,
            #         key_properties=None,
            #         multidimensional_info=None,
            #     )
            
            # print("Update Mosaic Raster CH selesai")
            # print("\n")


            # print("Mengupdate Mosaic Raster SH")
            # mosaic_data_sh = os.getenv("MOSAIC_DAS_ASH")

            # for raster_path, area in raster_ASH_to_merge:
            #     add_raster_and_update_fields(raster_path, area, mosaic_data_sh)

            # time.sleep(20)


            # arcpy.management.RemoveRastersFromMosaicDataset(
            #     in_mosaic_dataset=mosaic_data_sh,
            #     where_clause=f"date <= timestamp '{formatted_date}'",
            #     update_boundary="UPDATE_BOUNDARY",
            #     mark_overviews_items="MARK_OVERVIEW_ITEMS",
            #     delete_overview_images="DELETE_OVERVIEW_IMAGES",
            #     delete_item_cache="DELETE_ITEM_CACHE",
            #     remove_items="REMOVE_MOSAICDATASET_ITEMS",
            #     update_cellsize_ranges="UPDATE_CELL_SIZES")


            # #delete_old_rasters(mosaic_data_sh)

            # arcpy.management.CalculateStatistics(
            #     in_raster_dataset=mosaic_data_sh,
            #     x_skip_factor=1,
            #     y_skip_factor=1,
            #     ignore_values=[],
            #     skip_existing="OVERWRITE")

            # arcpy.management.SetRasterProperties(
            #         in_raster=mosaic_data_sh,
            #         data_type="GENERIC",
            #         statistics="1 0 10000 # #",
            #         stats_file=None,
            #         nodata=None,
            #         key_properties=None,
            #         multidimensional_info=None,
            #     )
            # print("Update Mosaic Raster SH selesai")
            # print("\n")

            print("Hapus semua data temp")
            empty_fgdb(fgdb_temp)
            print("Data temp terhapus")


            log_to_sde(message = "PROSES ANALISIS DASARIAN SELESAI", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
            
            sys.exit(0)
        
        except Exception as e:
            print(f"Error {e}")
            log_to_sde(message = f"Error {e}", status="ERROR", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
            
            sys.exit(1)
            
    
    else:
        print("Input Data Terbaru Tidak Ditemukan atau Belum Terupdate")
        log_to_sde(message = "Input Data Terbaru Tidak Ditemukan atau Belum Terupdate", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        sys.exit(0)

    

    

