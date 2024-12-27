import arcpy
import os
import pandas as pd
import datetime
from datetime import timedelta
from arcgis.features import GeoAccessor
from arcgis.features import Table, Feature
from config import prov_sde, nama_prov_union_shp, nama_prov_table
from utils.proses1_dataframe_process import dataframe_indo, dataframe_upt
from utils.proses1_log_table import log_to_sde

prov_referensi = os.getenv("POLY_PROV")
output_folder = os.getenv("OUTPUT_FOLDER")
folder_aset = os.getenv("ASSET")

def first_date_of_previous_month():
    today = datetime.datetime.now()  # Get the current date
    # Calculate the first day of the current month
    first_of_current_month = today.replace(day=1)
    # Subtract one day to get the last day of the previous month
    last_of_previous_month = first_of_current_month - timedelta(days=1)
    # Get the first day of the previous month
    first_of_previous_month = last_of_previous_month.replace(day=1)
    first_of_previous_month_str = first_of_previous_month.strftime("%d-%m-%Y")
    return first_of_previous_month, first_of_previous_month_str

def first_date_of_dasarian():
    today = datetime.datetime.now() # Get the current date
    # Calculate the number of days since the start of the cycle
    days_since_start = today.day % 10
    # Calculate the first day of the current dasarian cycle
    first_dasarian_date = today - timedelta(days=days_since_start)
    first_dasarian_date_str = first_dasarian_date.strftime("%d-%m-%Y")
    return first_dasarian_date, first_dasarian_date_str


def update_table(feature, tipe_informasi, periode):

    current_date = datetime.datetime.now()
    current_date_str = current_date.strftime('%d-%m-%Y')
    current_date_datetime = pd.to_datetime(current_date_str, format='%d-%m-%Y')
    date_input_bln, date_input_bln_str = first_date_of_previous_month()
    date_input_das, date_input_das_str = first_date_of_dasarian()

    two_months_ago = datetime.datetime.now() - timedelta(days=90)
    prov_referensi = os.getenv("POLY_PROV")


    dataframe = pd.DataFrame.spatial.from_featureclass(feature)


    print("Memulai Update Table")

    with arcpy.da.SearchCursor(prov_referensi, ["WADMPR", "SHAPE@"]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
            for r in cursors:
                try:
                
                    wilayah_ref = r[0]
                    prov_geometry = r[1]
                    if wilayah_ref == 'Indonesia':
                        print(wilayah_ref)
                        sde_table_path = prov_sde[wilayah_ref]


                        if periode == 'BULANAN':
                            if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
                                indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi="ANALISIS_CURAH_HUJAN")
                                df = prov_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah (%)': 'rendah', 'Menengah (%)': 'menengah', 'Tinggi (%)' : 'tinggi', 'Sangat Tinggi (%)': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')


                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor




                            else: #tipe_informasi == 'ANALISIS_SIFAT HUJAN'
                                indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, _, _, _ = dataframe_indo(dataframe, tipe_informasi="ANALISIS_SIFAT_HUJAN")
                                df = prov_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal (%)': 'bawah_normal', 'Normal (%)': 'normal', 'Atas Normal (%)' : 'atas_normal'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor



                                

                        else: #periode == 'DASARIAN \
                            if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
                                indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_indo(dataframe, tipe_informasi="ANALISIS_CURAH_HUJAN")
                                df = prov_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah (%)': 'rendah', 'Menengah (%)': 'menengah', 'Tinggi (%)' : 'tinggi', 'Sangat Tinggi (%)': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das


                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor


                                

                            else: #tipe_informasi == 'ANALISIS_SIFAT HUJAN'
                                indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, _, _, _ = dataframe_indo(dataframe, tipe_informasi="ANALISIS_SIFAT_HUJAN")
                                df = prov_df_complete_clean


                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal (%)': 'bawah_normal', 'Normal (%)': 'normal', 'Atas Normal (%)' : 'atas_normal'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das


                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor




                    else: # wilayah_ref == UPT
                        
                        print(wilayah_ref)
                        sde_table_path = prov_sde[wilayah_ref]
                        

                        if periode == 'BULANAN':
                            if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
                                prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_table[wilayah_ref])
                                
                                # Add provinsi into table
                                df = prov_df_pivot

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'PROVINSI'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor



                                # Add kabupaten into table

                                df = kab_df_complete_clean_copy

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'KABUPATEN'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor



                                # Add kecamatan into table

                                df = kec_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['wilayah'] = df['wilayah'].str.upper() 
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'KABUPATEN'
                                df['admin_2'] = df['KABUPATEN']

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor




                            else: #tipe_informasi == 'ANALISIS_SIFAT HUJAN'
                                prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, _, _, _ = dataframe_upt(dataframe, tipe_informasi, nama_prov_table[wilayah_ref])
                                
                                # Add provinsi into table
                                df = prov_df_pivot

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'PROVINSI'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor


                                # Add kabupaten into table

                                df = kab_df_complete_clean_copy
                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'KABUPATEN'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor




                                # Add kecamatan into table
                                df = kec_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['wilayah'] = df['wilayah'].str.upper() 
                                df['periode_informasi'] = 'Bulanan'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_bln_str
                                df['date_datetime'] = date_input_bln
                                df['admin_1'] = 'KABUPATEN'
                                df['admin_2'] = df['KABUPATEN']

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor


                            

                        else: # periode == 'DASARIAN'
                            if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
                                prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah = dataframe_upt(dataframe, tipe_informasi, nama_prov_table[wilayah_ref])
                                

                                # Add provinsi into table
                                df = prov_df_pivot

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'PROVINSI'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor



                                # Add kabupaten into table

                                df = kab_df_complete_clean_copy

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'KABUPATEN'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor



                                # Add kecamatan into table

                                df = kec_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Rendah': 'rendah', 'Menengah': 'menengah', 'Tinggi' : 'tinggi', 'Sangat Tinggi': 'sangat_tinggi'})
                                df['wilayah'] = df['wilayah'].str.upper() 
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'CH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'KABUPATEN'
                                df['admin_2'] = df['KABUPATEN']

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor


                                

                            else: #tipe_informasi == 'ANALISIS_SIFAT HUJAN'
                                prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, _, _, _ = dataframe_upt(dataframe, tipe_informasi, nama_prov_table[wilayah_ref])
                                

                                # Add provinsi into table
                                df = prov_df_pivot

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'PROVINSI'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor


                                # Add kabupaten into table

                                df = kab_df_complete_clean_copy
                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'PROVINSI'
                                df['admin_2'] = 'KABUPATEN'

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor




                                # Add kecamatan into table
                                df = kec_df_complete_clean

                                df = df.rename(columns={'Wilayah' : 'wilayah', 'Bawah Normal': 'bawah_normal', 'Normal': 'normal', 'Atas Normal' : 'atas_normal'})
                                df['wilayah'] = df['wilayah'].str.upper() 
                                df['periode_informasi'] = 'Dasarian'
                                df['jenis_informasi'] = 'SH'
                                df['tipe_informasi'] = 'Analisis'
                                df['date'] = date_input_das_str
                                df['date_datetime'] = date_input_das
                                df['admin_1'] = 'KABUPATEN'
                                df['admin_2'] = df['KABUPATEN']

                                # Use ArcPy to create a search cursor and read the data
                                fields = [field.name for field in arcpy.ListFields(sde_table_path)]
                                data = []
                                with arcpy.da.SearchCursor(sde_table_path, fields) as cursor:
                                    for row in cursor:
                                        data.append(row)
                                # Convert the data to a pandas DataFrame
                                df_sde = pd.DataFrame(data, columns=fields)
                                df_sde['date_datetime'] = pd.to_datetime(df_sde['date_datetime'], errors='coerce')

                                
                                # Filter SDE data for relevant entries
                                df_filtered = df_sde[~((df_sde['tipe_informasi'] == 'Analisis') & 
                                    (df_sde['date_datetime'] < two_months_ago))]

                                # Set index to see the difference
                                df.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)
                                df_filtered.set_index(['wilayah', 'periode_informasi', 'jenis_informasi', 'tipe_informasi', 'date', 'admin_1', 'admin_2'], inplace=True)


                                df_filtered.update(df)

                                # Mencari baris di df yang tidak ada di df_filtered
                                new_rows = df[~df.index.isin(df_filtered.index)]

                                # Menggabungkan baris baru ke df_B
                                df_combined = pd.concat([df_filtered, new_rows])

                                df_combined.reset_index(inplace=True)

                                # Ensure all necessary columns are present
                                sde_table_columns = [field.name for field in arcpy.ListFields(sde_table_path)]
                                for col in sde_table_columns:
                                    if col not in df_combined.columns:
                                        df_combined[col] = None

                                df_combined = df_combined[sde_table_columns]
                                data_to_insert = df_combined.to_dict(orient='records')

                                # Truncate the SDE table
                                arcpy.management.TruncateTable(sde_table_path)

                                # Insert the filtered data back into the SDE table
                                with arcpy.da.InsertCursor(sde_table_path, sde_table_columns) as cursor:
                                    for row in data_to_insert:
                                        cursor.insertRow([row[col] for col in sde_table_columns])

                                del cursor







                except Exception as e:
                    print(f"Error di pengolahan {wilayah_ref} {e}")
                    continue

    print("Proses Update Table selesai")
    

