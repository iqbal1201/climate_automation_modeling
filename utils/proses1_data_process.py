import arcpy
import os
import datetime
import pandas as pd
# import geopandas as gpd
from config import extent_pulau, pulau_feature, titik_grid, nama_prov, poly_kecamatan, nama_prov_folder
from utils.proses1_raster_mosaic import copy_raster, add_raster_and_update_fields, delete_old_rasters
from utils.proses1_archiving import ArchivingFolder
from utils.dasarian import get_current_dasarian
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
from utils.proses1_log_table import log_to_sde
from utils.proses1_update_polygon import update_polygon_bln, update_polygon_das
import arcgis
from arcgis.features import GeoAccessor
import matplotlib.pyplot as plt
import datetime
import locale
from dotenv import load_dotenv
load_dotenv()


# Get date for previous month and previous dasarian
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



# Set parameter
gridsize_pkecil = os.getenv("GRID_PKECIL")
gridsize_pbesar= os.getenv("GRID_PBESAR")


# Set folder structure
output_folder = os.getenv("OUTPUT_FOLDER")
output_level_ind = 'INDONESIA'
output_level_prov = 'PROVINSI'
output_tipe_bln = 'ANALISIS_BULANAN'
output_tipe_das = 'ANALISIS_DASARIAN'



# All output folder path Bulanan - Prov
output_prov = os.path.join(output_folder, output_level_prov)


# Set file to loop code
pulau_reference = os.getenv("PULAU_REFERENCE")
pulau_besar_merge = os.getenv("PULAU_BESAR_MERGE")


# Set data for I/O
raster_loc = os.getenv("RASTER_LOC")
fgdb_input = os.getenv("FGDB_TEMP")
fgdb_temp = os.getenv("FGDB_TEMP")
mosaic_bln_ch= os.getenv("MOSAIC_BLN_ACH")
mosaic_bln_sh= os.getenv("MOSAIC_BLN_ASH")
mosaic_das_ch= os.getenv("MOSAIC_DAS_ACH")
mosaic_das_sh= os.getenv("MOSAIC_DAS_ASH")
main_output_folder = os.getenv("OUTPUT_FOLDER")
input_data_bln = os.path.join(fgdb_temp, 'output_2_proses1_feature_point_bln')
input_data_das = os.path.join(fgdb_temp, 'output_2_proses1_feature_point_das')


# Reference polygon in dasboard
poly_ach_bln = os.getenv("POLY_BLN_ACH")
poly_ash_bln = os.getenv("POLY_BLN_ASH")
poly_ach_das = os.getenv("POLY_DAS_ACH")
poly_ash_das = os.getenv("POLY_DAS_ASH")

# Environment ArcPY
arcpy.env.overwriteOutput = True


# Function for interpolaion

def interpolasi_bln(input_data):

    print("PROSES ANALISIS BULANAN DIMULAI . . .")
    log_to_sde(message = "PROSES ANALISIS BULANAN DIMULAI . . .", status="INFO", tipe_progress="Bulanan", tipe_informasi="Analisis")
    
    raster_ACH_to_merge = []
    raster_ASH_to_merge = []
    raster_ACH_to_merge_tif = []
    raster_ASH_to_merge_tif = []
    ACH_to_merge = []
    ASH_to_merge = []
    CSV_to_merge = []

    poly_indo_ach = None
    poly_indo_ash = None

    with arcpy.da.SearchCursor(pulau_reference, [["Pulau_Singkat", ["Is_Besar"]]]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
        for r in cursors:
            try:
                if r[1] == "False":  # val False = Pulau Kecil dan va True = Pulau Besar
                    pulau_kecil = r[0]
                    print(f"Memulai Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} . . .", status="INFO", tipe_progress="Bulanan", tipe_informasi="Analisis")

                    ####### Proses untuk kategori pulau kecil\
                    ####### Proses ACH untuk kategori pulau kecil
                    # Create new folder
                    
                    pembuatan_archiving = ArchivingFolder(output_folder)
                    output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='TIFF', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)

                    # Start Process

                    with arcpy.EnvManager(extent=extent_pulau[pulau_kecil], mask=pulau_feature[pulau_kecil]):
                        arcpy.ga.IDW(
                            in_features= input_data,
                            z_field="CH",
                            out_ga_layer=None,
                            out_raster=os.path.join(output_loc_tiff, f"ach_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif"),
                            cell_size=gridsize_pkecil,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )
                    raster_ach_pk = arcpy.Raster(os.path.join(output_loc_tiff, f"ach_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif"))
                    raster_ach_pk_copy = os.path.join(raster_loc, f"ach_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif")

                    copy_raster(raster_ach_pk, raster_ach_pk_copy)

                    row_list_ch = (raster_ach_pk_copy, f'{pulau_kecil}')

                    raster_ACH_to_merge.append(row_list_ch)

                    raster_ACH_to_merge_tif.append(raster_ach_pk)
                    

                    print(f"Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", tipe_progress="Bulanan", tipe_informasi="Analisis")



                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai ...")
                    log_to_sde(message = f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai ...", status="INFO", tipe_progress="Bulanan", tipe_informasi="Analisis")
                    

                    pembuatan_archiving = ArchivingFolder(output_folder)
                    output_loc_csv = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='CSV', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)
                    

                    titik_grid_extract_pk = os.path.join(fgdb_temp, f"Titik_extract_{pulau_kecil}_{year_bln}{month_bln}")
                    arcpy.management.CopyFeatures(in_features=titik_grid[pulau_kecil], out_feature_class=titik_grid_extract_pk)
                    point_extracted_pk = arcpy.sa.ExtractMultiValuesToPoints(titik_grid_extract_pk, [[raster_ach_pk, "CH"]], "NONE")
                    # point_extracted_ch.save()
                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Extract Point Pulau Kecil: {pulau_kecil} selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")

                    

                    print(f"Proses Reclassify ACH Pulau Kecil: {pulau_kecil} dimulai . . . . . . . . . . . .")
                    log_to_sde(message = f"Proses Reclassify ACH Pulau Kecil: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    out_raster_ach_pk = arcpy.sa.Reclassify(
                        in_raster=raster_ach_pk,
                        reclass_field="VALUE",
                        remap="0 20 1;20 50 2;50 100 3;100 150 4;150 200 5;200 300 6;300 400 7;400 500 8;500 10000 9",
                        missing_values="DATA")
                    
                    out_raster_ach_pk.save(os.path.join(fgdb_temp, f"Reclass_ACH_{pulau_kecil}_{year_bln}{month_bln}"))
                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")



                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai . . . . ")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    # Pembuatan archive
                    output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)
                    Output_polygon_features_ach = os.path.join(fgdb_temp, f"ach_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}")
                    arcpy.conversion.RasterToPolygon(in_raster=out_raster_ach_pk, out_polygon_features=Output_polygon_features_ach)
                    arcpy.management.AddFields(in_table=Output_polygon_features_ach, field_description= "CH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                    arcpy.management.CalculateField(
                                in_table=Output_polygon_features_ach,
                                field="CH",
                                expression="ch(!gridcode!)",
                                expression_type="PYTHON3",
                                code_block="""def ch(x):
                                if x == 1:
                                    return "0-20"
                                elif x == 2:
                                    return "21-50"
                                elif x == 3:
                                    return "51-100"
                                elif x == 4:
                                    return "101-150"
                                elif x == 5:
                                    return "151-200"
                                elif x == 6:
                                    return "201-300"
                                elif x == 7:
                                    return "301-400"
                                elif x == 8:
                                    return "401-500"
                                elif x ==9 :
                                    return ">500"
                                """,
                                field_type="TEXT",
                                enforce_domains="NO_ENFORCE_DOMAINS")
                    arcpy.management.CalculateField(
                                in_table=Output_polygon_features_ach,
                                field="Kategori",
                                expression="cat(!gridcode!)",
                                expression_type="PYTHON3",
                                code_block="""def cat(x):
                                if x == 1:
                                    return "Rendah"
                                elif x == 2:
                                    return "Rendah"
                                elif x == 3:
                                    return "Rendah"
                                elif x == 4:
                                    return "Menengah"
                                elif x == 5:
                                    return "Menengah"
                                elif x == 6:
                                    return "Menengah"
                                elif x == 7:
                                    return "Tinggi"
                                elif x == 8:
                                    return "Sangat Tinggi"
                                elif x ==9 :
                                    return "Sangat Tinggi"
                                """,
                                field_type="TEXT",
                                enforce_domains="NO_ENFORCE_DOMAINS")
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Periode",
                                            expression=f'"{month_name_bln} {year_bln}"',
                                            expression_type="PYTHON3"
                                        )
                    arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ach,
                                        field="Informasi",
                                        expression='"Curah Hujan"',
                                        expression_type="PYTHON3"
                                    )
                    
                    poly_kec = poly_kecamatan[pulau_kecil]


                    Output_polygon_features_ach_union = os.path.join(output_loc_shp, f"ach_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}")
                    arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ach], 
                                         out_feature_class=Output_polygon_features_ach_union)
                    
                    arcpy.management.AddField(
                                in_table=Output_polygon_features_ach_union,
                                field_name="Area_H", field_type="DOUBLE")
                    
                    arcpy.management.CalculateGeometryAttributes(
                            in_features=Output_polygon_features_ach_union,
                            geometry_property=[["Area_H", "AREA_GEODESIC"]],
                            area_unit="HECTARES")
                    
                    # Menggabungkan polygon untuk di merge
                    ACH_to_merge.append(Output_polygon_features_ach)
                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    print("\n")



                    ####### Proses ASH untuk kategori pulau kecil
                    print(f"Memulai Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ASH Pulau Kecil: {pulau_kecil}", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    with arcpy.EnvManager(extent=extent_pulau[pulau_kecil], mask=pulau_feature[pulau_kecil]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="SH_",
                            out_ga_layer=None,
                            out_raster=os.path.join(output_loc_tiff, f"ash_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif"),
                            cell_size=gridsize_pkecil,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )

                    raster_ash_pk = arcpy.Raster(os.path.join(output_loc_tiff, f"ash_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif"))

                    raster_ash_pk_copy = os.path.join(raster_loc, f"ash_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.tif")

                    copy_raster(raster_ash_pk, raster_ash_pk_copy)

                    row_list_sh = (raster_ash_pk_copy, f'{pulau_kecil}')

                    raster_ASH_to_merge.append(row_list_sh)

                    raster_ASH_to_merge_tif.append(raster_ash_pk)


                    print(f"Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")


                    # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {pulau_kecil} dimulai . . .. ")
                    # arcpy.management.AddRastersToMosaicDataset(
                    #                 in_mosaic_dataset= mosaic_bln_sh,
                    #                 raster_type="Raster Dataset",
                    #                 input_path= raster_ash_pk,
                    #                 update_cellsize_ranges="UPDATE_CELL_SIZES",
                    #                 update_boundary="UPDATE_BOUNDARY",
                    #                 update_overviews="NO_OVERVIEWS",
                    #                 maximum_pyramid_levels=None,
                    #                 maximum_cell_size=0,
                    #                 minimum_dimension=1500,
                    #                 spatial_reference=None,
                    #                 filter="",
                    #                 sub_folder="SUBFOLDERS",
                    #                 duplicate_items_action="ALLOW_DUPLICATES",
                    #                 build_pyramids="BUILD_PYRAMIDS",
                    #                 calculate_statistics="CALCULATE_STATISTICS",
                    #                 build_thumbnails="NO_THUMBNAILS",
                    #                 operation_description="",
                    #                 force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
                    #                 estimate_statistics="ESTIMATE_STATISTICS",
                    #                 aux_inputs=None,
                    #                 enable_pixel_cache="NO_PIXEL_CACHE",
                    #                 cache_location=r"C:\Users\mjanuadi\AppData\Local\ESRI\rasterproxies\Mosaic_Dataset_SH")
                    # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {pulau_kecil} selesai ")


                    
                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai . . .")
                    log_to_sde(message = f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    point_extracted_pk = os.path.join(fgdb_temp, f"Titik_extract_{pulau_kecil}_{year_bln}{month_bln}")
                    arcpy.sa.ExtractMultiValuesToPoints(point_extracted_pk, [[raster_ash_pk, "SH"]], "NONE")
                    # point_extracted_sh.save()
                    arcpy.management.AddFields(in_table=point_extracted_pk, field_description=[["LAT", "DOUBLE", "Latitude", "", "", ""], ["LONG", "DOUBLE", "Longitude", "", "", ""]])[0]
                    arcpy.management.CalculateGeometryAttributes(in_features=point_extracted_pk, geometry_property=[["LAT", "POINT_Y"], ["LONG", "POINT_X"]], coordinate_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", 
                                                                            coordinate_format="DD")[0]
                    print(f"Proses Extract Point Provinsi: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Extract Point Provinsi: {pulau_kecil} selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")



                    print(f"Proses Export to csv Provinsi: {pulau_kecil} dimulai . . .")
                    log_to_sde(message = f"Proses Export to csv Provinsi: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    out_csv_table_pk = os.path.join(output_loc_csv, f"bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}.csv")
                    arcpy.conversion.ExportTable(
                                    in_table= point_extracted_pk,
                                    out_table= out_csv_table_pk,
                                    where_clause="",
                                    use_field_alias_as_name="NOT_USE_ALIAS",
                                    field_mapping=None,
                                    sort_field=None)
                    
                    # Menggabungkan csv untuk di merge
                    CSV_to_merge.append(out_csv_table_pk)
                    print(f"Proses Export to csv Provinsi: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Export to csv Provinsi: {pulau_kecil} selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")


                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} dimulai . . . . . . . . . . . .")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    out_raster_ash_pk = arcpy.sa.Reclassify(
                        in_raster=raster_ash_pk,
                        reclass_field="VALUE",
                        remap="0 30 1;30 50 2;50 84 3;84 115 4;115 150 5;150 200 6;200 10000 7",
                        missing_values="DATA")
                    
                    out_raster_ash_pk.save(os.path.join(fgdb_temp, f"Reclass_ACH_{pulau_kecil}_{year_bln}{month_bln}"))
                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                



                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai . . . .")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    Output_polygon_features_ash = os.path.join(fgdb_temp, f"ash_bln_{pulau_kecil}_ver_{year_bln}{month_bln}")
                    arcpy.conversion.RasterToPolygon(in_raster=out_raster_ash_pk, out_polygon_features=Output_polygon_features_ash)
                    arcpy.management.AddFields(in_table=Output_polygon_features_ash, field_description= "SH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="SH",
                                            expression="sh(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def sh(x):
                                            if x == 1:
                                                return "0-30"
                                            elif x == 2:
                                                return "31-50"
                                            elif x == 3:
                                                return "51-84"
                                            elif x == 4:
                                                return "85-115"
                                            elif x == 5:
                                                return "116-150"
                                            elif x == 6:
                                                return "151-200"
                                            elif x == 7:
                                                return ">200"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Kategori",
                                            expression="kategori(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def kategori(x):
                                            if x == 1:
                                                return "Bawah Normal"
                                            elif x == 2:
                                                return "Bawah Normal"
                                            elif x == 3:
                                                return "Bawah Normal"
                                            elif x == 4:
                                                return "Normal"
                                            elif x == 5:
                                                return "Atas Normal"
                                            elif x == 6:
                                                return "Atas Normal"
                                            elif x == 7:
                                                return "Atas Normal"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                    
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Periode",
                                            expression=f'"{month_name_bln} {year_bln}"',
                                            expression_type="PYTHON3"
                                        )
                    arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ash,
                                        field="Informasi",
                                        expression='"Sifat Hujan"',
                                        expression_type="PYTHON3"
                                    )
                    

                    poly_kec = poly_kecamatan[pulau_kecil]
                    
                    Output_polygon_features_ash_union = os.path.join(output_loc_shp, f"ash_bln_{pulau_kecil.lower()}_ver_{year_bln}{month_bln}")
                    arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ash], 
                                         out_feature_class=Output_polygon_features_ash_union)
                    
                    arcpy.management.AddField(
                                in_table=Output_polygon_features_ash_union,
                                field_name="Area_H", field_type="DOUBLE")
                    
                    arcpy.management.CalculateGeometryAttributes(
                            in_features=Output_polygon_features_ash_union,
                            geometry_property=[["Area_H", "AREA_GEODESIC"]],
                            area_unit="HECTARES")

                    # menggabungkan polygon untuk di merge
                    ASH_to_merge.append(Output_polygon_features_ash)
                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    print("\n")


                ####### Proses untuk kategori pulau besar
                ####### Proses ACH Pulau Besar
                else:
                    pulau_besar = r[0]
                    print(f"Memulai Proses Interpolasi ACH Pulau Besar: {pulau_besar} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ACH Pulau Besar: {pulau_besar}", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    with arcpy.EnvManager(extent=extent_pulau[pulau_besar], mask=pulau_feature[pulau_besar]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="CH",
                            out_ga_layer=None,
                            out_raster=os.path.join(fgdb_temp, f"interpolasi_ACH_Pulau_{pulau_besar}_{year_bln}{month_bln}"),
                            cell_size=gridsize_pbesar,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )
                    raster_ach_pb = arcpy.Raster(os.path.join(fgdb_temp, f"interpolasi_ACH_Pulau_{pulau_besar}_{year_bln}{month_bln}"))

                   

                    


                    print(f"Proses Interpolasi ACH Pulau Besar: {pulau_besar} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ACH Pulau Besar: {pulau_besar} telah selesai", status="INFO", 
                               tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    print("\n")

                    ######### Proses Masking ACH
                    print(f"Proses Masking ACH Pulau Besar: {pulau_besar} dimulai . . .")
                    with arcpy.da.SearchCursor(pulau_besar_merge, [["Pulau", ["Provinsi_Singkat"]]]) as masks:
                        for r in masks:
                            pulau_mask = r[0]
                            provinsi = r[1]
                            if pulau_mask == pulau_besar:
                                print(f"Memulai Mask Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Mask Provinsi: {provinsi}", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                                # Membuat archive folder
                                print("Membuat Archive")
                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='TIFF', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                print("Selesai Archive")


                                Extract_rast_ch = os.path.join(output_loc_tiff, f"ach_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}.tif")
                                Extract_by_Mask = Extract_rast_ch
                                Extract_rast_ch = arcpy.sa.ExtractByMask(raster_ach_pb, pulau_feature[provinsi], "INSIDE", extent_pulau[provinsi])
                                Extract_rast_ch.save(Extract_by_Mask)

                                Extract_rast_ch_copy = os.path.join(raster_loc, f"ach_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}.tif")

                                copy_raster(Extract_rast_ch, Extract_rast_ch_copy)

                                row_list_ch = (Extract_rast_ch_copy, f'{provinsi}')

                                raster_ACH_to_merge.append(row_list_ch)

                                raster_ACH_to_merge_tif.append(Extract_rast_ch)

                                

                                


                                print(f"Proses Mask Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Memulai Mask Provinsi: {provinsi} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                                
                                # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {provinsi} dimulai . . .. ")
                                # arcpy.management.AddRastersToMosaicDataset(
                                #     in_mosaic_dataset= mosaic_bln_ch,
                                #     raster_type="Raster Dataset",
                                #     input_path= Extract_rast_ch,
                                #     update_cellsize_ranges="UPDATE_CELL_SIZES",
                                #     update_boundary="UPDATE_BOUNDARY",
                                #     update_overviews="NO_OVERVIEWS",
                                #     maximum_pyramid_levels=None,
                                #     maximum_cell_size=0,
                                #     minimum_dimension=1500,
                                #     spatial_reference=None,
                                #     filter="",
                                #     sub_folder="SUBFOLDERS",
                                #     duplicate_items_action="ALLOW_DUPLICATES",
                                #     build_pyramids="BUILD_PYRAMIDS",
                                #     calculate_statistics="CALCULATE_STATISTICS",
                                #     build_thumbnails="NO_THUMBNAILS",
                                #     operation_description="",
                                #     force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
                                #     estimate_statistics="ESTIMATE_STATISTICS",
                                #     aux_inputs=None,
                                #     enable_pixel_cache="NO_PIXEL_CACHE",
                                #     cache_location=r"C:\Users\mjanuadi\AppData\Local\ESRI\rasterproxies\Mosaic_Dataset_CH")
                                # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {provinsi} selesai ")


                                print(f"Proses Extract Point Provinsi: {provinsi} dimulai ...")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                titik_grid_extract_pb = os.path.join(fgdb_temp, f"Titik_extract_{provinsi}_{year_bln}{month_bln}")
                                arcpy.management.CopyFeatures(in_features=titik_grid[provinsi], out_feature_class=titik_grid_extract_pb)
                                point_extracted_pb = arcpy.sa.ExtractMultiValuesToPoints(titik_grid_extract_pb, [[Extract_rast_ch, "CH"]], "NONE")
                                # point_extracted_ch.save()
                                print(f"Proses Extract Point Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")




                                print(f"Memulai Reclassify Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Reclassify Provinsi: {provinsi}", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                out_raster_ach_pb = arcpy.sa.Reclassify(in_raster=Extract_rast_ch,
                                                                reclass_field="VALUE",
                                                                remap="0 20 1;20 50 2;50 100 3;100 150 4;150 200 5;200 300 6;300 400 7;400 500 8;500 10000 9",
                                                                missing_values="DATA")
                                
                                out_raster_ach_pb.save(os.path.join(fgdb_temp, f"Reclass_ACH_{provinsi}_{year_bln}{month_bln}"))
                                print(f"Proses Reclassify Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Reclassify Provinsi: {provinsi} telah selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                            

                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai . . . .")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                # Membuat archive folder
                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                Output_polygon_features_ach = os.path.join(fgdb_temp, f"ach_bln_{provinsi}_ver_{year_bln}{month_bln}")
                                arcpy.conversion.RasterToPolygon(in_raster=out_raster_ach_pb, out_polygon_features=Output_polygon_features_ach)
                                arcpy.management.AddFields(in_table=Output_polygon_features_ach, field_description= "CH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="CH",
                                            expression="ch(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def ch(x):
                                            if x == 1:
                                                return "0-20"
                                            elif x == 2:
                                                return "21-50"
                                            elif x == 3:
                                                return "51-100"
                                            elif x == 4:
                                                return "101-150"
                                            elif x == 5:
                                                return "151-200"
                                            elif x == 6:
                                                return "201-300"
                                            elif x == 7:
                                                return "301-400"
                                            elif x == 8:
                                                return "401-500"
                                            elif x ==9 :
                                                return ">500"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Kategori",
                                            expression="cat(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def cat(x):
                                            if x == 1:
                                                return "Rendah"
                                            elif x == 2:
                                                return "Rendah"
                                            elif x == 3:
                                                return "Rendah"
                                            elif x == 4:
                                                return "Menengah"
                                            elif x == 5:
                                                return "Menengah"
                                            elif x == 6:
                                                return "Menengah"
                                            elif x == 7:
                                                return "Tinggi"
                                            elif x == 8:
                                                return "Sangat Tinggi"
                                            elif x ==9 :
                                                return "Sangat Tinggi"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Periode",
                                            expression=f'"{month_name_bln} {year_bln}"',
                                            expression_type="PYTHON3"
                                        )
                                arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ach,
                                        field="Informasi",
                                        expression='"Curah Hujan"',
                                        expression_type="PYTHON3"
                                    )
                                

                                poly_kec = poly_kecamatan[provinsi]

                                Output_polygon_features_ach_union = os.path.join(output_loc_shp, f"ach_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}")
                                arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ach], 
                                         out_feature_class= Output_polygon_features_ach_union)
                                
                                
                                arcpy.management.AddField(
                                in_table=Output_polygon_features_ach_union,
                                field_name="Area_H", field_type="DOUBLE")
                    
                                arcpy.management.CalculateGeometryAttributes(
                                        in_features=Output_polygon_features_ach_union,
                                        geometry_property=[["Area_H", "AREA_GEODESIC"]],
                                        area_unit="HECTARES")

                                

                                
                                # Menggabungkan polygon untuk di merge
                                ACH_to_merge.append(Output_polygon_features_ach)
                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                print("\n")

                            

                    ####### Proses ASH Pulau Besar
                    ####### Proses Interpolasi ASH
                    print(f"Memulai Proses Interpolasi ASH Pulau Besar: {pulau_besar}")
                    log_to_sde(message = f"Memulai Proses Interpolasi ASH Pulau Besar: {pulau_besar}", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                    with arcpy.EnvManager(extent=extent_pulau[pulau_besar], mask=pulau_feature[pulau_besar]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="SH_",
                            out_ga_layer=None,
                            out_raster=os.path.join(fgdb_temp, f"interpolasi_ASH_Pulau_{pulau_besar}_{year_bln}{month_bln}"),
                            cell_size=gridsize_pbesar,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )

                    raster_ash = arcpy.Raster(os.path.join(fgdb_temp, f"interpolasi_ASH_Pulau_{pulau_besar}_{year_bln}{month_bln}"))

                    

                    print(f"Proses Interpolasi ASH Pulau Besar: {pulau_besar} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ASH Pulau Besar: {pulau_besar} telah selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                    
                    print("\n")

                    ######### Proses Masking ASH
                    print(f"Proses Masking ASH Pulau Besar: {pulau_besar} dimulai . . .")
                    log_to_sde(message = f"PProses Masking ASH Pulau Besar: {pulau_besar} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")




                    with arcpy.da.SearchCursor(pulau_besar_merge, [["Pulau", ["Provinsi_Singkat"]]]) as masks:
                        for r in masks:
                            pulau_mask = r[0]
                            provinsi = r[1]
                            if pulau_mask == pulau_besar:
                                print(f"Memulai Mask ASH Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Mask ASH Provinsi: {provinsi}", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                            output_tipe_periode=output_tipe_bln, tipe='TIFF', 
                                                            nama_prov=nama_prov_folder, pulau_kecil=provinsi)



                                Extract_rast_sh = os.path.join(output_loc_tiff, f"ash_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}.tif")
                                Extract_by_Mask = Extract_rast_sh
                                Extract_rast_sh = arcpy.sa.ExtractByMask(raster_ash, pulau_feature[provinsi], "INSIDE", extent_pulau[provinsi])
                                Extract_rast_sh.save(Extract_by_Mask)


                                Extract_rast_sh_copy = os.path.join(raster_loc, f"ash_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}.tif")

                                copy_raster(Extract_rast_sh, Extract_rast_sh_copy)

                                row_list_sh = (Extract_rast_sh_copy, f'{provinsi}')

                                raster_ASH_to_merge.append(row_list_sh)


                                raster_ASH_to_merge_tif.append(Extract_rast_sh)






                                print(f"Proses Mask Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Mask Provinsi: {provinsi} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


                                print(f"Proses Extract Point Provinsi: {provinsi} dimulai . . .")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                point_extracted_pb = os.path.join(fgdb_temp, f"Titik_extract_{provinsi}_{year_bln}{month_bln}")
                                arcpy.sa.ExtractMultiValuesToPoints(point_extracted_pb, [[Extract_rast_sh, "SH"]], "NONE")
                                arcpy.management.AddFields(in_table=point_extracted_pb, field_description=[["LAT", "DOUBLE", "Latitude", "", "", ""], ["LONG", "DOUBLE", "Longitude", "", "", ""]])[0]
                                arcpy.management.CalculateGeometryAttributes(in_features=point_extracted_pb, geometry_property=[["LAT", "POINT_Y"], ["LONG", "POINT_X"]],coordinate_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", 
                                                                            coordinate_format="DD")[0]
                                # point_extracted_sh.save()
                                print(f"Proses Extract Point Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")



                                print(f"Proses Export to csv Provinsi: {provinsi} dimulai . . .")
                                log_to_sde(message = f"Proses Export to csv Provinsi: {provinsi} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_csv = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='CSV', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                out_csv_table_pb = os.path.join(output_loc_csv, f"bln_{provinsi.lower()}_ver_{year_bln}{month_bln}.csv")
                                arcpy.conversion.ExportTable(
                                    in_table= point_extracted_pb,
                                    out_table= out_csv_table_pb,
                                    where_clause="",
                                    use_field_alias_as_name="NOT_USE_ALIAS",
                                    field_mapping=None,
                                    sort_field=None)
                                
                                # Menggabungkan ke dalam list csv untuk di merge
                                CSV_to_merge.append(out_csv_table_pb)
                                print(f"Proses Export to csv Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Export to csv Provinsi: {provinsi} selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                


                                print(f"Memulai Reclassify Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Reclassify Provinsi: {provinsi}", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                out_raster_ash_pb = arcpy.sa.Reclassify(in_raster=Extract_rast_sh,
                                                                reclass_field="VALUE",
                                                                remap="0 30 1;30 50 2;50 84 3;84 115 4;115 150 5;150 200 6;200 10000 7",
                                                                missing_values="DATA")
                                
                                out_raster_ash_pb.save(os.path.join(fgdb_temp, f"Reclass_ASH_{provinsi}_{year_bln}{month_bln}"))
                                print(f"Proses Reclassify Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Reclassify Provinsi: {provinsi} telah selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                



                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai . . . . ")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_bln, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)


                                Output_polygon_features_ash = os.path.join(fgdb_temp, f"ash_bln_{provinsi}_ver_{year_bln}{month_bln}")
                                arcpy.conversion.RasterToPolygon(in_raster=out_raster_ash_pb, out_polygon_features=Output_polygon_features_ash)
                                arcpy.management.AddFields(in_table=Output_polygon_features_ash, field_description= "SH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="SH",
                                            expression="sh(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def sh(x):
                                            if x == 1:
                                                return "0-30"
                                            elif x == 2:
                                                return "31-50"
                                            elif x == 3:
                                                return "51-84"
                                            elif x == 4:
                                                return "85-115"
                                            elif x == 5:
                                                return "116-150"
                                            elif x == 6:
                                                return "151-200"
                                            elif x == 7:
                                                return ">200"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Kategori",
                                            expression="kategori(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def kategori(x):
                                            if x == 1:
                                                return "Bawah Normal"
                                            elif x == 2:
                                                return "Bawah Normal"
                                            elif x == 3:
                                                return "Bawah Normal"
                                            elif x == 4:
                                                return "Normal"
                                            elif x == 5:
                                                return "Atas Normal"
                                            elif x == 6:
                                                return "Atas Normal"
                                            elif x == 7:
                                                return "Atas Normal"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Periode",
                                            expression=f'"{month_name_bln} {year_bln}"',
                                            expression_type="PYTHON3"
                                        )
                                arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ash,
                                        field="Informasi",
                                        expression='"Sifat Hujan"',
                                        expression_type="PYTHON3"
                                    )
                                
                                poly_kec = poly_kecamatan[provinsi]
        

                                Output_polygon_features_ash_union = os.path.join(output_loc_shp, f"ash_bln_{provinsi.lower()}_ver_{year_bln}{month_bln}")
                                arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ach], 
                                         out_feature_class= Output_polygon_features_ash_union)
                                
                                arcpy.management.AddField(
                                            in_table=Output_polygon_features_ash_union,
                                            field_name="Area_H", field_type="DOUBLE")
                    
                                arcpy.management.CalculateGeometryAttributes(
                                        in_features=Output_polygon_features_ash_union,
                                        geometry_property=[["Area_H", "AREA_GEODESIC"]],
                                        area_unit="HECTARES")
                                                                        
                                # Menggabungkan output polygon untuk di merge
                                ASH_to_merge.append(Output_polygon_features_ash)
                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
                                
                                print("\n")

            except Exception as e:
                print(f"Error di pengolahan Pulau/Provinsi {r[0]}: {e}")
                log_to_sde(message= f"Error di pengolahan Pulau/Provinsi {r[0]}: {e}", status = "ERROR", tipe_progress="Bulanan", tipe_informasi="Analisis")
                # Log additional debug information with status set to DEBUG
                log_to_sde(message = "Detailed debug information for error analysis.", status = "DEBUG", tipe_progress="Bulanan", tipe_informasi="Analisis")

                continue  # Skip to the next island

    
    try:
        # Proses se Indonesia 
        #Mosaic CH

        

        print("Proses Merge Raster ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge Raster ACH dan ASH: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

        pembuatan_archiving = ArchivingFolder(output_folder)
        output_loc_tiff = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_bln, tipe='TIFF')


        arcpy.MosaicToNewRaster_management(
            input_rasters=raster_ACH_to_merge_tif,
            output_location=output_loc_tiff,  # Direktori output
            raster_dataset_name_with_extension=f"ach_bln_indo_ver_{year_bln}{month_bln}.tif",
            coordinate_system_for_the_raster=None,  # Sistem koordinat, bisa None untuk menggunakan sistem koordinat raster input
            pixel_type="32_BIT_FLOAT",
            cellsize=None,
            number_of_bands=1,
            mosaic_method="MEAN" ,
            mosaic_colormap_mode="FIRST"  # Mode kolormap, bisa "FIRST", "LAST", "MATCH", dll.
            )

        arcpy.MosaicToNewRaster_management(
            input_rasters=raster_ASH_to_merge_tif,
            output_location=output_loc_tiff,  # Direktori output
            raster_dataset_name_with_extension= f"ash_bln_indo_ver_{year_bln}{month_bln}.tif",
            coordinate_system_for_the_raster=None,  # Sistem koordinat, bisa None untuk menggunakan sistem koordinat raster input
            pixel_type="32_BIT_FLOAT",
            cellsize=None,
            number_of_bands=1,
            mosaic_method="MEAN" ,
            mosaic_colormap_mode="FIRST"  # Mode kolormap, bisa "FIRST", "LAST", "MATCH", dll.
            )
        
        print("Proses Merge Raster ACH dan ASH: Indonesia selesai")
        log_to_sde(message = f"Proses Merge Raster ACH dan ASH: Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")


        print("Proses Merge Polygon ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge Polygon ACH dan ASH: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")

        #Membuat archiving
        pembuatan_archiving = ArchivingFolder(output_folder)
        output_loc_shp = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_bln, tipe='SHP')


        # Merge polygon menjadi se Indonesia
        kec_indo = os.getenv("POLY_KEC")
        arcpy.management.Merge(ACH_to_merge, os.path.join(fgdb_temp, f"ach_bln_indo_ver_{year_bln}{month_bln}"))
        poly_indo_ach = os.path.join(output_loc_shp, f"ach_bln_indo_ver_{year_bln}{month_bln}")
        arcpy.analysis.Union(in_features=[kec_indo, os.path.join(fgdb_temp, f"ach_bln_indo_ver_{year_bln}{month_bln}")], 
                                         out_feature_class=poly_indo_ach)
        
        arcpy.management.AddField(
                                in_table=poly_indo_ach,
                                field_name="Area_H", field_type="DOUBLE")
                    
        arcpy.management.CalculateGeometryAttributes(
                in_features=poly_indo_ach,
                geometry_property=[["Area_H", "AREA_GEODESIC"]],
                area_unit="HECTARES")
        
        folder_layout = os.getenv("FOLDER_LAYOUT")
        
        arcpy.CopyFeatures_management(poly_indo_ach, os.path.join(folder_layout, 'polygon_ach_bln'))
        

        arcpy.management.Merge(ASH_to_merge, os.path.join(fgdb_temp, f"ash_bln_indo_ver_{year_bln}{month_bln}"))
        poly_indo_ash = os.path.join(output_loc_shp, f"ash_bln_indo_ver_{year_bln}{month_bln}")
        arcpy.analysis.Union(in_features=[kec_indo, os.path.join(fgdb_temp, f"ash_bln_indo_ver_{year_bln}{month_bln}")], 
                                         out_feature_class= poly_indo_ash)
        arcpy.management.AddField(
                                in_table=poly_indo_ash,
                                field_name="Area_H", field_type="DOUBLE")
                    
        arcpy.management.CalculateGeometryAttributes(
                in_features=poly_indo_ash,
                geometry_property=[["Area_H", "AREA_GEODESIC"]],
                area_unit="HECTARES")
        
        folder_layout = os.getenv("FOLDER_LAYOUT")
        
        arcpy.CopyFeatures_management(poly_indo_ash, os.path.join(folder_layout, 'polygon_ash_bln'))

        

        print("Proses Merge Polygon ACH dan ASH: Indonesia selesai")

        ### Updating polygon CH di dashboard
        log_to_sde(message = f"Proses Update Polygon ACH Dasboard: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        update_polygon_bln(sde_polygon=poly_ach_bln, process_polygon=poly_indo_ach)

        log_to_sde(message = f"Proses Update Polygon ACH Dasboard: Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        
        ### Updating polygon SH di dashboard
        
        log_to_sde(message = f"Proses Update Polygon ASH Dasboard: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        update_polygon_bln(sde_polygon=poly_ash_bln, process_polygon=poly_indo_ash)
        
        log_to_sde(message = f"Proses Update Polygon ASH Dasboard: Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        
        print("\n")


        print("Proses Merge CSV ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge CSV ACH dan ASH: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        #Mmebuiat archive
        output_loc_csv = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_bln, tipe='CSV')

        # Merge csv se Indonesia
        combined_df = pd.DataFrame()
        for file in CSV_to_merge:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file, delimiter=';')
            # Append the DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        combined_df.to_csv(os.path.join(output_loc_csv, f"bln_indo_ver_{year_bln}{month_bln}.csv"), index=False)
        print("Proses Merge CSV ACH dan ASH: Indonesia selesai")
        log_to_sde(message = f"Proses Merge CSV ACH dan ASH: Indonesia selesai", status="INFO", 
                                        tipe_progress="Bulanan", tipe_informasi="Analisis")
        print("\n")


        return poly_indo_ach, poly_indo_ash, raster_ACH_to_merge, raster_ASH_to_merge

    except Exception as e:
        print(f"Error Pengolahan Data Indonesia: {e}")
        log_to_sde(message= f"Error Pengolahan Data Indonesia: {e}", status = "ERROR", tipe_progress="Dasarian", tipe_informasi="Analisis")
        # Log additional debug information with status set to DEBUG
        log_to_sde(message = "Detailed debug information for error analysis.", status = "DEBUG", tipe_progress="Dasarian", tipe_informasi="Analisis")

    
    print("PROSES ANALISIS BULANAN SELESAI")

    




def interpolasi_das(input_data):

    print("PROSES ANALISIS DASARIAN DIMULAI . . .")
    
    raster_ACH_to_merge = []
    raster_ASH_to_merge = []
    raster_ACH_to_merge_tif = []
    raster_ASH_to_merge_tif = []
    ACH_to_merge = []
    ASH_to_merge = []
    CSV_to_merge = []

    poly_indo_ach = None
    poly_indo_ash = None


    with arcpy.da.SearchCursor(pulau_reference, [["Pulau_Singkat", ["Is_Besar"]]]) as cursors:  # Membaca feature service untuk mmeisahkan proses looping pulau besar dan pulau kecil berdasarkan atribut
        for r in cursors:
            try:
                if r[1] == "False":  # val False = Pulau Kecil dan va True = Pulau Besar
                    pulau_kecil = r[0]
                    print(f"Memulai Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ACH Pulau Kecil: {pulau_kecil}", status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                    ####### Proses untuk kategori pulau kecil\
                    ####### Proses ACH untuk kategori pulau kecil
                    # Create new folder
                    
                    pembuatan_archiving = ArchivingFolder(output_folder)
                    output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='TIFF', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)

                    # Start Process

                    with arcpy.EnvManager(extent=extent_pulau[pulau_kecil], mask=pulau_feature[pulau_kecil]):
                        arcpy.ga.IDW(
                            in_features= input_data,
                            z_field="CH",
                            out_ga_layer=None,
                            out_raster=os.path.join(output_loc_tiff, f"ach_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif"),
                            cell_size=gridsize_pkecil,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )
                    raster_ach_pk = arcpy.Raster(os.path.join(output_loc_tiff, f"ach_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif"))
                    raster_ach_pk_copy = os.path.join(raster_loc, f"ach_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")

                    copy_raster(raster_ach_pk, raster_ach_pk_copy)

                    row_list_ch = (raster_ach_pk_copy, f'{pulau_kecil}')

                    raster_ACH_to_merge.append(row_list_ch)


                    raster_ACH_to_merge_tif.append(raster_ach_pk)

                    

                    

                    print(f"Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ACH Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")



                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai ...")

                    pembuatan_archiving = ArchivingFolder(output_folder)
                    output_loc_csv = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='CSV', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)
                    

                    titik_grid_extract_pk = os.path.join(fgdb_temp, f"Titik_extract_{pulau_kecil}_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.management.CopyFeatures(in_features=titik_grid[pulau_kecil], out_feature_class=titik_grid_extract_pk)
                    point_extracted_pk = arcpy.sa.ExtractMultiValuesToPoints(titik_grid_extract_pk, [[raster_ach_pk, "CH"]], "NONE")
                    # point_extracted_ch.save()
                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Extract Point Pulau Kecil: {pulau_kecil} selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                    

                    print(f"Proses Reclassify ACH Pulau Kecil: {pulau_kecil} dimulai . . . .")
                    log_to_sde(message = f"Proses Reclassify ACH Pulau Kecil: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                    out_raster_ach_pk = arcpy.sa.Reclassify(
                        in_raster=raster_ach_pk,
                        reclass_field="VALUE",
                        remap="0 10 1;10 20 2;20 50 3;50 75 4;75 100 5;100 150 6;150 200 7;200 300 8;300 10000 9",
                        missing_values="DATA")
                    
                    out_raster_ach_pk.save(os.path.join(fgdb_temp, f"Reclass_ACH_{pulau_kecil}_{year_das}{month_das}das0{current_dasarian}"))
                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")



                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai . . . .")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    # Pembuatan archive
                    output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=pulau_kecil)
                    Output_polygon_features_ach = os.path.join(fgdb_temp, f"ach_das_{pulau_kecil}_ver_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.conversion.RasterToPolygon(in_raster=out_raster_ach_pk, out_polygon_features=Output_polygon_features_ach)
                    arcpy.management.AddFields(in_table=Output_polygon_features_ach, field_description= "CH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                    arcpy.management.CalculateField(
                                in_table=Output_polygon_features_ach,
                                field="CH",
                                expression="ch(!gridcode!)",
                                expression_type="PYTHON3",
                                code_block="""def ch(x):
                                if x == 1:
                                    return "0-10"
                                elif x == 2:
                                    return "11-20"
                                elif x == 3:
                                    return "21-50"
                                elif x == 4:
                                    return "51-75"
                                elif x == 5:
                                    return "76-100"
                                elif x == 6:
                                    return "101-150"
                                elif x == 7:
                                    return "151-200"
                                elif x == 8:
                                    return "201-300"
                                elif x ==9 :
                                    return ">300"
                                """,
                                field_type="TEXT",
                                enforce_domains="NO_ENFORCE_DOMAINS")
                    arcpy.management.CalculateField(
                                in_table=Output_polygon_features_ach,
                                field="Kategori",
                                expression="cat(!gridcode!)",
                                expression_type="PYTHON3",
                                code_block="""def cat(x):
                                if x == 1:
                                    return "Rendah"
                                elif x == 2:
                                    return "Rendah"
                                elif x == 3:
                                    return "Rendah"
                                elif x == 4:
                                    return "Menengah"
                                elif x == 5:
                                    return "Menengah"
                                elif x == 6:
                                    return "Menengah"
                                elif x == 7:
                                    return "Tinggi"
                                elif x == 8:
                                    return "Sangat Tinggi"
                                elif x ==9 :
                                    return "Sangat Tinggi"
                                """,
                                field_type="TEXT",
                                enforce_domains="NO_ENFORCE_DOMAINS")
                    
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Periode",
                                            expression=f'"Dasarian {current_dasarian} {month_name_das} {year_das}"',
                                            expression_type="PYTHON3"
                                        )
                    arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ach,
                                        field="Informasi",
                                        expression='"Curah Hujan"',
                                        expression_type="PYTHON3"
                                    )
                    
                    poly_kec = poly_kecamatan[pulau_kecil]

                    Output_polygon_features_ach_union = os.path.join(output_loc_shp, f"ach_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ach], 
                                         out_feature_class=Output_polygon_features_ach_union)
                    

                    arcpy.management.AddField(
                                in_table=Output_polygon_features_ach_union,
                                field_name="Area_H", field_type="DOUBLE")
                    
                    arcpy.management.CalculateGeometryAttributes(
                            in_features=Output_polygon_features_ach_union,
                            geometry_property=[["Area_H", "AREA_GEODESIC"]],
                            area_unit="HECTARES")
                    


                    # Menggabungkan polygon untuk di merge
                    ACH_to_merge.append(Output_polygon_features_ach)
                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    print("\n")



                    ####### Proses ASH untuk kategori pulau kecil
                    print(f"Memulai Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ASH Pulau Kecil: {pulau_kecil}", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    with arcpy.EnvManager(extent=extent_pulau[pulau_kecil], mask=pulau_feature[pulau_kecil]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="SH_",
                            out_ga_layer=None,
                            out_raster=os.path.join(output_loc_tiff, f"ash_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif"),
                            cell_size=gridsize_pkecil,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )

                    raster_ash_pk = arcpy.Raster(os.path.join(output_loc_tiff, f"ash_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif"))

                    raster_ash_pk_copy = os.path.join(raster_loc, f"ash_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")

                    copy_raster(raster_ash_pk, raster_ash_pk_copy)

                    row_list_sh = (raster_ash_pk_copy, f'{pulau_kecil}')
                    
                    raster_ASH_to_merge.append(row_list_sh)

                    raster_ASH_to_merge_tif.append(raster_ash_pk)


                    print(f"Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ASH Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                    # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {pulau_kecil} dimulai . . .. ")
                    # arcpy.management.AddRastersToMosaicDataset(
                    #                 in_mosaic_dataset= mosaic_bln_sh,
                    #                 raster_type="Raster Dataset",
                    #                 input_path= raster_ash_pk,
                    #                 update_cellsize_ranges="UPDATE_CELL_SIZES",
                    #                 update_boundary="UPDATE_BOUNDARY",
                    #                 update_overviews="NO_OVERVIEWS",
                    #                 maximum_pyramid_levels=None,
                    #                 maximum_cell_size=0,
                    #                 minimum_dimension=1500,
                    #                 spatial_reference=None,
                    #                 filter="",
                    #                 sub_folder="SUBFOLDERS",
                    #                 duplicate_items_action="ALLOW_DUPLICATES",
                    #                 build_pyramids="BUILD_PYRAMIDS",
                    #                 calculate_statistics="CALCULATE_STATISTICS",
                    #                 build_thumbnails="NO_THUMBNAILS",
                    #                 operation_description="",
                    #                 force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
                    #                 estimate_statistics="ESTIMATE_STATISTICS",
                    #                 aux_inputs=None,
                    #                 enable_pixel_cache="NO_PIXEL_CACHE",
                    #                 cache_location=r"C:\Users\mjanuadi\AppData\Local\ESRI\rasterproxies\Mosaic_Dataset_SH")
                    # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {pulau_kecil} selesai ")


                    
                    print(f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai . . .")
                    log_to_sde(message = f"Proses Extract Point Pulau Kecil: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    point_extracted_pk = os.path.join(fgdb_temp, f"Titik_extract_{pulau_kecil}_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.sa.ExtractMultiValuesToPoints(point_extracted_pk, [[raster_ash_pk, "SH"]], "NONE")
                    # point_extracted_sh.save()
                    arcpy.management.AddFields(in_table=point_extracted_pk, field_description=[["LAT", "DOUBLE", "Latitude", "", "", ""], ["LONG", "DOUBLE", "Longitude", "", "", ""]])[0]
                    arcpy.management.CalculateGeometryAttributes(in_features=point_extracted_pk, geometry_property=[["LAT", "POINT_Y"], ["LONG", "POINT_X"]], coordinate_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", 
                                                                            coordinate_format="DD")[0]
                    print(f"Proses Extract Point Provinsi: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Extract Point Provinsi: {pulau_kecil} selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    



                    print(f"Proses Export to csv Provinsi: {pulau_kecil} dimulai . . .")
                    log_to_sde(message = f"Proses Export to csv Provinsi: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    out_csv_table_pk = os.path.join(output_loc_csv, f"das_{pulau_kecil.lower()}_ver_{year_das}0{month_das}das0{current_dasarian}.csv")
                    arcpy.conversion.ExportTable(
                                    in_table= point_extracted_pk,
                                    out_table= out_csv_table_pk,
                                    where_clause="",
                                    use_field_alias_as_name="NOT_USE_ALIAS",
                                    field_mapping=None,
                                    sort_field=None)
                    
                    # Menggabungkan csv untuk di merge
                    CSV_to_merge.append(out_csv_table_pk)
                    print(f"Proses Export to csv Provinsi: {pulau_kecil} selesai")
                    log_to_sde(message = f"Proses Export to csv Provinsi: {pulau_kecil} selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} dimulai . . . .")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    out_raster_ash_pk = arcpy.sa.Reclassify(
                        in_raster=raster_ash_pk,
                        reclass_field="VALUE",
                        remap="0 30 1;30 50 2;50 84 3;84 115 4;115 150 5;150 200 6;200 10000 7",
                        missing_values="DATA")
                    
                    out_raster_ash_pk.save(os.path.join(fgdb_temp, f"Reclass_ACH_{pulau_kecil}_{year_das}{month_das}das0{current_dasarian}"))
                    print(f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Reclassify Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                



                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai . . . . ")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    Output_polygon_features_ash = os.path.join(fgdb_temp, f"ash_das_{pulau_kecil}_ver_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.conversion.RasterToPolygon(in_raster=out_raster_ash_pk, out_polygon_features=Output_polygon_features_ash)
                    arcpy.management.AddFields(in_table=Output_polygon_features_ash, field_description= "SH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="SH",
                                            expression="sh(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def sh(x):
                                            if x == 1:
                                                return "0-30"
                                            elif x == 2:
                                                return "31-50"
                                            elif x == 3:
                                                return "51-84"
                                            elif x == 4:
                                                return "85-115"
                                            elif x == 5:
                                                return "116-150"
                                            elif x == 6:
                                                return "151-200"
                                            elif x == 7:
                                                return ">200"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Kategori",
                                            expression="kategori(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def kategori(x):
                                            if x == 1:
                                                return "Bawah Normal"
                                            elif x == 2:
                                                return "Bawah Normal"
                                            elif x == 3:
                                                return "Bawah Normal"
                                            elif x == 4:
                                                return "Normal"
                                            elif x == 5:
                                                return "Atas Normal"
                                            elif x == 6:
                                                return "Atas Normal"
                                            elif x == 7:
                                                return "Atas Normal"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                    
                    arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Periode",
                                            expression=f'"Dasarian {current_dasarian} {month_name_das} {year_das}"',
                                            expression_type="PYTHON3"
                                        )
                    arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ash,
                                        field="Informasi",
                                        expression='"Sifat Hujan"',
                                        expression_type="PYTHON3"
                                    )
                    

                    poly_kec = poly_kecamatan[pulau_kecil]

                    Output_polygon_features_ash_union = os.path.join(output_loc_shp, f"ash_das_{pulau_kecil.lower()}_ver_{year_das}{month_das}das0{current_dasarian}")
                    arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ash], 
                                         out_feature_class=Output_polygon_features_ash_union)
                    
                    arcpy.management.AddField(
                                in_table=Output_polygon_features_ash_union,
                                field_name="Area_H", field_type="DOUBLE")
                    
                    arcpy.management.CalculateGeometryAttributes(
                            in_features=Output_polygon_features_ash_union,
                            geometry_property=[["Area_H", "AREA_GEODESIC"]],
                            area_unit="HECTARES")
                    
                    
                    
                    # menggabungkan polygon untuk di merge
                    ASH_to_merge.append(Output_polygon_features_ash)
                    print(f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai")
                    log_to_sde(message = f"Proses Konversi Raster to Polygon Pulau Kecil: {pulau_kecil} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    print("\n")


                ####### Proses untuk kategori pulau besar
                ####### Proses ACH Pulau Besar
                else:
                    pulau_besar = r[0]
                    print(f"Memulai Proses Interpolasi ACH Pulau Besar: {pulau_besar} . . .")
                    log_to_sde(message = f"Memulai Proses Interpolasi ACH Pulau Besar: {pulau_besar}", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    with arcpy.EnvManager(extent=extent_pulau[pulau_besar], mask=pulau_feature[pulau_besar]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="CH",
                            out_ga_layer=None,
                            out_raster=os.path.join(fgdb_temp, f"interpolasi_ACH_Pulau_{pulau_besar}_{year_das}{month_das}das0{current_dasarian}"),
                            cell_size=gridsize_pbesar,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )
                    raster_ach_pb = arcpy.Raster(os.path.join(fgdb_temp, f"interpolasi_ACH_Pulau_{pulau_besar}_{year_das}{month_das}das0{current_dasarian}"))


                    #raster_ACH_to_merge.append(raster_ach_pb)


                    print(f"Proses Interpolasi ACH Pulau Besar: {pulau_besar} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ACH Pulau Besar: {pulau_besar} telah selesai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                    
                    print("\n")

                    ######### Proses Masking ACH
                    print(f"Proses Masking ACH Pulau Besar: {pulau_besar} dimulai . . .")
                    log_to_sde(message = f"Proses Masking ACH Pulau Besar: {pulau_besar} dimulai", 
                               status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                    with arcpy.da.SearchCursor(pulau_besar_merge, [["Pulau", ["Provinsi_Singkat"]]]) as masks:
                        for r in masks:
                            pulau_mask = r[0]
                            provinsi = r[1]
                            if pulau_mask == pulau_besar:
                                print(f"Memulai Mask Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Mask Provinsi: {provinsi}", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                                # Membuat archive folder
                                print("Membuat Archive")
                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='TIFF', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                print("Selesai Archive")


                                Extract_rast_ch = os.path.join(output_loc_tiff, f"ach_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")
                                Extract_by_Mask = Extract_rast_ch
                                Extract_rast_ch = arcpy.sa.ExtractByMask(raster_ach_pb, pulau_feature[provinsi], "INSIDE", extent_pulau[provinsi])
                                Extract_rast_ch.save(Extract_by_Mask)

                                Extract_rast_ch_copy = os.path.join(raster_loc, f"ach_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")

                                copy_raster(Extract_rast_ch, Extract_rast_ch_copy)

                                row_list_ch = (Extract_rast_ch_copy, f'{provinsi}')

                                raster_ACH_to_merge.append(row_list_ch)

                                raster_ACH_to_merge_tif.append(Extract_rast_ch)

                                


                                print(f"Proses Mask Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Mask Provinsi: {provinsi} selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                                
                                # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {provinsi} dimulai . . .. ")
                                # arcpy.management.AddRastersToMosaicDataset(
                                #     in_mosaic_dataset= mosaic_bln_ch,
                                #     raster_type="Raster Dataset",
                                #     input_path= Extract_rast_ch,
                                #     update_cellsize_ranges="UPDATE_CELL_SIZES",
                                #     update_boundary="UPDATE_BOUNDARY",
                                #     update_overviews="NO_OVERVIEWS",
                                #     maximum_pyramid_levels=None,
                                #     maximum_cell_size=0,
                                #     minimum_dimension=1500,
                                #     spatial_reference=None,
                                #     filter="",
                                #     sub_folder="SUBFOLDERS",
                                #     duplicate_items_action="ALLOW_DUPLICATES",
                                #     build_pyramids="BUILD_PYRAMIDS",
                                #     calculate_statistics="CALCULATE_STATISTICS",
                                #     build_thumbnails="NO_THUMBNAILS",
                                #     operation_description="",
                                #     force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
                                #     estimate_statistics="ESTIMATE_STATISTICS",
                                #     aux_inputs=None,
                                #     enable_pixel_cache="NO_PIXEL_CACHE",
                                #     cache_location=r"C:\Users\mjanuadi\AppData\Local\ESRI\rasterproxies\Mosaic_Dataset_CH")
                                # print(f"Proses Memasukan Ke Mosaic Dataset Provinsi: {provinsi} selesai ")


                                print(f"Proses Extract Point Provinsi: {provinsi} dimulai ...")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                titik_grid_extract_pb = os.path.join(fgdb_temp, f"Titik_extract_{provinsi}_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.management.CopyFeatures(in_features=titik_grid[provinsi], out_feature_class=titik_grid_extract_pb)
                                point_extracted_pb = arcpy.sa.ExtractMultiValuesToPoints(titik_grid_extract_pb, [[Extract_rast_ch, "CH"]], "NONE")
                                # point_extracted_ch.save()
                                print(f"Proses Extract Point Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")




                                print(f"Memulai Reclassify Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Reclassify Provinsi: {provinsi}", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                out_raster_ach_pb = arcpy.sa.Reclassify(in_raster=Extract_rast_ch,
                                                                reclass_field="VALUE",
                                                                remap="0 10 1;10 20 2;20 50 3;50 75 4;75 100 5;100 150 6;150 200 7;200 300 8;300 10000 9",
                                                                missing_values="DATA")
                                
                                out_raster_ach_pb.save(os.path.join(fgdb_temp, f"Reclass_ACH_{provinsi}_{year_das}{month_das}das0{current_dasarian}"))
                                print(f"Proses Reclassify Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Reclassify Provinsi: {provinsi} telah selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                            

                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai . . . . ")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                # Membuat archive folder
                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                Output_polygon_features_ach = os.path.join(fgdb_temp, f"ach_das_{provinsi}_ver_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.conversion.RasterToPolygon(in_raster=out_raster_ach_pb, out_polygon_features=Output_polygon_features_ach)
                                arcpy.management.AddFields(in_table=Output_polygon_features_ach, field_description= "CH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="CH",
                                            expression="ch(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def ch(x):
                                            if x == 1:
                                                return "0-10"
                                            elif x == 2:
                                                return "11-20"
                                            elif x == 3:
                                                return "21-50"
                                            elif x == 4:
                                                return "51-75"
                                            elif x == 5:
                                                return "76-100"
                                            elif x == 6:
                                                return "101-150"
                                            elif x == 7:
                                                return "151-200"
                                            elif x == 8:
                                                return "201-300"
                                            elif x ==9 :
                                                return ">300"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Kategori",
                                            expression="cat(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def cat(x):
                                            if x == 1:
                                                return "Rendah"
                                            elif x == 2:
                                                return "Rendah"
                                            elif x == 3:
                                                return "Rendah"
                                            elif x == 4:
                                                return "Menengah"
                                            elif x == 5:
                                                return "Menengah"
                                            elif x == 6:
                                                return "Menengah"
                                            elif x == 7:
                                                return "Tinggi"
                                            elif x == 8:
                                                return "Sangat Tinggi"
                                            elif x ==9 :
                                                return "Sangat Tinggi"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ach,
                                            field="Periode",
                                            expression=f'"Dasarian {current_dasarian} {month_name_das} {year_das}"',
                                            expression_type="PYTHON3"
                                        )
                                arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ach,
                                        field="Informasi",
                                        expression='"Curah Hujan"',
                                        expression_type="PYTHON3"
                                    )
                                
                                poly_kec = poly_kecamatan[provinsi]
                                
                                Output_polygon_features_ach_union = os.path.join(output_loc_shp, f"ach_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ach], 
                                         out_feature_class= Output_polygon_features_ach_union)
                                
                                
                                arcpy.management.AddField(
                                            in_table=Output_polygon_features_ach_union,
                                            field_name="Area_H", field_type="DOUBLE")
                    
                                arcpy.management.CalculateGeometryAttributes(
                                        in_features=Output_polygon_features_ach_union,
                                        geometry_property=[["Area_H", "AREA_GEODESIC"]],
                                        area_unit="HECTARES")

                                
                                
                                # Menggabungkan polygon untuk di merge
                                ACH_to_merge.append(Output_polygon_features_ach)
                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                print("\n")

                            

                    ####### Proses ASH Pulau Besar
                    ####### Proses Interpolasi ASH
                    print(f"Memulai Proses Interpolasi ASH Pulau Besar: {pulau_besar}")
                    log_to_sde(message = f"Memulai Proses Interpolasi ASH Pulau Besar: {pulau_besar}", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                    with arcpy.EnvManager(extent=extent_pulau[pulau_besar], mask=pulau_feature[pulau_besar]):
                        arcpy.ga.IDW(
                            in_features=input_data,
                            z_field="SH_",
                            out_ga_layer=None,
                            out_raster=os.path.join(fgdb_temp, f"interpolasi_ASH_Pulau_{pulau_besar}_{year_das}{month_das}das0{current_dasarian}"),
                            cell_size=gridsize_pbesar,
                            power=2,
                            search_neighborhood="NBRTYPE=Standard S_MAJOR=12,2269298067831 S_MINOR=12,2269298067831 ANGLE=0 NBR_MAX=15 NBR_MIN=10 SECTOR_TYPE=ONE_SECTOR",
                            weight_field=None
                        )

                    raster_ash = arcpy.Raster(os.path.join(fgdb_temp, f"interpolasi_ASH_Pulau_{pulau_besar}_{year_das}{month_das}das0{current_dasarian}"))

                    #raster_ASH_to_merge.append(raster_ash)

                    print(f"Proses Interpolasi ASH Pulau Besar: {pulau_besar} telah selesai")
                    log_to_sde(message = f"Proses Interpolasi ASH Pulau Besar: {pulau_besar} telah selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                    print("\n")

                    ######### Proses Masking ASH
                    print(f"Proses Masking ASH Pulau Besar: {pulau_besar} dimulai . . .")
                    log_to_sde(message = f"Proses Masking ASH Pulau Besar: {pulau_besar} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")




                    with arcpy.da.SearchCursor(pulau_besar_merge, [["Pulau", ["Provinsi_Singkat"]]]) as masks:
                        for r in masks:
                            pulau_mask = r[0]
                            provinsi = r[1]
                            if pulau_mask == pulau_besar:
                                print(f"Memulai Mask ASH Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Mask ASH Provinsi: {provinsi}", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_tiff = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                            output_tipe_periode=output_tipe_das, tipe='TIFF', 
                                                            nama_prov=nama_prov_folder, pulau_kecil=provinsi)



                                Extract_rast_sh = os.path.join(output_loc_tiff, f"ash_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")
                                Extract_by_Mask = Extract_rast_sh
                                Extract_rast_sh = arcpy.sa.ExtractByMask(raster_ash, pulau_feature[provinsi], "INSIDE", extent_pulau[provinsi])
                                Extract_rast_sh.save(Extract_by_Mask)


                                Extract_rast_sh_copy = os.path.join(raster_loc, f"ash_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.tif")

                                copy_raster(Extract_rast_sh, Extract_rast_sh_copy)

                                row_list_sh = (Extract_rast_sh_copy, f'{provinsi}')

                                raster_ASH_to_merge.append(row_list_sh)

                                raster_ASH_to_merge_tif.append(Extract_rast_sh)



                                print(f"Proses Mask Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Mask Provinsi: {provinsi} selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


                                print(f"Proses Extract Point Provinsi: {provinsi} dimulai . . .")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                point_extracted_pb = os.path.join(fgdb_temp, f"Titik_extract_{provinsi}_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.sa.ExtractMultiValuesToPoints(point_extracted_pb, [[Extract_rast_sh, "SH"]], "NONE")
                                arcpy.management.AddFields(in_table=point_extracted_pb, field_description=[["LAT", "DOUBLE", "Latitude", "", "", ""], ["LONG", "DOUBLE", "Longitude", "", "", ""]])[0]
                                arcpy.management.CalculateGeometryAttributes(in_features=point_extracted_pb, geometry_property=[["LAT", "POINT_Y"], ["LONG", "POINT_X"]],coordinate_system="PROJCS[\"WGS_1984_Web_Mercator_Auxiliary_Sphere\",GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Mercator_Auxiliary_Sphere\"],PARAMETER[\"False_Easting\",0.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",0.0],PARAMETER[\"Standard_Parallel_1\",0.0],PARAMETER[\"Auxiliary_Sphere_Type\",0.0],UNIT[\"Meter\",1.0]]", 
                                                                            coordinate_format="DD")[0]
                                # point_extracted_sh.save()
                                print(f"Proses Extract Point Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Extract Point Provinsi: {provinsi} selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")




                                print(f"Proses Export to csv Provinsi: {provinsi} dimulai . . .")
                                log_to_sde(message = f"Proses Export to csv Provinsi: {provinsi} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_csv = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='CSV', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)

                                out_csv_table_pb = os.path.join(output_loc_csv, f"das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}.csv")
                                arcpy.conversion.ExportTable(
                                    in_table= point_extracted_pb,
                                    out_table= out_csv_table_pb,
                                    where_clause="",
                                    use_field_alias_as_name="NOT_USE_ALIAS",
                                    field_mapping=None,
                                    sort_field=None)
                                
                                # Menggabungkan ke dalam list csv untuk di merge
                                CSV_to_merge.append(out_csv_table_pb)
                                print(f"Proses Export to csv Provinsi: {provinsi} selesai")
                                log_to_sde(message = f"Proses Export to csv Provinsi: {provinsi} selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                


                                print(f"Memulai Reclassify Provinsi: {provinsi}  . . .")
                                log_to_sde(message = f"Memulai Reclassify Provinsi: {provinsi}", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                out_raster_ash_pb = arcpy.sa.Reclassify(in_raster=Extract_rast_sh,
                                                                reclass_field="VALUE",
                                                                remap="0 30 1;30 50 2;50 84 3;84 115 4;115 150 5;150 200 6;200 10000 7",
                                                                missing_values="DATA")
                                
                                out_raster_ash_pb.save(os.path.join(fgdb_temp, f"Reclass_ASH_{provinsi}_{year_das}{month_das}das0{current_dasarian}"))
                                print(f"Proses Reclassify Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Reclassify Provinsi: {provinsi} telah selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                



                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai . . . .")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

                                pembuatan_archiving = ArchivingFolder(output_folder)
                                output_loc_shp = pembuatan_archiving.archive_prov(output_level_prov=output_level_prov, 
                                                                       output_tipe_periode=output_tipe_das, tipe='SHP', 
                                                                       nama_prov=nama_prov_folder, pulau_kecil=provinsi)


                                Output_polygon_features_ash = os.path.join(fgdb_temp, f"ash_das_{provinsi}_ver_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.conversion.RasterToPolygon(in_raster=out_raster_ash_pb, out_polygon_features=Output_polygon_features_ash)
                                arcpy.management.AddFields(in_table=Output_polygon_features_ash, field_description= "SH TEXT # 255 # #;Kategori TEXT # 255 # #;Periode TEXT # 255 # #;Informasi TEXT # 255 # #")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="SH",
                                            expression="sh(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def sh(x):
                                            if x == 1:
                                                return "0-30"
                                            elif x == 2:
                                                return "31-50"
                                            elif x == 3:
                                                return "51-84"
                                            elif x == 4:
                                                return "85-115"
                                            elif x == 5:
                                                return "116-150"
                                            elif x == 6:
                                                return "151-200"
                                            elif x == 7:
                                                return ">200"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Kategori",
                                            expression="kategori(!gridcode!)",
                                            expression_type="PYTHON3",
                                            code_block="""def kategori(x):
                                            if x == 1:
                                                return "Bawah Normal"
                                            elif x == 2:
                                                return "Bawah Normal"
                                            elif x == 3:
                                                return "Bawah Normal"
                                            elif x == 4:
                                                return "Normal"
                                            elif x == 5:
                                                return "Atas Normal"
                                            elif x == 6:
                                                return "Atas Normal"
                                            elif x == 7:
                                                return "Atas Normal"
                                            """,
                                            field_type="TEXT",
                                            enforce_domains="NO_ENFORCE_DOMAINS")
                                

                                arcpy.management.CalculateField(
                                            in_table=Output_polygon_features_ash,
                                            field="Periode",
                                            expression=f'"Dasarian {current_dasarian} {month_name_das} {year_das}"',
                                            expression_type="PYTHON3"
                                        )
                                arcpy.management.CalculateField(
                                        in_table=Output_polygon_features_ash,
                                        field="Informasi",
                                        expression='"Sifat Hujan"',
                                        expression_type="PYTHON3"
                                    )
                                

                                poly_kec = poly_kecamatan[provinsi]

                                
                                Output_polygon_features_ash_union = os.path.join(output_loc_shp, f"ash_das_{provinsi.lower()}_ver_{year_das}{month_das}das0{current_dasarian}")
                                arcpy.analysis.Union(in_features=[poly_kec, Output_polygon_features_ash], 
                                         out_feature_class= Output_polygon_features_ash_union)
                                
                                
                                arcpy.management.AddField(
                                            in_table=Output_polygon_features_ash_union,
                                            field_name="Area_H", field_type="DOUBLE")
                    
                                arcpy.management.CalculateGeometryAttributes(
                                        in_features=Output_polygon_features_ash_union,
                                        geometry_property=[["Area_H", "AREA_GEODESIC"]],
                                        area_unit="HECTARES")
                                
                                
                                
                                # Menggabungkan output polygon untuk di merge
                                ASH_to_merge.append(Output_polygon_features_ash)
                                print(f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai")
                                log_to_sde(message = f"Proses Konversi Raster to Polygon Provinsi: {provinsi} telah selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
                                
                                print("\n")

            except Exception as e:
                print(f"Error di pengolahan Pulau/Provinsi {r[0]}: {e}")
                log_to_sde(message= f"Error di pengolahan Pulau/Provinsi {r[0]}: {e}", status = "ERROR", tipe_progress="Dasarian", tipe_informasi="Analisis")
                # Log additional debug information with status set to DEBUG
                log_to_sde(message = "Detailed debug information for error analysis.", status = "DEBUG", tipe_progress="Dasarian", tipe_informasi="Analisis")

                continue  # Skip to the next island

    
    try:
        # Proses se Indonesia

        
        # print("\n")

        print("Proses Merge Raster ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge Raster ACH dan ASH: Indonesia dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

        pembuatan_archiving = ArchivingFolder(output_folder)
        output_loc_tiff = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_das, tipe='TIFF')


        arcpy.MosaicToNewRaster_management(
            input_rasters=raster_ACH_to_merge_tif,
            output_location=output_loc_tiff,  # Direktori output
            raster_dataset_name_with_extension=f"ach_das_indo_ver_{year_das}{month_das}das0{current_dasarian}.tif",
            coordinate_system_for_the_raster=None,  # Sistem koordinat, bisa None untuk menggunakan sistem koordinat raster input
            pixel_type="32_BIT_FLOAT",
            cellsize=None,
            number_of_bands=1,
            mosaic_method="MEAN" ,
            mosaic_colormap_mode="FIRST"  # Mode kolormap, bisa "FIRST", "LAST", "MATCH", dll.
            )

        arcpy.MosaicToNewRaster_management(
            input_rasters=raster_ASH_to_merge_tif,
            output_location=output_loc_tiff,  # Direktori output
            raster_dataset_name_with_extension= f"ash_das_indo_ver_{year_das}{month_das}das0{current_dasarian}.tif",
            coordinate_system_for_the_raster=None,  # Sistem koordinat, bisa None untuk menggunakan sistem koordinat raster input
            pixel_type="32_BIT_FLOAT",
            cellsize=None,
            number_of_bands=1,
            mosaic_method="MEAN" ,
            mosaic_colormap_mode="FIRST"  # Mode kolormap, bisa "FIRST", "LAST", "MATCH", dll.
            )
        
        print("Proses Merge Raster ACH dan ASH: Indonesia selesai")
        log_to_sde(message = f"Proses Merge Raster ACH dan ASH: Indonesia selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")


        print("Proses Merge Polygon ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge Polygon ACH dan ASH: Indonesia dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")

        #Membuat archiving
        pembuatan_archiving = ArchivingFolder(output_folder)
        output_loc_shp = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_das, tipe='SHP')


        # Merge polygon menjadi se Indonesia
        kec_indo = os.getenv("POLY_KEC")
        arcpy.management.Merge(ACH_to_merge, os.path.join(fgdb_temp, f"ach_das_indo_ver_{year_das}{month_das}das0{current_dasarian}"))
        poly_indo_ach = os.path.join(output_loc_shp, f"ach_das_indo_ver_{year_das}{month_das}das0{current_dasarian}")
        arcpy.analysis.Union(in_features=[kec_indo, os.path.join(fgdb_temp, f"ach_das_indo_ver_{year_das}{month_das}das0{current_dasarian}")], 
                                         out_feature_class=poly_indo_ach)
        arcpy.management.AddField(
                                in_table=poly_indo_ach,
                                field_name="Area_H", field_type="DOUBLE")
                    
        arcpy.management.CalculateGeometryAttributes(
                in_features=poly_indo_ach,
                geometry_property=[["Area_H", "AREA_GEODESIC"]],
                area_unit="HECTARES")
        
        folder_layout = os.getenv("FOLDER_LAYOUT")
        
        arcpy.CopyFeatures_management(poly_indo_ach, os.path.join(folder_layout, 'polygon_ach_das'))
        
        

        arcpy.management.Merge(ASH_to_merge, os.path.join(fgdb_temp, f"ash_das_indo_ver_{year_das}{month_das}das0{current_dasarian}"))
        poly_indo_ash = os.path.join(output_loc_shp, f"ash_das_indo_ver_{year_das}{month_das}das0{current_dasarian}")
        arcpy.analysis.Union(in_features=[kec_indo, os.path.join(fgdb_temp, f"ash_das_indo_ver_{year_das}{month_das}das0{current_dasarian}")], 
                                         out_feature_class=poly_indo_ash)
        
        arcpy.management.AddField(
                                in_table=poly_indo_ash,
                                field_name="Area_H", field_type="DOUBLE")
                    
        arcpy.management.CalculateGeometryAttributes(
                in_features=poly_indo_ash,
                geometry_property=[["Area_H", "AREA_GEODESIC"]],
                area_unit="HECTARES")
        
        arcpy.CopyFeatures_management(poly_indo_ash, os.path.join(folder_layout, 'polygon_ash_das'))
        
        
        print("Proses Merge Polygon ACH dan ASH: Indonesia selesai")
        log_to_sde(message = f"Proses Merge Polygon ACH dan ASH: Indonesia selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
        print("\n")


         ### Updating polygon CH di dashboard
        log_to_sde(message = f"Proses Update Polygon ACH Dasboard: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        update_polygon_das(sde_polygon=poly_ach_das, process_polygon=poly_indo_ach)

        log_to_sde(message = f"Proses Update Polygon ACH Dasboard: Indonesia selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        
        ### Updating polygon SH di dashboard
        
        log_to_sde(message = f"Proses Update Polygon ASH Dasboard: Indonesia dimulai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        update_polygon_das(sde_polygon=poly_ash_das, process_polygon=poly_indo_ash)
        
        log_to_sde(message = f"Proses Update Polygon ASH Dasboard: Indonesia selesai", status="INFO", 
                                        tipe_progress="Dasarian", tipe_informasi="Analisis")
        
        print("\n")



        print("Proses Merge CSV ACH dan ASH: Indonesia dimulai . . .")
        log_to_sde(message = f"Proses Merge CSV ACH dan ASH: Indonesia dimulai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
        #Mmebuiat archive
        output_loc_csv = pembuatan_archiving.archive_indo(output_level_indo= output_level_ind, output_tipe_periode=output_tipe_das, tipe='CSV')

        # Merge csv se Indonesia
        combined_df = pd.DataFrame()
        for file in CSV_to_merge:
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file, delimiter=';')
            # Append the DataFrame to the combined DataFrame
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        combined_df.to_csv(os.path.join(output_loc_csv, f"das_indo_ver_{year_das}{month_das}das0{current_dasarian}.csv"), index=False)
        print("Proses Merge CSV ACH dan ASH: Indonesia selesai")
        log_to_sde(message = f"Proses Merge CSV ACH dan ASH: Indonesia selesai", 
                                        status="INFO", tipe_progress="Dasarian", tipe_informasi="Analisis")
        
        print("\n")




        return poly_indo_ach, poly_indo_ash, raster_ACH_to_merge, raster_ASH_to_merge

    except Exception as e:
        print(f"Error Pengolahan Data Indonesia: {e}")
        log_to_sde(message= f"Error Pengolahan Data Indonesia: {e}", status = "ERROR", tipe_progress="Dasarian", tipe_informasi="Analisis")
        # Log additional debug information with status set to DEBUG
        log_to_sde(message = "Detailed debug information for error analysis.", status = "DEBUG", tipe_progress="Dasarian", tipe_informasi="Analisis")

    print("PROSES ANALISIS DASARIAN SELESAI")


