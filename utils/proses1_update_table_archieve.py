


def define_data_path(wilayah, wilayah_folder, tipe_informasi, jenis_informasi, periode_informasi, date, format, filename):
    import datetime
    from datetime import timedelta
    from utils.dasarian import get_current_dasarian
    from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month

    # current_date =  datetime.datetime.now()
    # lag_date_month = current_date - datetime.timedelta(days=30)
    # lag_date_das, _ = get_current_dasarian_pseudo()
    # date =  lag_date_month.strftime('%Y-%m-%d')
    # year_lag = lag_date_month.year
    # month_lag = lag_date_month.strftime("%m")
    # year = current_date.year
    # month = current_date.strftime("%m")
    
    
    date_input_bln, date_input_bln_str = first_date_of_previous_month()
    date_input_das, date_input_das_str = first_date_of_dasarian()

    year_bln = date_input_bln.year
    month_bln = date_input_bln.strftime("%m")
    month_name_bln = date_input_bln.strftime("%B")

    year_das = date_input_das.year
    month_das = date_input_das.strftime("%m")
    month_name_das = date_input_das.strftime("%B")
    current_dasarian, current_dasarian_text = get_current_dasarian(date_input_das)

    date_format_bln = f"{year_bln}.{month_bln}"
    date_format_das = f"{year_das}.{month_das}.DAS0{current_dasarian}"

    if wilayah == 'INDONESIA':
        if periode_informasi == 'Bulanan':
            path = f'//fileserveriklim.bmkg.go.id/data_bmkg/data_automation/PINTER_IKLIM/INDONESIA/ANALISIS_BULANAN/{format}/{date_format_bln}/{filename}'
        elif periode_informasi == 'Dasarian':
            path = f'//fileserveriklim.bmkg.go.id/data_bmkg/data_automation/PINTER_IKLIM/INDONESIA/ANALISIS_DASARIAN/{format}/{date_format_das}/{filename}'
    
    else: #wilayah == UPT
        if periode_informasi == 'Bulanan':
            path = f'//fileserveriklim.bmkg.go.id/data_bmkg/data_automation/PINTER_IKLIM/PROVINSI/{wilayah_folder}/ANALISIS_BULANAN/{format}/{date_format_bln}/{filename}'
        elif periode_informasi == 'Dasarian':
            path = f'//fileserveriklim.bmkg.go.id/data_bmkg/data_automation/PINTER_IKLIM/PROVINSI/{wilayah_folder}/ANALISIS_DASARIAN/{format}/{date_format_das}/{filename}'


    data_to_add = []

    data_to_add.append(wilayah)
    data_to_add.append(tipe_informasi)
    data_to_add.append(jenis_informasi)
    data_to_add.append(periode_informasi)
    data_to_add.append(date)
    data_to_add.append(format)
    data_to_add.append(filename)
    data_to_add.append(path)

    return data_to_add
     

def update_table_path(data_to_add):
    table_sde = r'F:\ASSET\spatial\BMKG_PinterIklim\PostgreSQL-gisdbiklim-geodb_bmkg(sde).sde\geodb_bmkg.sde.archiving'
    field_names = ["wilayah", 'tipe_informasi', 'jenis_informasi', 'periode_informasi', 'date', 'format', 'filename', 'path']

    import arcpy
    try:
    # Use InsertCursor to insert a row into the specified table
        with arcpy.da.InsertCursor(table_sde, field_names) as cursor:
            cursor.insertRow(data_to_add)
            print("Data inserted successfully.")
    except Exception as e:
        print(f"Error inserting data: {e}")
