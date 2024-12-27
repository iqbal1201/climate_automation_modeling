'''
Script ini digunakan untuk menghapus temp setelah semua Proses I dijalankan
'''

import arcpy
import os

def empty_fgdb(fgdb_path):
    """
    Empties the contents of the specified File Geodatabase (FGDB).
    
    Parameters:
    fgdb_path (str): Path to the File Geodatabase.
    """
    try:
        # Check if the FGDB exists
        if not arcpy.Exists(fgdb_path):
            raise Exception(f"File Geodatabase does not exist: {fgdb_path}")
        
        # Set the workspace to the FGDB
        arcpy.env.workspace = fgdb_path
        
        # List and delete feature datasets
        feature_datasets = arcpy.ListDatasets("", "Feature")
        for dataset in feature_datasets:
            arcpy.Delete_management(dataset)
            # print(f"Deleted feature dataset: {dataset}")
        
        # List and delete feature classes
        feature_classes = arcpy.ListFeatureClasses()
        for feature_class in feature_classes:
            arcpy.Delete_management(feature_class)
            # print(f"Deleted feature class: {feature_class}")
        
        # List and delete tables
        tables = arcpy.ListTables()
        for table in tables:
            arcpy.Delete_management(table)
            # print(f"Deleted table: {table}")
        
        # List and delete raster datasets
        raster_datasets = arcpy.ListRasters()
        for raster in raster_datasets:
            arcpy.Delete_management(raster)
            # print(f"Deleted raster dataset: {raster}")
        
        # List and delete relationship classes
        relationship_classes = arcpy.ListRelationships()
        for relationship in relationship_classes:
            arcpy.Delete_management(relationship)
            # print(f"Deleted relationship class: {relationship}")
        
        print(f"Successfully emptied the File Geodatabase: {fgdb_path}")
    
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e)
