import arcpy
from arcgis.features import GeoAccessor
import os
import pandas as pd
import datetime
import locale
from config import nama_stasiun, nama_prov,nama_prov_archieve, nama_prov_union_shp, nama_prov_folder
from dotenv import load_dotenv
load_dotenv()
import matplotlib.pyplot as plt
from utils.proses1_archiving import ArchivingFolder
from utils.proses1_log_table import log_to_sde
from utils.dasarian import get_current_dasarian, get_current_dasarian_pseudo
from utils.proses1_chart import cut_image
from utils.proses1_dataframe_process import dataframe_indo, dataframe_upt
from utils.proses1_chart import chart_infografis_ch, chart_infografis_sh, laporan_tabel, chart_laporan_ch, chart_laporan_sh
from utils.proses1_update_table_archieve import define_data_path, update_table_path

# Set waktu
locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')

current_date = datetime.datetime.now()
pseudo_today = current_date - datetime.timedelta(days=30)
das_pseudo_today = current_date - datetime.timedelta(days=10)
year_pseudo = pseudo_today.year
year = current_date.year
month_now = current_date.strftime("%m")
month_pseudo = pseudo_today.strftime("%m")
month_name = current_date.strftime("%B")
month_name_pseudo = pseudo_today.strftime("%B")
current_day = current_date.day
current_das_pseudo, current_das_text_pseudo = get_current_dasarian_pseudo()


# Special case for dasarian
today = datetime.datetime.today()
day = today.day

if day < 9:
    das_pseudo_today = current_date - datetime.timedelta(days=10)
    year = das_pseudo_today
    month_now = das_pseudo_today.strftime("%m")
    month_name = das_pseudo_today.strftime("%B")
    current_das_pseudo = 3
    current_das_text_pseudo = 'III'




class PembuatanPetaLaporan():

    def __init__(self, map_project):
        self.map_project = map_project

    
    def store_initial_state(self, original_layout):
        initial_state = {}
        elements = original_layout.listElements()
        for element in elements:
            if hasattr(element, 'text'):
                initial_state[element.name] = element.text
        return initial_state

    # Function to reset elements to their initial state
    def reset_elements(self, modified_layout, initial_state):
        elements = modified_layout.listElements()
        for element in elements:
            if element.name in initial_state:
                try:
                    element.text = initial_state[element.name]
                except Exception as e:
                    print(f"Error resetting element '{element.name}': {e}")


    def peta_1(self, periode_informasi):
        print('Pembuatan Peta 1 dimulai ...')
        
        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")

        aprx = arcpy.mp.ArcGISProject(self.map_project)
        # layout = aprx.listLayouts("peta1_upt1")[0]

        # map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        # map_obj_ch = map_frame_ch.map
        # prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        # kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        # inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
        # inset_obj_ch = inset_frame_ch.map
        # inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


        # map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        # map_obj_sh = map_frame_sh.map
        # prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        # kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        # inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
        # inset_obj_sh = inset_frame_sh.map
        

        # layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
        # layers_to_show = [kab_layer_ch, kab_layer_sh]

        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                wilayah_ref = r[0]
                prov_geometry = r[1]
                if wilayah_ref == 'Indonesia':
                    # layout = aprx.listLayouts("peta_1_pusat")[0]
                    print(wilayah_ref)

                    if periode_informasi == 'ANALISA_BULANAN':

                        layout = aprx.listLayouts("peta1_pusat_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_1')
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                            

                        output_file = os.path.join(output_loc_peta1, f"bln_indo_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_bln_indo_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_bln_indo_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ach_bln_indo_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ash_bln_indo_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Indonesia Sukses")
                        log_to_sde(message = f"Peta 1 Indonesia Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                        
                    else: # DASARIAN

                        layout = aprx.listLayouts("peta1_pusat_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_1')
                        
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        
                                


                        output_file = os.path.join(output_loc_peta1, f"das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ash_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)
                        
                        print("Peta 1 Indonesia Sukses")
                        log_to_sde(message = f"Peta 1 Indonesia Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                elif wilayah_ref == 'Jatim':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("Peta1_Jawa Timur")[0]

                    if periode_informasi == 'ANALISA_BULANAN':

                        layout = aprx.listLayouts("peta1_jatim_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                        

                        output_file = os.path.join(output_loc_peta1, f"bln_jatim_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_bln_jatim_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_bln_jatim_ver_{year_pseudo}{month_pseudo}.png")
                        
                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ach_bln_jatim_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ash_bln_jatim_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Jatim Sukses")
                        log_to_sde(message = f"Peta 1 Jatim Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:
                        layout = aprx.listLayouts("peta1_jatim_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        
                        output_file = os.path.join(output_loc_peta1, f"das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ach_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ash_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Jatim Sukses")
                        log_to_sde(message = f"Peta 1 Jatim Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                
                elif wilayah_ref == 'Kepri':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("Peta1_Kepulauan Riau")[0]

                    if periode_informasi == 'ANALISA_BULANAN':

                        layout = aprx.listLayouts("peta1_kepri_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')

                        output_file = os.path.join(output_loc_peta1, f"bln_kepri_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_bln_kepri_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_bln_kepri_ver_{year_pseudo}{month_pseudo}.png")
                        
                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ach_bln_kepri_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ash_bln_kepri_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Kepri Sukses")
                        log_to_sde(message = f"Peta 1 Kepri Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:
                        layout = aprx.listLayouts("peta1_kepri_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')


                        output_file = os.path.join(output_loc_peta1, f"das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ach_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ash_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Kepri Sukses")
                        log_to_sde(message = f"Peta 1 Kepri Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                    

                elif wilayah_ref == 'Sulut':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("Peta1_Sulawesi Utara")[0]

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta1_sulut_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            


                        output_file = os.path.join(output_loc_peta1, f"bln_sulut_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_bln_sulut_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_bln_sulut_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)


                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ach_bln_sulut_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ash_bln_sulut_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Sulut sukses")
                        log_to_sde(message = f"Peta 1 Sulut Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:
                        layout = aprx.listLayouts("peta1_sulut_dasarian")[0]
                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN 0{current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN 0{current_das_text_pseudo} {month_name.upper()} {year}')
                            
                        


                        output_file = os.path.join(output_loc_peta1, f"das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ach_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ash_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 1 Sulut sukses")
                        log_to_sde(message = f"Peta 1 Sulut Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                
                else:
                    print(wilayah_ref)

                    # layout = aprx.listLayouts("peta1_upt1")[0]
                    # initial_state = self.store_initial_state(layout)

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta1_upt_bulanan")[0]
                        initial_state = self.store_initial_state(layout)

                        

                        map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
                        map_obj_ch = map_frame_ch.map
                        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
                        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
                        inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
                        inset_obj_ch = inset_frame_ch.map
                        inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


                        map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
                        map_obj_sh = map_frame_sh.map
                        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
                        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
                        inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
                        inset_obj_sh = inset_frame_sh.map
                        

                        layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
                        layers_to_show = [kab_layer_ch, kab_layer_sh]





                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        
                        map_frame_sh.camera.setExtent(prov_geometry.extent)
                        map_frame_ch.camera.setExtent(prov_geometry.extent)
                        

                        for layer in layers_to_hide:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        for layer in layers_to_show:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        

                        elements = layout.listElements()
                        
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                try:
                                    # Update the text by replacing placeholders
                                
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                            

                            elif element.name == 'Teks-Judul-SH':
                                try:
                                    # Update the text by replacing placeholders
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")

                            
                            elif element.name == "Teks-stasiun-ch":
                                element.text = element.text.replace('[STASIUN]', f'{nama_stasiun[wilayah_ref]}')

                            elif element.name == "Teks-stasiun-sh":
                                element.text = element.text.replace('[STASIUN]', f'{nama_stasiun[wilayah_ref]}')
                        
            

                        output_file = os.path.join(output_loc_peta1, f"bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_1', 
                                                filename = f'ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        self.reset_elements(layout, initial_state)

                        
                        print(f"Peta 1 {wilayah_ref} sukses")
                        log_to_sde(message = f"Peta 1 {wilayah_ref} Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:
                        layout = aprx.listLayouts("peta1_upt_dasarian")[0]
                        initial_state = self.store_initial_state(layout)

                        map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
                        map_obj_ch = map_frame_ch.map
                        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
                        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
                        inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
                        inset_obj_ch = inset_frame_ch.map
                        inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


                        map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
                        map_obj_sh = map_frame_sh.map
                        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
                        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
                        inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
                        inset_obj_sh = inset_frame_sh.map
                        

                        layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
                        layers_to_show = [kab_layer_ch, kab_layer_sh]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_1', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        
                        map_frame_sh.camera.setExtent(prov_geometry.extent)
                        map_frame_ch.camera.setExtent(prov_geometry.extent)
                        
                        

                        for layer in layers_to_hide:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                    
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        for layer in layers_to_show:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        

                        elements = layout.listElements()
                        print(nama_prov[wilayah_ref])
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                try:
                                    # Update the text by replacing placeholders
                                    
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                                
                                
                            elif element.name == 'Teks-Judul-SH':
                                try:
                                    # Update the text by replacing placeholders
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                            

                            elif element.name == "Teks-stasiun-ch":
                                element.text = element.text.replace('[STASIUN]', f'{nama_stasiun[wilayah_ref]}')

                            elif element.name == "Teks-stasiun-sh":
                                element.text = element.text.replace('[STASIUN]', f'{nama_stasiun[wilayah_ref]}')



                        output_file = os.path.join(output_loc_peta1, f"das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta1, f"ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta1, f"ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")


                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_1', 
                                                filename = f'ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)


                        self.reset_elements(layout, initial_state)
                        print(f"Peta 1 {wilayah_ref} sukses")
                        log_to_sde(message = f"Peta 1 {wilayah_ref} Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                        
        print('Pembuatan Peta 1 selesai')


    def peta_2(self, periode_informasi):
        print('Pembuatan Peta 2 dimulai ...')
        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        # layout = aprx.listLayouts("peta2_upt1")[0]

        # map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        # map_obj_ch = map_frame_ch.map
        # prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        # kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        # inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
        # inset_obj_ch = inset_frame_ch.map
        # inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


        # map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        # map_obj_sh = map_frame_sh.map
        # prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        # kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        # inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
        # inset_obj_sh = inset_frame_sh.map
        

        # layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
        # layers_to_show = [kab_layer_ch, kab_layer_sh]


        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                wilayah_ref = r[0]
                prov_geometry = r[1]
                if wilayah_ref == 'Indonesia':
                    # layout = aprx.listLayouts("peta_2_pusat")[0]
                    print(wilayah_ref)

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta2_pusat_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_2')
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            

                        output_file = os.path.join(output_loc_peta2, f"bln_indo_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_bln_indo_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_bln_indo_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ach_bln_indo_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ash_bln_indo_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Indonesia Sukses")
                        log_to_sde(message = f"Peta 2 Indonesia Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                        

                        
                    else:
                        layout = aprx.listLayouts("peta2_pusat_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_2')
                        
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        

                        output_file = os.path.join(output_loc_peta2, f"das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ash_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Indonesia Sukses")
                        log_to_sde(message = f"Peta 2 Indonesia Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                        
                    
                    
                elif wilayah_ref == 'Jatim':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("peta2_jatim_bulanan")[0]

                    if periode_informasi == 'ANALISA_BULANAN':

                        layout = aprx.listLayouts("peta2_jatim_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            
                        


                        output_file = os.path.join(output_loc_peta2, f"bln_jatim_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_bln_jatim_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_bln_bln_jatim_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ach_bln_jatim_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ash_bln_jatim_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Jatim Sukses")
                        log_to_sde(message = f"Peta 2 Jatim Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:
                        layout = aprx.listLayouts("peta2_jatim_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        

                        output_file = os.path.join(output_loc_peta2, f"das_jatim_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_das_jatim_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_das_jatim_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ach_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI JAWA TIMUR', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ash_das_jatim_ver_{year}{month_now}das0{current_das_text_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Jatim Sukses")
                        log_to_sde(message = f"Peta 2 Jatim Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                        

                    
                elif wilayah_ref == 'Kepri':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("peta2_kepri")[0]

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta2_kepri_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                

                        output_file = os.path.join(output_loc_peta2, f"bln_kepri_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_bln_kepri_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_bln_kepri_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ach_bln_kepri_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ash_bln_kepri_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Kepri sukses")
                        log_to_sde(message = f"Peta 2 Kepri Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                        
                        

                        
                    else:
                        layout = aprx.listLayouts("peta2_kepri_dasarian")[0]
                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta1 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                        

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')


                        output_file = os.path.join(output_loc_peta2, f"das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ach_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI KEPULAUAN RIAU', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ash_das_kepri_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)

                        print("Peta 2 Kepri sukses")
                        log_to_sde(message = f"Peta 2 Kepri Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                        
                    

                elif wilayah_ref == 'Sulut':
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("peta2_sulut")[0]

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta2_sulut_bulanan")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                            


                        output_file = os.path.join(output_loc_peta2, f"bln_sulut_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_bln_sulut_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_bln_sulut_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ach_bln_sulut_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ash_bln_sulut_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)

                        
                        print("Peta 2 Sulut sukses")
                        log_to_sde(message = f"Peta 2 Sulut Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else: #periode_informasi = 'ANALISA_DASARIAN
                        layout = aprx.listLayouts("peta2_sulut_dasarian")[0]

                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        elements = layout.listElements()
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                

                            elif element.name == 'Teks-Judul-SH':
                                element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                            
                        


                        output_file = os.path.join(output_loc_peta2, f"das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ach_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = 'PROVINSI SULAWESI UTARA', wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ash_das_sulut_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)
                        

                        print("Peta 2 Sulut sukses")
                        log_to_sde(message = f"Peta 2 Sulut Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                
                else:
                    print(wilayah_ref)
                    # layout = aprx.listLayouts("peta2_upt1")[0]
                    # initial_state = self.store_initial_state(layout)

                    if periode_informasi == 'ANALISA_BULANAN':
                        layout = aprx.listLayouts("peta2_upt_bulanan")[0]
                        initial_state = self.store_initial_state(layout)


                        map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]

                        map_obj_ch = map_frame_ch.map
                        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
                        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
                        inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
                        inset_obj_ch = inset_frame_ch.map
                        inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


                        map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
                        map_obj_sh = map_frame_sh.map
                        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
                        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
                        inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
                        inset_obj_sh = inset_frame_sh.map
                        

                        layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
                        layers_to_show = [kab_layer_ch, kab_layer_sh]



                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_BULANAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        
                        map_frame_sh.camera.setExtent(prov_geometry.extent)
                        map_frame_ch.camera.setExtent(prov_geometry.extent)
                        # inset_frame_ch.camera.setExtent(prov_geometry.extent)
                        # inset_frame_sh.camera.setExtent(prov_geometry.extent)

                        for layer in layers_to_hide:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        for layer in layers_to_show:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        
                        elements = layout.listElements()
                        
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                try:
                                    # Update the text by replacing placeholders
                                
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                            

                            elif element.name == 'Teks-Judul-SH':
                                try:
                                    # Update the text by replacing placeholders
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")


                        output_file = os.path.join(output_loc_peta2, f"bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Bulanan', date = date_bulanan, format = 'PETA_2', 
                                                filename = f'ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                        update_table_path(data_list_sh)
                        

                        self.reset_elements(layout, initial_state)
                        print(f"Peta 2 {wilayah_ref} sukses")
                        log_to_sde(message = f"Peta 2 {wilayah_ref} Sukses", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        
                    else:  #periode_informasi = 'ANALISA_DASARIAN
                        layout = aprx.listLayouts("peta2_upt_dasarian")[0]
                        initial_state = self.store_initial_state(layout)


                        map_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
                        
                        map_obj_ch = map_frame_ch.map
                        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
                        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
                        inset_frame_ch = layout.listElements("MAPFRAME_ELEMENT", 'Inset CH')[0]
                        inset_obj_ch = inset_frame_ch.map
                        inset_prov_layer = inset_obj_ch.listLayers("admin_prov")[0]


                        map_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
                        map_obj_sh = map_frame_sh.map
                        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
                        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
                        inset_frame_sh = layout.listElements("MAPFRAME_ELEMENT", 'Inset SH')[0]
                        inset_obj_sh = inset_frame_sh.map
                        

                        layers_to_hide = [prov_layer_ch, prov_layer_sh, inset_prov_layer]
                        layers_to_show = [kab_layer_ch, kab_layer_sh]


                        pembuatan_archive = ArchivingFolder(output_folder)
                        output_loc_peta2 = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                        output_tipe_periode='ANALISA_DASARIAN', tipe='PETA_2', 
                                                                        nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                        
                        map_frame_sh.camera.setExtent(prov_geometry.extent)
                        map_frame_ch.camera.setExtent(prov_geometry.extent)
                        # inset_frame_ch.camera.setExtent(prov_geometry.extent)
                        # inset_frame_sh.camera.setExtent(prov_geometry.extent)
                        

                        for layer in layers_to_hide:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                    
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        for layer in layers_to_show:
                            if layer: 
                                try:
                                    layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                except Exception as e:
                                    print(f"Error setting definition query for {layer.name}: {e}")
                        

                        elements = layout.listElements()
                        print(nama_prov[wilayah_ref])
                        for element in elements:
                            if element.name == 'Teks-Judul-CH':
                                try:
                                    # Update the text by replacing placeholders
                                    
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                                
                                
                            elif element.name == 'Teks-Judul-SH':
                                try:
                                    # Update the text by replacing placeholders
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                except Exception as e:
                                    print(f"Error updating element '{element.name}': {e}")
                            

                        output_file = os.path.join(output_loc_peta2, f"das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ach = os.path.join(output_loc_peta2, f"ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")
                        output_ash = os.path.join(output_loc_peta2, f"ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png")

                        layout.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                        cut_image(output_file, output_ach, output_ash)

                        date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                        data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_ch)

                        data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                periode_informasi = 'Dasarian', date = date_dasarian, format = 'PETA_2', 
                                                filename = f'ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                        update_table_path(data_list_sh)

                        
                        self.reset_elements(layout, initial_state)
                        print(f"Peta 2 {wilayah_ref} sukses")
                        log_to_sde(message = f"Peta 2 {wilayah_ref} Sukses", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        
        print('Pembuatan Peta 2 selesai')



    def infografis_bln(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_infog1_ach = aprx.listLayouts("Infografis_ach_pusat_1")[0]
        layout_infog2_ach = aprx.listLayouts("Infografis_ach_pusat_2")[0]
        layout_infog1_ash = aprx.listLayouts("Infografis_ash_pusat_1")[0]
        layout_infog2_ash = aprx.listLayouts("Infografis_ash_pusat_2")[0]

        map_frame_ch = layout_infog1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_infog1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh]
        layers_to_show = [kab_layer_ch, kab_layer_sh]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Infografis dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        
                        print("Infografis Bulanan CH Indonesia dimulai . . .")
                        log_to_sde(message = f"Infografis Bulanan Indonesia CH dimulai . . .", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':
                            
                            initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='INFOGRAFIS')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi)

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            chart_infografis_ch(indo_df_complete)

                            # print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False
                            

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_infog1 = layout_infog1_ach.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')

                            
                            # print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ach.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>CURAH HUJAN</BOL>, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI CURAH HUJAN <BOL>SANGAT TINGGI SEBESAR {sgt_tinggi}%</BOL>, <BOL>TINGGI SEBESAR {tinggi}%</BOL>, <BOL>MENENGAH SEBESAR {menengah}%</BOL>, DAN <BOL>RENDAH SEBESAR {rendah}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>SANGAT TINGGI</BOL> MELIPUTI: {wilayah_sgt_tinggi}. WILAYAH DOMINAN <BOL>TINGGI</BOL> MELIPUTI: {wilayah_tinggi}. WILAYAH DOMINAN <BOL>MENENGAH</BOL> MELIPUTI: {wilayah_menengah}. WILAYAH DOMINAN <BOL>RENDAH</BOL> MELIPUTI: {wilayah_rendah}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ach_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ach_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_ch)



                            self.reset_elements(layout_infog1_ach, initial_state_infog1)
                            self.reset_elements(layout_infog2_ach, initial_state_infog2)

                            print("Infografis Bulanan Indonesia CH selesai")
                            log_to_sde(message = f"Infografis Bulanan CH Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA_SIFAT_HUJAN'

                            print("Infografis Bulanan SH Indonesia dimulai . . .")
                            log_to_sde(message = f"Infografis Bulanan SH Indonesia dimulai . . .", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                            initial_state_infog1 = self.store_initial_state(layout_infog1_ash)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ash)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='INFOGRAFIS')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi)

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            chart_infografis_sh(indo_df_complete)

                            # print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_infog1 = layout_infog1_ash.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')

                            

                            # print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ash.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>SIFAT HUJAN</BOL>, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI SIFAT HUJAN <BOL>ATAS NORMAL SEBESAR {atas_normal}%</BOL>, <BOL>NORMAL SEBESAR {normal}%</BOL>, <BOL>BAWAH NORMAL SEBESAR {bawah_normal}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>ATAS NORMAL</BOL> MELIPUTI: {wilayah_atas_normal}. WILAYAH DOMINAN <BOL>NORMAL</BOL> MELIPUTI: {wilayah_normal}. WILAYAH DOMINAN <BOL>BAWAH NORMAL</BOL> MELIPUTI: {wilayah_bawah_normal}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ash_bln_indo_ver_{year_pseudo}{month_name_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ash_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            self.reset_elements(layout_infog1_ash, initial_state_infog1)
                            self.reset_elements(layout_infog2_ash, initial_state_infog2)

                            print("Infografis Bulanan Indonesia SH selesai")
                            log_to_sde(message = f"Infografis Bulanan SH Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                    else: # wilayah_ref == UPT
                        # print(wilayah_ref)
                        wilayah_upt = nama_prov_union_shp[wilayah_ref]
                        
                
                        print(wilayah_ref)
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Infografis Bulanan {wilayah_ref} CH dimulai")
                            log_to_sde(message = f"Infografis Bulanan CH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='INFOGRAFIS', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            chart_infografis_ch(prov_df_complete)

                            #print("Print Infografis 1")
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_infog1 = layout_infog1_ach.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')


                            
                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ach.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                    element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>CURAH HUJAN</BOL>, UMUMNYA {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI CURAH HUJAN <BOL>SANGAT TINGGI SEBESAR {sgt_tinggi}%</BOL>, <BOL>TINGGI SEBESAR {tinggi}%</BOL>, <BOL>MENENGAH SEBESAR {menengah}%</BOL>, DAN <BOL>RENDAH SEBESAR {rendah}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>SANGAT TINGGI</BOL> MELIPUTI: {wilayah_sgt_tinggi}. WILAYAH DOMINAN <BOL>TINGGI</BOL> MELIPUTI: {wilayah_tinggi}. WILAYAH DOMINAN <BOL>MENENGAH</BOL> MELIPUTI: {wilayah_menengah}. WILAYAH DOMINAN <BOL>RENDAH</BOL> MELIPUTI: {wilayah_rendah}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            self.reset_elements(layout_infog1_ach, initial_state_infog1)
                            self.reset_elements(layout_infog2_ach, initial_state_infog2)

                            print(f"Infografis Bulanan {wilayah_ref} CH selesai")
                            log_to_sde(message = f"Infografis Bulanan CH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA_SIFAT_HUJAN'

                            print(f"Infografis Bulanan {wilayah_ref} SH dimulai")
                            log_to_sde(message = f"Infografis Bulanan SH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            initial_state_infog1 = self.store_initial_state(layout_infog1_ash)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ash)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='INFOGRAFIS', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean,prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi , nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            chart_infografis_sh(prov_df_complete)

                            #print("Print Infografis 1")
                            map_frame_sh.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_infog1 = layout_infog1_ash.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')


                            
                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ash.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                    element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>SIFAT HUJAN</BOL>, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI SIFAT HUJAN <BOL>ATAS NORMAL SEBESAR {atas_normal}%</BOL>, <BOL>NORMAL SEBESAR {normal}%</BOL>, <BOL>BAWAH NORMAL SEBESAR {bawah_normal}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>ATAS NORMAL</BOL> MELIPUTI: {wilayah_atas_normal}. WILAYAH DOMINAN <BOL>NORMAL</BOL> MELIPUTI: {wilayah_normal}. WILAYAH DOMINAN <BOL>BAWAH NORMAL</BOL> MELIPUTI: {wilayah_bawah_normal}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            self.reset_elements(layout_infog1_ash, initial_state_infog1)
                            self.reset_elements(layout_infog2_ash, initial_state_infog2)

                            print(f"Infografis Bulanan {wilayah_ref} SH selesai")
                            log_to_sde(message = f"Infografis Bulanan SH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                except Exception as e:
                    print(f"Error di pengolahan Infografis Bulanan {wilayah_ref}: {e}")
                    log_to_sde(message = f"Error di pengolahan Infografis Bulanan {wilayah_ref}: {e}", status="ERROR", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                    continue  # Skip to the next island



    def infografis_das(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_infog1_ach = aprx.listLayouts("Infografis_ach_pusat_1_das")[0]
        layout_infog2_ach = aprx.listLayouts("Infografis_ach_pusat_2")[0]
        layout_infog1_ash = aprx.listLayouts("Infografis_ash_pusat_1")[0]
        layout_infog2_ash = aprx.listLayouts("Infografis_ash_pusat_2")[0]

        map_frame_ch = layout_infog1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_infog1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh]
        layers_to_show = [kab_layer_ch, kab_layer_sh]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Infografis dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        print(wilayah_ref)
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print("Infografis Dasarian Indonesia CH dimulai")
                            log_to_sde(message = f"Infografis Dasarian CH Indonesia dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='INFOGRAFIS')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi = 'ANALISA_CURAH_HUJAN' )

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            chart_infografis_ch(indo_df_complete)

                            #print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_infog1 = layout_infog1_ach.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')

                            
                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ach.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>CURAH HUJAN</BOL>, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI CURAH HUJAN <BOL>SANGAT TINGGI SEBESAR {sgt_tinggi}%</BOL>, <BOL>TINGGI SEBESAR {tinggi}%</BOL>, <BOL>MENENGAH SEBESAR {menengah}%</BOL>, DAN <BOL>RENDAH SEBESAR {rendah}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>SANGAT TINGGI</BOL> MELIPUTI: {wilayah_sgt_tinggi}. WILAYAH DOMINAN <BOL>TINGGI</BOL> MELIPUTI: {wilayah_tinggi}. WILAYAH DOMINAN <BOL>MENENGAH</BOL> MELIPUTI: {wilayah_menengah}. Wilayah dominan <BOL>RENDAH</BOL> MELIPUTI: {wilayah_rendah}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ach_das_indo_ver_{year}{month_now}das0{current_das_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            print("Infografis Dasarian Indonesia CH selesai")
                            log_to_sde(message = f"Infografis Dasarian CH Indonesia selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'

                            print("Infografis Dasarian Indonesia SH dimulai")
                            log_to_sde(message = f"Infografis Dasarian SH Indonesia dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='INFOGRAFIS')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi = 'ANALISA SIFAT HUJAN')

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            chart_infografis_sh(indo_df_complete)

                            #print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_infog1 = layout_infog1_ash.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')

                            

                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ash.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', 'INDONESIA')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>SIFAT HUJAN</BOL>, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI SIFAT HUJAN <BOL>ATAS NORMAL SEBESAR {atas_normal}%</BOL>, <BOL>NORMAL SEBESAR {normal}%</BOL>, <BOL>BAWAH NORMAL SEBESAR {bawah_normal}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>ATAS NORMAL</BOL> MELIPUTI: {wilayah_atas_normal}. WILAYAH DOMINAN <BOL>NORMAL</BOL> MELIPUTI: {wilayah_normal}. WILAYAH DOMINAN <BOL>BAWAH NORMAL</BOL> MELIPUTI: {wilayah_bawah_normal}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ash_das_indo_ver_{year}{month_now}das0{current_das_text_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)


                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ash_das_indo_ver_{year}{month_now}das0{current_das_text_pseudo}.pdf')
                            update_table_path(data_list_ch)


                            print("Infografis Dasarian Indonesia SH selesai")
                            log_to_sde(message = f"Infografis Dasarian SH Indonesia selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                            


                    else: # wilayah_ref == UPT
                        # print(wilayah_ref)
                        wilayah_upt = nama_prov_union_shp[wilayah_ref]
                
                        print(wilayah_ref)
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Infografis Dasarian {wilayah_ref} CH dimulai")
                            log_to_sde(message = f"Infografis Dasarian CH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='INFOGRAFIS', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            chart_infografis_ch(prov_df_complete)

                            #print("Print Infografis 1")
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_infog1 = layout_infog1_ach.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')


                            
                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ach.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                    element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>CURAH HUJAN</BOL>, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI CURAH HUJAN <BOL>SANGAT TINGGI SEBESAR {sgt_tinggi}%</BOL>, <BOL>TINGGI SEBESAR {tinggi}%</BOL>, <BOL>MENENGAH SEBESAR {menengah}%</BOL>,DAN <BOL>RENDAH SEBESAR {rendah}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>SANGAT TINGGI</BOL> MELIPUTI: {wilayah_sgt_tinggi}. WILAYAH DOMINAN <BOL>TINGGI</BOL> MELIPUTI: {wilayah_tinggi}. WILAYAH DOMINAN <BOL>MENENGAH</BOL> MELIPUTI: {wilayah_menengah}. WILAYAH DOMINAN <BOL>RENDAH</BOL> MELIPUTI: {wilayah_rendah}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ach_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            self.reset_elements(layout_infog1_ach, initial_state_infog1)
                            self.reset_elements(layout_infog2_ach, initial_state_infog2)

                            print(f"Infografis Dasarian {wilayah_ref} CH selesai")
                            log_to_sde(message = f"Infografis Dasarian CH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA_SIFAT_HUJAN'

                            print(f"Infografis Dasarian {wilayah_ref} SH dimulai")
                            log_to_sde(message = f"Infografis Dasarian SH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            initial_state_infog1 = self.store_initial_state(layout_infog1_ash)
                            initial_state_infog2 = self.store_initial_state(layout_infog2_ash)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='INFOGRAFIS', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            chart_infografis_sh(prov_df_complete)

                            #print("Print Infografis 1")
                            map_frame_sh.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_infog1 = layout_infog1_ash.listElements()

                            for element in elements_infog1:
                                if element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year}')


                            
                            #print("Print Infografis 2")

                            elements_infog2 = layout_infog2_ash.listElements()

                            for element in elements_infog2:
                                if element.name == 'CHART':
                                    element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "PROVINSI":
                                    element.text = element.text.replace('[PROVINSI]', f'{nama_prov[wilayah_ref]}')
                                elif element.name == "WAKTU":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == "SUBJUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}')
                                elif element.name == 'TEXT1':
                                    element.text = element.text.replace('[TEXT]', f'''BERDASARKAN ANALISIS <BOL>SIFAT HUJAN</BOL>, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI SIFAT HUJAN <BOL>ATAS NORMAL SEBESAR {atas_normal}%</BOL>, <BOL>NORMAL SEBESAR {normal}%</BOL>, <BOL>BAWAH NORMAL SEBESAR {bawah_normal}%</BOL>.''')
                                elif element.name == 'TEXT2':
                                    element.text = element.text.replace('[TEXT]', f'''WILAYAH DOMINAN <BOL>ATAS NORMAL</BOL> MELIPUTI: {wilayah_atas_normal}. WILAYAH DOMINAN <BOL>NORMAL</BOL> MELIPUTI: {wilayah_normal}. WILAYAH DOMINAN <BOL>BAWAH NORMAL</BOL> MELIPUTI: {wilayah_bawah_normal}.''')


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_infog1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_infog2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'ig_ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'INFOGRAFIS', 
                                                    filename = f'ig_ash_das_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            self.reset_elements(layout_infog1_ash, initial_state_infog1)
                            self.reset_elements(layout_infog2_ash, initial_state_infog2)

                            print(f"Infografis Dasarian {wilayah_ref} SH selesai")
                            log_to_sde(message = f"Infografis Dasarian SH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                except Exception as e:
                    print(f"Error di pengolahan Infografis Dasarian {wilayah_ref}: {e}")
                    log_to_sde(message = f"Error di Infografis Dasarian {wilayah_ref}: {e}", status="ERROR", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                    continue  # Skip to the next island



    def laporan_bln(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_laporan1_ach = aprx.listLayouts("laporan_ach_pusat_1")[0]
        layout_laporan2_ach = aprx.listLayouts("laporan_ach_pusat_2")[0]
        layout_laporan1_ash = aprx.listLayouts("laporan_ash_pusat_1")[0]
        layout_laporan2_ash = aprx.listLayouts("laporan_ash_pusat_2")[0]

        map_frame_ch = layout_laporan1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_laporan1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh]
        layers_to_show = [kab_layer_ch, kab_layer_sh]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Infografis dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        print(wilayah_ref)
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi)

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_ch(pulau_df_complete_clean)

                            print("Print Laporan 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name} {year}, umumnya wilayah Indonesia akan mengalami curah hujan kategori <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, dan <BOL>RENDAH {rendah}%</BOL>. Wilayah yang dominan <BOL>SANGAT TINGGI </BOL> yaitu {wilayah_sgt_tinggi}. Wilayah yang dominan <BOL>TINGGI</BOL> yaitu {wilayah_tinggi}. Wilayah yang dominan <BOL>MENENGAH</BOL> yaitu {wilayah_menengah}. Wilayah yang dominan <BOL>RENDAH</BOL> yaitu {wilayah_rendah}.')

                            
                            print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')
                                


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_indo_ver_{year}{month}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi)

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_sh(pulau_df_complete_clean)

                            print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name} {year}, umumnya wilayah Indonesia akan mengalami sifat hujan kategori <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. Wilayah yang dominan <BOL>ATAS NORMAL </BOL> yaitu {wilayah_atas_normal}. Wilayah yang dominan <BOL>NORMAL</BOL> yaitu {wilayah_normal}. Wilayah yang dominan <BOL>BAWAH NORMAL</BOL> yaitu {wilayah_bawah_normal}.')

                            
                            print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ash.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]]', 'Indonesia dan Pulau Besar')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')

                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ash_bln_indo_ver_{year}{month}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)


                    else: # wilayah_ref == UPT
                        print(wilayah_ref)
                        wilayah_upt = nama_prov_union_shp[wilayah_ref]
                
                        print(wilayah_ref)
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan1_ach)
                            initial_state_laporan2 = self.store_initial_state(layout_laporan2_ach)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            laporan_tabel(kab_df_complete_clean)
                            chart_laporan_ch(kab_df_complete_clean)

                            print("Print Laporan 1")
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name} {year}, umumnya wilayah {nama_prov[wilayah_ref].title()} akan mengalami curah hujan kategori <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, dan <BOL>RENDAH {rendah}%</BOL>. Wilayah yang dominan <BOL>SANGAT TINGGI </BOL> yaitu {wilayah_sgt_tinggi}. Wilayah yang dominan <BOL>TINGGI</BOL> yaitu {wilayah_tinggi}. Wilayah yang dominan <BOL>MENENGAH</BOL> yaitu {wilayah_menengah}. Wilayah yang dominan <BOL>RENDAH</BOL> yaitu {wilayah_rendah}.')


                            
                            print("Print Infografis 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_{wilayah_ref.lower()}_ver_{year}{month}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            self.reset_elements(layout_laporan1_ach, initial_state_laporan1)
                            self.reset_elements(layout_laporan2_ach, initial_state_laporan2)

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan1_ash)
                            initial_state_laporan2 = self.store_initial_state(layout_laporan2_ash)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_infog = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean,  top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            laporan_tabel(kab_df_complete_clean)
                            chart_laporan_sh(kab_df_complete_clean)

                            print("Print Laporan 1")
                            map_frame_sh.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                            
                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name} {year}, umumnya wilayah {nama_prov[wilayah_ref].title()} akan mengalami sifat hujan kategori <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. Wilayah yang dominan <BOL>ATAS NORMAL </BOL> yaitu {wilayah_atas_normal}. Wilayah yang dominan <BOL>NORMAL</BOL> yaitu {wilayah_normal}. Wilayah yang dominan <BOL>BAWAH NORMAL</BOL> yaitu {wilayah_bawah_normal}.')


                            
                            print("Print Infografis 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')

                            


                            temp_pdf1 = os.path.join(output_loc_infog, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_infog, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_infog, f'report_ash_bln_{wilayah_ref.lower()}_ver_{year}{month}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            self.reset_elements(layout_laporan1_ash, initial_state_laporan1)
                            self.reset_elements(layout_laporan2_ash, initial_state_laporan2)
                except Exception as e:
                    print(f"Error di pengolahan Pulau/Provinsi {wilayah_ref}: {e}")
                    continue  # Skip to the next island



    def laporan_das(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_laporan1_ach = aprx.listLayouts("laporan_ach_pusat_1")[0]
        layout_laporan2_ach = aprx.listLayouts("laporan_ach_pusat_2")[0]
        layout_laporan1_ash = aprx.listLayouts("laporan_ash_pusat_1")[0]
        layout_laporan2_ash = aprx.listLayouts("laporan_ash_pusat_2")[0]

        map_frame_ch = layout_laporan1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_laporan1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh]
        layers_to_show = [kab_layer_ch, kab_layer_sh]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Infografis dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        print(wilayah_ref)
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi)

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_ch(pulau_df_complete_clean)

                            print("Print Laporan 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada dasarian {current_dasarian_txt} {month_name} {year}, umumnya wilayah Indonesia akan mengalami curah hujan kategori <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, dan <BOL>RENDAH {rendah}%</BOL>. Wilayah yang dominan <BOL>SANGAT TINGGI </BOL> yaitu {wilayah_sgt_tinggi}. Wilayah yang dominan <BOL>TINGGI</BOL> yaitu {wilayah_tinggi}. Wilayah yang dominan <BOL>MENENGAH</BOL> yaitu {wilayah_menengah}. Wilayah yang dominan <BOL>RENDAH</BOL> yaitu {wilayah_rendah}.')

                            
                            print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR dan Pulau Besar')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')
                                


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_indo_ver_{year}{month}das0{current_dasarian}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi)

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_sh(pulau_df_complete_clean)

                            print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada dasarian {current_dasarian_txt} {month_name} {year}, umumnya wilayah Indonesia akan mengalami sifat hujan kategori <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. Wilayah yang dominan <BOL>ATAS NORMAL </BOL> yaitu {wilayah_atas_normal}. Wilayah yang dominan <BOL>NORMAL</BOL> yaitu {wilayah_normal}. Wilayah yang dominan <BOL>BAWAH NORMAL</BOL> yaitu {wilayah_bawah_normal}.')

                            
                            print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ash.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'Indonesia dan Pulau Besar')

                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ash_bln_indo_ver_{year}{month}das0{current_dasarian}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)


                    else: # wilayah_ref == UPT
                        wilayah_upt = nama_prov_union_shp[wilayah_ref]
                
                        print(wilayah_ref)
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan1_ach)
                            initial_state_laporan2 = self.store_initial_state(layout_laporan2_ach)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            laporan_tabel(kab_df_complete_clean)
                            chart_laporan_ch(kab_df_complete_clean)

                            print("Print Laporan 1")
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada dasarian {current_dasarian} {month_name} {year}, umumnya wilayah {nama_prov[wilayah_ref].title()} akan mengalami curah hujan kategori <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, dan <BOL>RENDAH {rendah}%</BOL>. Wilayah yang dominan <BOL>SANGAT TINGGI </BOL> yaitu {wilayah_sgt_tinggi}. Wilayah yang dominan <BOL>TINGGI</BOL> yaitu {wilayah_tinggi}. Wilayah yang dominan <BOL>MENENGAH</BOL> yaitu {wilayah_menengah}. Wilayah yang dominan <BOL>RENDAH</BOL> yaitu {wilayah_rendah}.')


                            
                            print("Print Infografis 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_{wilayah_ref.lower()}_ver_{year}{month}das0{current_dasarian}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            self.reset_elements(layout_laporan1_ach, initial_state_laporan1)
                            self.reset_elements(layout_laporan2_ach, initial_state_laporan2)

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan1_ash)
                            initial_state_laporan2 = self.store_initial_state(layout_laporan2_ash)

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            laporan_tabel(kab_df_complete_clean)
                            chart_laporan_sh(kab_df_complete_clean)

                            print("Print Laporan 1")
                            map_frame_sh.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                            
                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada dasarian {current_dasarian_txt} {month_name} {year}, umumnya wilayah {nama_prov[wilayah_ref].title()} akan mengalami sifat hujan kategori <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. Wilayah yang dominan <BOL>ATAS NORMAL </BOL> yaitu {wilayah_atas_normal}. Wilayah yang dominan <BOL>NORMAL</BOL> yaitu {wilayah_normal}. Wilayah yang dominan <BOL>BAWAH NORMAL</BOL> yaitu {wilayah_bawah_normal}.')


                            
                            print("Print Infografis 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_dasarian_txt} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', f'{nama_prov[wilayah_ref].capitalize()}')

                            


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ash_bln_{wilayah_ref.lower()}_ver_{year}{month}das0{current_dasarian}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            self.reset_elements(layout_laporan1_ash, initial_state_laporan1)
                            self.reset_elements(layout_laporan2_ash, initial_state_laporan2)
                except Exception as e:
                    print(f"Error di pengolahan Pulau/Provinsi {wilayah_ref}: {e}")
                    continue  # Skip to the next island

    
    def laporan_bln2(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_laporan1_ach = aprx.listLayouts("laporan_ach_pusat_1")[0]
        layout_laporan2_ach = aprx.listLayouts("laporan_ach_pusat_2")[0]
        layout_laporan1_ash = aprx.listLayouts("laporan_ash_pusat_1")[0]
        layout_laporan2_ash = aprx.listLayouts("laporan_ash_pusat_2")[0]
        layout_laporan_ach_upt = aprx.listLayouts("laporan_ach_upt")[0]
        layout_laporan_ash_upt = aprx.listLayouts("laporan_ash_upt")[0]

        map_frame_ch = layout_laporan1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_laporan1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]

        # UPT
        map_frame_ch_upt = layout_laporan_ach_upt.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch_upt = map_frame_ch_upt.map
        prov_layer_ch_upt = map_obj_ch_upt.listLayers("admin_prov")[0]
        kab_layer_ch_upt = map_obj_ch_upt.listLayers("admin_kab")[0]
        kec_layer_ch_upt = map_obj_ch_upt.listLayers("idkec")[0]

        map_frame_sh_upt = layout_laporan_ash_upt.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh_upt = map_frame_sh_upt.map
        prov_layer_sh_upt = map_obj_sh_upt.listLayers("admin_prov")[0]
        kab_layer_sh_upt = map_obj_sh_upt.listLayers("admin_kab")[0]
        kec_layer_sh_upt = map_obj_sh_upt.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh, prov_layer_ch_upt, prov_layer_sh_upt]
        layers_to_show = [kab_layer_ch, kab_layer_sh, kab_layer_ch_upt, kab_layer_sh_upt]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Laporan Singkat dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Laporan Singkat Bulanan Indonesia CH dimulai")
                            log_to_sde(message = f"Laporan Singkat Bulanan Indonesia CH dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi="ANALISA_CURAH_HUJAN")

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_ch(pulau_df_complete_clean)

                            #print("Print Laporan 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name_pseudo} {year_pseudo}, umumnya wilayah Indonesia akan mengalami curah hujan kategori <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, dan <BOL>RENDAH {rendah}%</BOL>. Wilayah yang dominan <BOL>SANGAT TINGGI </BOL> yaitu {wilayah_sgt_tinggi}. Wilayah yang dominan <BOL>TINGGI</BOL> yaitu {wilayah_tinggi}. Wilayah yang dominan <BOL>MENENGAH</BOL> yaitu {wilayah_menengah}. Wilayah yang dominan <BOL>RENDAH</BOL> yaitu {wilayah_rendah}.')

                            
                            #print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'REPORT', 
                                                    filename = f'report_ach_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            print(f"Laporan Singkat Bulanan Indonesia CH selesai")
                            log_to_sde(message = f"Laporan Singkat Bulanan Indonesia CH selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'

                            print(f"Laporan Singkat Bulanan Indonesia SH dimulai")
                            log_to_sde(message = f"Laporan Singkat Bulanan Indonesia SH dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_BULANAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi='ANALISA_SIFAT_HUJAN')

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_sh(pulau_df_complete_clean)

                            #print("Print Laporan 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA BULAN {month_name_pseudo.upper()} {year_pseudo}, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI SIFAT HUJAN KATEGORI <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. WILAYAH YANG DOMINAN <BOL>ATAS NORMAL </BOL> YAITU {wilayah_atas_normal}. WILAYAH YANG DOMINAN <BOL>NORMAL</BOL> YAITU {wilayah_normal}. WILAYAH YANG DOMINAN <BOL>BAWAH NORMAL</BOL> YAITU {wilayah_bawah_normal}.')

                            
                            #print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ash.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')

                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ash_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)


                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'REPORT', 
                                                    filename = f'report_ash_bln_indo_ver_{year_pseudo}{month_pseudo}.pdf')
                            update_table_path(data_list_sh)

                            print(f"Laporan Singkat Bulanan Indonesia SH selesai")
                            log_to_sde(message = f"Laporan Singkat Bulanan Indonesia SH selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                    else: # wilayah_ref == UPT
                        
                        wilayah_upt = nama_prov_union_shp[wilayah_ref]
                
                        
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Laporan Singkat Bulanan {wilayah_ref} CH dimulai")
                            log_to_sde(message = f"Laporan Singkat Bulanan SH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan_ach_upt)
                            

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            
                            chart_infografis_ch(prov_df_complete)

                            #print("Print Laporan 1")
                            map_frame_ch_upt.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_laporan1 = layout_laporan_ach_upt.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA BULAN {month_name_pseudo.upper()} {year_pseudo}, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI CURAH HUJAN KATEGORI <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, DAN <BOL>RENDAH {rendah}%</BOL>. WILAYAH YANG DOMINAN <BOL>SANGAT TINGGI </BOL> YAITU {wilayah_sgt_tinggi}. WILAYAH YANG DOMINAN <BOL>TINGGI</BOL> YAITU {wilayah_tinggi}. WILAYAH YANG DOMINAN <BOL>MENENGAH</BOL> YAITU {wilayah_menengah}. WILAYAH YANG DOMINAN <BOL>RENDAH</BOL> YAITU {wilayah_rendah}.')
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} {nama_prov[wilayah_ref].upper()}')

                            layout_laporan_ach_upt.exportToPNG(os.path.join(output_loc_report, f'report_ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png'), resolution=300, clip_to_elements=True)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'REPORT', 
                                                    filename = f'report_ach_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                            update_table_path(data_list_ch)
                            
                            self.reset_elements(layout_laporan_ach_upt, initial_state_laporan1)

                            print(f"Laporan Singkat Bulanan {wilayah_ref} CH selesai")
                            log_to_sde(message = f"Laporan Singkat Bulanan SH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'

                            print(f"Laporan Singkat Bulanan {wilayah_ref} SH dimulai")
                            log_to_sde(message = f"Laporan Singkat Bulanan SH {wilayah_ref} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan_ash_upt)
                            

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_BULANAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            
                            chart_infografis_sh(prov_df_complete)

                            #print("Print Laporan 1")
                            map_frame_sh_upt.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")




                            elements_laporan1 = layout_laporan_ash_upt.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'Pada bulan {month_name_pseudo} {year_pseudo}, umumnya wilayah {nama_prov[wilayah_ref].title()} akan mengalami sifat hujan kategori <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. Wilayah yang dominan <BOL>ATAS NORMAL </BOL> yaitu {wilayah_atas_normal}. Wilayah yang dominan <BOL>NORMAL</BOL> yaitu {wilayah_normal}. Wilayah yang dominan <BOL>BAWAH NORMAL</BOL> yaitu {wilayah_bawah_normal}.')
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WAKTU]', f'{month_name_pseudo.upper()} {year_pseudo} {nama_prov[wilayah_ref].upper()}')

                            layout_laporan_ash_upt.exportToPNG(os.path.join(output_loc_report, f'report_ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png'), resolution=300, clip_to_elements=True)

                            date_bulanan = pseudo_today.strftime('%Y-%m-%d')
                            data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Bulanan', date = date_bulanan, format = 'REPORT', 
                                                    filename = f'report_ash_bln_{wilayah_ref.lower()}_ver_{year_pseudo}{month_pseudo}.png')
                            update_table_path(data_list_sh)

                            self.reset_elements(layout_laporan_ash_upt, initial_state_laporan1)


                            print(f"Laporan Singkat Bulanan {wilayah_ref} SH selesai")
                            log_to_sde(message = f"Laporan Singkat Bulanan SH {wilayah_ref} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                except Exception as e:
                    print(f"Error di pengolahan Laporan Singkat Bulanan {wilayah_ref}: {e}")
                    log_to_sde(message = f"Error di pengolahan Laporan Singkat Bulanan {wilayah_ref}: {e}", status="ERROR", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                    continue  # Skip to the next island



    def laporan_das2(self, feature, tipe_informasi):
        
        aprx = arcpy.mp.ArcGISProject(self.map_project)
        
        layout_laporan1_ach = aprx.listLayouts("laporan_ach_pusat_1_das")[0]
        layout_laporan2_ach = aprx.listLayouts("laporan_ach_pusat_2")[0]
        layout_laporan1_ash = aprx.listLayouts("laporan_ash_pusat_1")[0]
        layout_laporan2_ash = aprx.listLayouts("laporan_ash_pusat_2")[0]
        layout_laporan_ach_upt = aprx.listLayouts("laporan_ach_upt")[0]
        layout_laporan_ash_upt = aprx.listLayouts("laporan_ash_upt")[0]

        map_frame_ch = layout_laporan1_ach.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch = map_frame_ch.map
        prov_layer_ch = map_obj_ch.listLayers("admin_prov")[0]
        kab_layer_ch = map_obj_ch.listLayers("admin_kab")[0]
        kec_layer_ch = map_obj_ch.listLayers("idkec")[0]

        map_frame_sh = layout_laporan1_ash.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh = map_frame_sh.map
        prov_layer_sh = map_obj_sh.listLayers("admin_prov")[0]
        kab_layer_sh = map_obj_sh.listLayers("admin_kab")[0]
        kec_layer_sh = map_obj_sh.listLayers("idkec")[0]
        

        # UPT
        map_frame_ch_upt = layout_laporan_ach_upt.listElements("MAPFRAME_ELEMENT", 'Map Frame CH')[0]
        map_obj_ch_upt = map_frame_ch_upt.map
        prov_layer_ch_upt = map_obj_ch_upt.listLayers("admin_prov")[0]
        kab_layer_ch_upt = map_obj_ch_upt.listLayers("admin_kab")[0]
        kec_layer_ch_upt = map_obj_ch_upt.listLayers("idkec")[0]

        map_frame_sh_upt = layout_laporan_ash_upt.listElements("MAPFRAME_ELEMENT", 'Map Frame SH')[0]
        map_obj_sh_upt = map_frame_sh_upt.map
        prov_layer_sh_upt = map_obj_sh_upt.listLayers("admin_prov")[0]
        kab_layer_sh_upt = map_obj_sh_upt.listLayers("admin_kab")[0]
        kec_layer_sh_upt = map_obj_sh_upt.listLayers("idkec")[0]
        

        layers_to_hide = [prov_layer_ch, prov_layer_sh, prov_layer_ch_upt, prov_layer_sh_upt]
        layers_to_show = [kab_layer_ch, kab_layer_sh, kab_layer_ch_upt, kab_layer_sh_upt]


        dataframe = pd.DataFrame.spatial.from_featureclass(feature)


        print("Proses Pembuatan Laporan Singkat dimulai . . .")

        prov_referensi = os.getenv("POLY_PROV")
        output_folder = os.getenv("OUTPUT_FOLDER")
        folder_aset = os.getenv("ASSET")
        
        with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        
                        
                        # initial_state_infog1 = self.store_initial_state(layout_infog1_ach)
                        # initial_state_infog2 = self.store_initial_state(layout_infog2_ach)

                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Laporan Singkat Dasarian Indonesia CH dimulai")
                            log_to_sde(message = f"Laporan Singkat Dasarian Indonesia CH dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi='ANALISA_CURAH_HUJAN')

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_ch(pulau_df_complete_clean)

                            #print("Print Laporan 1")
                            # Set extent sesuai geometry
                            
                            map_frame_ch.camera.setExtent(prov_geometry.extent)

                            prov_layer_ch.visible = False
                            kab_layer_ch.visible = False
                            kec_layer_ch.visible = False

                            # output_file = os.path.join(folder_aset, 'maps', f"peta_infografis.png")
                            # output_ach = os.path.join(folder_aset, 'maps', f"peta_infografis_ach.png")
                            # output_ash = os.path.join(folder_aset, 'maps', f"peta_infografis_ash.png")

                            # layout_peta.exportToPNG(output_file, resolution=300, clip_to_elements=True)
                            # cut_image(output_file, output_ach, output_ash)


                            elements_laporan1 = layout_laporan1_ach.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI CURAH HUJAN KATEGORI <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, DAN <BOL>RENDAH {rendah}%</BOL>. WILAYAH YANG DOMINAN <BOL>SANGAT TINGGI </BOL> YAITU {wilayah_sgt_tinggi}. WILAYAH YANG DOMINAN <BOL>TINGGI</BOL> YAITU {wilayah_tinggi}. WILAYAH YANG DOMINAN <BOL>MENENGAH</BOL> YAITU {wilayah_menengah}. WILAYAH YANG DOMINAN <BOL>RENDAH</BOL> YAITU {wilayah_rendah}.')

                            
                            #print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ach.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                


                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ach.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ach.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ach_bln_indo_ver_{year}{month_pseudo}das0{current_das_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)

                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'REPORT', 
                                                    filename = f'report_ach_bln_indo_ver_{year}{month_pseudo}das0{current_das_pseudo}.pdf')
                            update_table_path(data_list_ch)

                            print(f"Laporan Singkat Dasarian Indonesia CH selesai")
                            log_to_sde(message = f"Laporan Singkat Dasarian Indonesia CH selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'

                            print(f"Laporan Singkat Dasarian Indonesia SH dimulai")
                            log_to_sde(message = f"Laporan Singkat Dasarian Indonesia SH dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_indo(output_level_indo='INDONESIA', 
                                                                            output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT')


                            indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori,  atas_normal, normal, bawah_normal= dataframe_indo(dataframe, tipe_informasi='ANALISA_SIFAT_HUJAN')

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']


                            laporan_tabel(pulau_df_complete_clean)
                            chart_laporan_sh(pulau_df_complete_clean)

                            #print("Print Infografis 1")
                            # Set extent sesuai geometry
                            
                            map_frame_sh.camera.setExtent(prov_geometry.extent)

                            prov_layer_sh.visible = False
                            kab_layer_sh.visible = False
                            kec_layer_sh.visible = False



                            elements_laporan1 = layout_laporan1_ash.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA DASARIAN {current_das_text_pseudo} {month_name.upper} {year}, UMUMNYA WILAYAH INDONESIA AKAN MENGALAMI SIFAT HUJAN KATEGORI <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, DAN <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. WILAYAH YANG DOMINAN <BOL>ATAS NORMAL </BOL> YAITU {wilayah_atas_normal}. WILAYAH YANG DOMINAN <BOL>NORMAL</BOL> YAITU {wilayah_normal}. WILAYAH YANG DOMINAN <BOL>BAWAH NORMAL</BOL> YAITU {wilayah_bawah_normal}.')

                            
                            #print("Print Laporan 2")

                            elements_laporan2 = layout_laporan2_ash.listElements()

                            for element in elements_laporan2:
                                if element.name == 'TABEL':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'table', 'table_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'table', 'table_laporan.png')))
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'laporan', 'chart_laporan.png')))
                                elif element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-TABEL":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WILAYAH]', 'INDONESIA DAN PULAU BESAR')

                            temp_pdf1 = os.path.join(output_loc_report, 'infog1.pdf')
                            temp_pdf2 = os.path.join(output_loc_report, 'infog2.pdf')
                            layout_laporan1_ash.exportToPDF(temp_pdf1, resolution=300)
                            layout_laporan2_ash.exportToPDF(temp_pdf2, resolution=300)

                            pdf_doc = arcpy.mp.PDFDocumentCreate(os.path.join(output_loc_report, f'report_ash_bln_indo_ver_{year}{month_now}das0{current_das_pseudo}.pdf'))
                            pdf_doc.appendPages(temp_pdf1)
                            pdf_doc.appendPages(temp_pdf2)
                            pdf_doc.saveAndClose()

                            os.remove(temp_pdf1)
                            os.remove(temp_pdf2)


                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_sh = define_data_path(wilayah = 'INDONESIA', wilayah_folder = 'INDONESIA', tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'REPORT', 
                                                    filename = f'report_ash_bln_indo_ver_{year}{month_now}das0{current_das_pseudo}.pdf')
                            update_table_path(data_list_sh)


                            print(f"Laporan Singkat Dasarian Indonesia SH selesai")
                            log_to_sde(message = f"Laporan Singkat Dasarian Indonesia SH selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")


                    else: # wilayah_ref == UPT
                        # print(wilayah_ref)
                        # wilayah_upt = nama_prov_union_shp[wilayah_ref]
                
                        # print(wilayah_ref)
                        if tipe_informasi == 'ANALISA_CURAH_HUJAN':

                            print(f"Laporan Singkat Dasarian {wilayah_ref} CH dimulai")
                            log_to_sde(message = f"Laporan Singkat Dasarian {wilayah_ref} CH dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan_ach_upt)
                            

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_sgt_tinggi = top_by_kategori['Sangat Tinggi']
                            wilayah_tinggi = top_by_kategori['Tinggi']
                            wilayah_menengah = top_by_kategori['Menengah']
                            wilayah_rendah = top_by_kategori['Rendah']

                            
                            chart_infografis_ch(prov_df_complete)

                            #print("Print Laporan 1")
                            map_frame_ch_upt.camera.setExtent(prov_geometry.extent)

                            

                            # if kab_layer_ch.isFeatureLayer:
                            #     for lbl_class in kab_layer_ch.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_ch.showLabels = True



                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    

                            elements_laporan1 = layout_laporan_ach_upt.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI CURAH HUJAN KATEGORI <BOL>SANGAT TINGGI {sgt_tinggi}%</BOL>, <BOL>TINGGI {tinggi}%</BOL>, <BOL>MENENGAH {menengah}%</BOL>, DAN <BOL>RENDAH {rendah}%</BOL>. WILAYAH YANG DOMINAN <BOL>SANGAT TINGGI </BOL> YAITU {wilayah_sgt_tinggi}. WILAYAH YANG DOMINAN <BOL>TINGGI</BOL> YAITU {wilayah_tinggi}. WILAYAH YANG DOMINAN <BOL>MENENGAH</BOL> YAITU {wilayah_menengah}. WILAYAH YANG DOMINAN <BOL>RENDAH</BOL> YAITU {wilayah_rendah}.')
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_ch.png')))
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} {nama_prov[wilayah_ref].upper()}')
                                        

                            layout_laporan_ach_upt.exportToPNG(os.path.join(output_loc_report, f'report_ach_bln_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png'), resolution=300, clip_to_elements=True)
                            
                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_ch = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='CH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'REPORT', 
                                                    filename = f'report_ach_bln_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                            update_table_path(data_list_ch)
                            
                            self.reset_elements(layout_laporan_ach_upt, initial_state_laporan1)


                            print(f"Laporan Singkat Dasarian {wilayah_ref} CH selesai")
                            log_to_sde(message = f"Laporan Singkat Dasarian {wilayah_ref} CH selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                            

                        else: # tipe_informasi == 'ANALISA SIFAT HUJAN'

                            print(f"Laporan Singkat Dasarian {wilayah_ref} SH dimulai")
                            log_to_sde(message = f"Laporan Singkat Dasarian {wilayah_ref} SH dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                            
                            initial_state_laporan1 = self.store_initial_state(layout_laporan_ash_upt)
                            

                            pembuatan_archive = ArchivingFolder(output_folder)
                            output_loc_report = pembuatan_archive.archive_prov(output_level_prov='PROVINSI', 
                                                                                    output_tipe_periode='ANALISA_DASARIAN', tipe='REPORT', 
                                                                                    nama_prov=nama_prov_folder, pulau_kecil=wilayah_ref)
                            

                            prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal = dataframe_upt(dataframe, tipe_informasi, nama_prov_union_shp[wilayah_ref])

                            wilayah_atas_normal = top_by_kategori['Atas Normal']
                            wilayah_normal = top_by_kategori['Normal']
                            wilayah_bawah_normal = top_by_kategori['Bawah Normal']

                            
                            chart_infografis_sh(prov_df_complete)

                            #print("Print Laporan 1")
                            map_frame_sh_upt.camera.setExtent(prov_geometry.extent)


                            # if kab_layer_sh.isFeatureLayer:
                            #     for lbl_class in kab_layer_sh.listLabelClasses():
                            #         lbl_class.showClassLabels = True
                            #         lbl_class.symbol.fontSize = 10
                            #     kab_layer_sh.showLabels = True


                            for layer in layers_to_hide:
                                    if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR <> '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                                    for layer in layers_to_show:
                                        if layer: 
                                            try:
                                                layer.definitionQuery = f"WADMPR = '{wilayah_ref}'"
                                            except Exception as e:
                                                print(f"Error setting definition query for {layer.name}: {e}")
                            
                            elements_laporan1 = layout_laporan_ash_upt.listElements()

                            for element in elements_laporan1:
                                if element.name == "JUDUL":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} {nama_prov[wilayah_ref]}')
                                elif element.name == "TEKS":
                                    element.text = element.text.replace('[TEKS]', f'PADA DASARIAN {current_das_text_pseudo} {month_name.upper()} {year}, UMUMNYA WILAYAH {nama_prov[wilayah_ref].upper()} AKAN MENGALAMI SIFAT HUJAN KATEGORI <BOL>ATAS NORMAL {atas_normal}%</BOL>, <BOL>NORMAL {normal}%</BOL>, dan <BOL>BAWAH NORMAL {bawah_normal}%</BOL>. WILAYAH YANG DOMINAN <BOL>ATAS NORMAL </BOL> YAITU {wilayah_atas_normal}. WILAYAH YANG DOMINAN <BOL>NORMAL</BOL> YAITU {wilayah_normal}. WILAYAH YANG DOMINAN <BOL>BAWAH NORMAL</BOL> YAITU {wilayah_bawah_normal}.')
                                elif element.name == 'CHART':
                                        element.sourceImage = element.sourceImage.replace(os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png'), 
                                                                                        (os.path.join(folder_aset,'chart', 'infografis', 'chart_infografis_sh.png')))
                                elif element.name == "JUDUL-CHART":
                                    element.text = element.text.replace('[WAKTU]', f'DASARIAN {current_das_text_pseudo} {month_name.upper()} {year} {nama_prov[wilayah_ref].upper()}')
                                        

                            layout_laporan_ash_upt.exportToPNG(os.path.join(output_loc_report, f'report_ash_bln_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png'), resolution=300, clip_to_elements=True)

                            date_dasarian = das_pseudo_today.strftime('%Y-%m-%d')
                            data_list_sh = define_data_path(wilayah = nama_prov_archieve[wilayah_ref], wilayah_folder = nama_prov_folder[wilayah_ref], tipe_informasi = 'Analisis', jenis_informasi='SH', 
                                                    periode_informasi = 'Dasarian', date = date_dasarian, format = 'REPORT', 
                                                    filename = f'report_ash_bln_{wilayah_ref.lower()}_ver_{year}{month_now}das0{current_das_pseudo}.png')
                            update_table_path(data_list_sh)

                            
                            self.reset_elements(layout_laporan_ash_upt, initial_state_laporan1)

                            print(f"Laporan Singkat Dasarian {wilayah_ref} SH selesai")
                            log_to_sde(message = f"Laporan Singkat Dasarian {wilayah_ref} SH selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")

                            
                except Exception as e:
                    print(f"Error di pengolahan Laporan Singkat Dasarian {wilayah_ref}: {e}")
                    log_to_sde(message = f"Error di pengolahan Laporan Singkat Dasarian {wilayah_ref}: {e}", status="ERROR", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
                    continue  # Skip to the next island   