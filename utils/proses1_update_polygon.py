import arcpy
from datetime import datetime, timedelta

def first_date_of_previous_month():
    today = datetime.now()  # Get the current date
    # Calculate the first day of the current month
    first_of_current_month = today.replace(day=1)
    # Subtract one day to get the last day of the previous month
    last_of_previous_month = first_of_current_month - timedelta(days=1)
    # Get the first day of the previous month
    first_of_previous_month = last_of_previous_month.replace(day=1)
    first_of_previous_month_str = first_of_previous_month.strftime("%d-%m-%Y")
    return first_of_previous_month, first_of_previous_month_str

def first_date_of_dasarian():
    today = datetime.now() # Get the current date
    # Calculate the number of days since the start of the cycle
    days_since_start = today.day % 10
    # Calculate the first day of the current dasarian cycle
    first_dasarian_date = today - timedelta(days=days_since_start)
    first_dasarian_date_str = first_dasarian_date.strftime("%d-%m-%Y")
    return first_dasarian_date, first_dasarian_date_str


def update_polygon_bln(sde_polygon, process_polygon):

    current_date = datetime.now()
    delta_date = current_date - timedelta(days=90)
    delta_date_str = delta_date.strftime('%d-%m-%Y %H:%M:%S')
    date_input_bln, date_input_bln_str = first_date_of_previous_month()
    # add field date in process_polygon
    arcpy.management.AddField(
            in_table=process_polygon,
            field_name="date",
            field_type="DATE",
            field_precision=None,
            field_scale=None,
            field_length=None,
            field_alias="",
            field_is_nullable="NULLABLE",
            field_is_required="NON_REQUIRED",
            field_domain="")
    
    arcpy.management.AddField(
            in_table=process_polygon,
            field_name="date_str",
            field_type="TEXT",
            field_precision=None,
            field_scale=None,
            field_length=10,
            field_alias="",
            field_is_nullable="NULLABLE",
            field_is_required="NON_REQUIRED",
            field_domain="")
    
    print("addfield berhasil")
    
    # calculate current_date
    arcpy.management.CalculateField(
            in_table=process_polygon,
            field="date",
            expression=f"datetime.datetime({date_input_bln.year}, {date_input_bln.month}, {date_input_bln.day})",
            expression_type="PYTHON3",
            code_block="",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
    
    arcpy.management.CalculateField(
            in_table=process_polygon,
            field="date_str",
            expression=f'"{date_input_bln_str}"',
            expression_type="PYTHON3",
            code_block="",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
    
    print("calculate field berhasil")

    # Append process polygon to sde_polygon
    arcpy.management.Append(
            inputs=process_polygon,
            target=sde_polygon,
            schema_type="TEST",
            field_mapping=None,
            subtype="",
            expression="",
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY"
        )
    
    

    with arcpy.da.UpdateCursor(sde_polygon, ["date"]) as cursor:
        for row in cursor:
            # Check if the date is not None before comparing
            if row[0] is not None and row[0] < delta_date:
                cursor.deleteRow()
    
    # # filter date
    # # Select features based on the date condition
    # arcpy.management.SelectLayerByAttribute(
    #                 in_layer_or_view=sde_polygon,
    #                 selection_type="NEW_SELECTION",
    #                 where_clause=f"date <= timestamp '{delta_date_str}'"
    #             )

    # print("Filter berhasil")

    # # Check how many features are selected
    # selected_count = arcpy.management.GetCount(sde_polygon)

    # if selected_count[0] == '0':
    #     print("No features selected for deletion.")
    # else:
    #     # Delete only the selected features
    #     arcpy.management.DeleteFeatures(in_features=sde_polygon)
    #     print(f"Deleted {selected_count[0]} selected features.")

    # # Clear selection if needed
    # arcpy.management.SelectLayerByAttribute(in_layer_or_view=sde_polygon, selection_type="CLEAR_SELECTION")
    
    # print("append berhasil")

    # arcpy.management.SelectLayerByAttribute(
    #         in_layer_or_view=sde_polygon,
    #         selection_type="NEW_SELECTION",
    #         where_clause=f"date <= timestamp '{delta_date_str}'",
    #         invert_where_clause=None
    #     )
    
    # print("filter berhasil")
    
    # # Remove the filtered date
    # arcpy.management.DeleteFeatures(
    #     in_features=sde_polygon)
    
    print("delete berhasil")
    



def update_polygon_das(sde_polygon, process_polygon):

    current_date = datetime.now()
    delta_date = current_date - timedelta(days=90)
    delta_date_str = delta_date.strftime('%Y-%m-%d %H:%M:%S')
    date_input_das, date_input_das_str = first_date_of_dasarian()

    # add field date in process_polygon
    arcpy.management.AddField(
            in_table=process_polygon,
            field_name="date",
            field_type="DATE",
            field_precision=None,
            field_scale=None,
            field_length=None,
            field_alias="",
            field_is_nullable="NULLABLE",
            field_is_required="NON_REQUIRED",
            field_domain="")
    
    arcpy.management.AddField(
            in_table=process_polygon,
            field_name="date_str",
            field_type="TEXT",
            field_precision=None,
            field_scale=None,
            field_length=None,
            field_alias="",
            field_is_nullable="NULLABLE",
            field_is_required="NON_REQUIRED",
            field_domain="")
    
    print("addfield berhasil")
    
    # calculate current_date
    arcpy.management.CalculateField(
            in_table=process_polygon,
            field="date",
            expression=f"datetime.datetime({date_input_das.year}, {date_input_das.month}, {date_input_das.day})",
            expression_type="PYTHON3",
            code_block="",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
    
    arcpy.management.CalculateField(
            in_table=process_polygon,
            field="date_str",
            expression=f'"{date_input_das_str}"',
            expression_type="PYTHON3",
            code_block="",
            field_type="TEXT",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )
    
    print("calculate field date berhasil")
    
    # Append process polygon to sde_polygon
    arcpy.management.Append(
            inputs=process_polygon,
            target=sde_polygon,
            schema_type="TEST",
            field_mapping=None,
            subtype="",
            expression="",
            match_fields=None,
            update_geometry="NOT_UPDATE_GEOMETRY"
        )
    
    print("append berhasil")
    
    # filter date

    with arcpy.da.UpdateCursor(sde_polygon, ["date"]) as cursor:
        for row in cursor:
            # Check if the date is not None before comparing
            if row[0] is not None and row[0] < delta_date:
                cursor.deleteRow()

    # # Select features based on the date condition
    # arcpy.management.SelectLayerByAttribute(
    #                 in_layer_or_view=sde_polygon,
    #                 selection_type="NEW_SELECTION",
    #                 where_clause=f"date <= timestamp '{delta_date_str}'"
    #             )

    # print("Filter berhasil")

    # # Check how many features are selected
    # selected_count = arcpy.management.GetCount(sde_polygon)

    # if selected_count[0] == '0':
    #     print("No features selected for deletion.")
    # else:
    #     # Delete only the selected features
    #     arcpy.management.DeleteFeatures(in_features=sde_polygon)
    #     print(f"Deleted {selected_count[0]} selected features.")

    # # Clear selection if needed
    # arcpy.management.SelectLayerByAttribute(in_layer_or_view=sde_polygon, selection_type="CLEAR_SELECTION")


    # arcpy.management.SelectLayerByAttribute(
    #         in_layer_or_view=sde_polygon,
    #         selection_type="NEW_SELECTION",
    #         where_clause=f"date <= timestamp '{delta_date_str}'",
    #         invert_where_clause=None
    #     )
    
    # print("filter berhasil")
    # # Remove the filtered date
    # arcpy.management.DeleteFeatures(
    #     in_features=sde_polygon)
    
    
    print("remove berhasil")
    
