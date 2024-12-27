import logging
import arcpy
import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("arcpy_logging.log"),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger()

def log_to_sde( message, status="INFO", tipe_progress="DASARIAN", tipe_informasi="Prediksi"):
    """Logs a message to the SDE database according to the specified table schema."""
    table_path = r'F:\ASSET\spatial\BMKG_PinterIklim\PostgreSQL-gisdbiklim-geodb_bmkg(sde).sde\geodb_bmkg.sde.log_table'
    current_time = datetime.datetime.now()

    with arcpy.da.InsertCursor(table_path, ["status", "message", "datetime", "progress_type", "tipe_informasi"]) as cursor:
        cursor.insertRow([status, message, current_time, tipe_progress, tipe_informasi])

    # Log to file and console based on status
    if status == "INFO":
        logger.info(message)
    elif status == "DEBUG":
        logger.debug(message)
    elif status == "ERROR":
        logger.error(message)
