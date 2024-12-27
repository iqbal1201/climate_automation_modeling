import arcpy
from datetime import datetime, timedelta
import os




def copy_raster(input_raster, output_raster):
    """
    Copies a raster dataset from the input location to the output location.

    Parameters:
    input_raster (str): Path to the input raster dataset.
    output_raster (str): Path to the output raster dataset.
    """
    try:
        # Use the CopyRaster function to copy the raster
        arcpy.management.CopyRaster(
                in_raster=input_raster,
                out_rasterdataset=output_raster,
                config_keyword="",
                background_value=None,
                nodata_value="",
                onebit_to_eightbit="NONE",
                colormap_to_RGB="NONE",
                pixel_type="",
                scale_pixel_value="NONE",
                RGB_to_Colormap="NONE",
                format="",
                transform="NONE",
                process_as_multidimensional="CURRENT_SLICE",
                build_multidimensional_transpose="NO_TRANSPOSE"
)
        print(f"Raster copied from {input_raster} to {output_raster}")
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
    except Exception as e:
        print(e)



# Function to add raster and update fields
def add_raster_and_update_fields(raster_path, area, mosaic_data):
    # Add the raster to the mosaic dataset
    # Add the raster to the mosaic dataset
    # Add the raster to the mosaic dataset
    arcpy.management.AddRastersToMosaicDataset(
        in_mosaic_dataset=mosaic_data,
        raster_type="Raster Dataset",
        input_path=raster_path,
        update_cellsize_ranges="UPDATE_CELL_SIZES",
        update_boundary="UPDATE_BOUNDARY",
        update_overviews="NO_OVERVIEWS",
        maximum_pyramid_levels=None,
        maximum_cell_size=0,
        minimum_dimension=1500,
        spatial_reference=None,
        filter="",
        sub_folder="SUBFOLDERS",
        duplicate_items_action="ALLOW_DUPLICATES",
        build_pyramids="BUILD_PYRAMIDS",
        calculate_statistics="CALCULATE_STATISTICS",
        build_thumbnails="NO_THUMBNAILS",
        operation_description="",
        force_spatial_reference="NO_FORCE_SPATIAL_REFERENCE",
        estimate_statistics="ESTIMATE_STATISTICS",
        aux_inputs=None,
        enable_pixel_cache="NO_PIXEL_CACHE"
    )
    
    # Get the current date in the format YYYY-MM-DD
    # current_date = datetime.now().strftime("%Y-%m-%d")
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    # Add a unique identifier using timestamp down to microseconds
    unique_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    # Find the highest OBJECTID to identify the newly added raster
    max_objectid = None
    with arcpy.da.SearchCursor(mosaic_data, ["objectid"]) as cursor:
        for row in cursor:
            if max_objectid is None or row[0] > max_objectid:
                max_objectid = row[0]

    # Update the fields for the newly added raster
    with arcpy.da.UpdateCursor(mosaic_data, ["objectid", "area_upt", "date"]) as cursor:
        for row in cursor:
            if row[0] == max_objectid:
                row[1] = area
                row[2] = current_date
                cursor.updateRow(row)

    print(f"Berhasil menambahkan {area}")

# Function to delete rasters older than two months
# def delete_old_rasters(mosaic_data):
#     # Calculate the date two months ago from today
    
#     two_months_ago = datetime.now() - timedelta(days=60)
    
#     # Use an UpdateCursor to delete rasters older than two months
#     with arcpy.da.UpdateCursor(mosaic_data, ["objectid", "date"]) as cursor:
#         for row in cursor:
#             # Check if row[1] is already a datetime object
#             if isinstance(row[1], datetime):
#                 raster_date = row[1]
#             else:
#                 raster_date = datetime.strptime(row[1], "%Y-%m-%d")
            
#             if raster_date < two_months_ago:
#                 cursor.deleteRow()

# from datetime import datetime, timedelta
# import arcpy

def delete_old_rasters(mosaic_data):
    # Calculate the date two months ago from today
    two_months_ago = datetime.now() - timedelta(days=60)
    
    # Use an UpdateCursor to delete rasters older than two months
    with arcpy.da.UpdateCursor(mosaic_data, ["OBJECTID", "date"]) as cursor:
        for row in cursor:
            # If the date is None, assume it's an old entry and delete it
            if row[1] is None:
                cursor.deleteRow()
                continue
            
            # Check if row[1] is already a datetime object
            if isinstance(row[1], datetime):
                raster_date = row[1]
            else:
                raster_date = datetime.strptime(row[1], "%Y-%m-%d")
            
            # Delete rows where the date is older than two months
            if raster_date < two_months_ago:
                cursor.deleteRow()
