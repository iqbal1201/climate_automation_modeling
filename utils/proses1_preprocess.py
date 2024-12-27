import arcpy
import os
import datetime
import pandas as pd
# import geopandas as gpd
import datetime
import locale
from utils.dasarian import get_current_dasarian
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
import warnings
warnings.filterwarnings("ignore")
from dotenv import load_dotenv
load_dotenv()

# Get date for previous month and previous dasarian

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


## Get folder structure
main_folder = os.getenv("MAIN_FOLDER")
folder_bulanan = r'BULANAN'
folder_dasarian = r'DASARIAN'
file_name_bulanan = f'BlendGSMAP_POS.{year_bln}{month_bln}.xls'
file_name_dasarian = f'BlendGSMAP_POS.{year_das}{month_das}dec{current_dasarian}.xls'

# Get full folder path
file_path_bulanan = os.path.join(main_folder, folder_bulanan)
file_path_dasarian = os.path.join(main_folder, folder_dasarian)

# File input
file_input_bulanan = os.path.join(file_path_bulanan, file_name_bulanan)
file_input_dasarian = os.path.join(file_path_dasarian, file_name_dasarian)


# Environment ArcPY
arcpy.env.overwriteOutput = True


# Set parameter
# Parameter
sheet_name = "Sheet 1"
x_field="LON",
y_field="LAT",
z_field=None,
coordinate_system='GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'


# Get excel to shapefiles    
class Preprocessing():

    def __init__(self, fgdb_temp, file_input):
        self.fgdb_temp = fgdb_temp
        self.file_input = file_input

    
    def Excel_to_Feature(self, output_table_name, output_feature_name):
        arcpy.conversion.ExcelToTable(
            Input_Excel_File = self.file_input,
            Output_Table = os.path.join(self.fgdb_temp, output_table_name),
            Sheet = "Sheet 1",
            field_names_row = 1,
            cell_range="")
        
        arcpy.management.XYTableToPoint(
            in_table = os.path.join(self.fgdb_temp, output_table_name),
            out_feature_class=os.path.join(self.fgdb_temp, output_feature_name),
            x_field = "LON",
            y_field = "LAT",
            z_field = None,
            coordinate_system = 'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]];-400 -400 1000000000;-100000 10000;-100000 10000;8.98315284119521E-09;0.001;0.001;IsHighPrecision'
        )
        
        return os.path.join(self.fgdb_temp, output_feature_name)