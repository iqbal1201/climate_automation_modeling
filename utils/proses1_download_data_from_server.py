import os
import requests
import datetime
from utils.dasarian import get_current_dasarian
from utils.proses1_update_polygon import first_date_of_dasarian, first_date_of_previous_month
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




# Define the server URLs and folder paths
main_url_bln = "http://172.19.1.208/direktori-bidang-avi/Analisis_CH_BLENDING/Data_Analisis_Late_Perpulau/BULANAN/XLSX_ANALISIS_BULANAN/"
secondary_url_bln = "http://172.19.3.97/REPOSITORI/03_analisis/BLENDING_HUJAN/BULANAN/LATE_PERPULAU/XLS/"
main_url_das = "http://172.19.1.208/direktori-bidang-avi/Analisis_CH_BLENDING/Data_Analisis_Late_Perpulau/DASARIAN/XLSX_ANALISIS_DASARIAN/"
secondary_url_das = 'http://172.19.3.97/REPOSITORI/03_analisis/BLENDING_HUJAN/DASARIAN/LATE_PERPULAU/XLS/'

download_folder_bln = os.getenv("DOWNLOAD_FOLDER_BLN")
download_folder_das = os.getenv("DOWNLOAD_FOLDER_DAS")

# Define the file name based on current year and month
file_name_bln = f"BlendGSMAP_POS.{year_bln}{month_bln}.xls"  # e.g., BlendGSMAP_POS.202410.xlsx
file_name_das = f"BlendGSMAP_POS.{year_das}{month_das}dec0{current_dasarian}.xls" 

# Construct the local path where the file will be saved
local_file_path_bln = os.path.join(download_folder_bln, file_name_bln)
local_file_path_das = os.path.join(download_folder_das, file_name_das)



# Construct the full URLs for both servers
main_file_url_bln = main_url_bln + file_name_bln
secondary_file_url_bln = secondary_url_bln + file_name_bln
main_file_url_das = main_url_das + file_name_das
secondary_file_url_das = secondary_url_das + file_name_das



# Function to download the file from a given URL
def download_file(url, save_path):
    try:
        # Send GET request to download the file
        response = requests.get(url, stream=True)
        
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the local file in write-binary mode
            with open(save_path, 'wb') as file:
                # Write the content of the file in chunks
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            print(f"File downloaded successfully to {save_path}")
            return True  # Return True if download is successful
        else:
            print(f"Failed to download file from {url}. Status code: {response.status_code}")
            return False  # Return False if file is not found or another error occurred
    except requests.RequestException as e:
        print(f"An error occurred while downloading the file: {e}")
        return False  # Return False if an exception occurred
    



# Main function to attempt download from the main server first, then the secondary server if needed
def download_data(main_url, sec_url, folder_path):
    # Attempt to download the file from the main server
    print(f"Attempting to download the file from the main server: {main_url}")
    
    # Try downloading from the main server first
    if download_file(main_url, folder_path):
        print("Download completed from the main server.")
    else:
        # If the main server fails, attempt to download from the secondary server
        print(f"Main server failed. Trying the secondary server: {sec_url}")
        if download_file(sec_url, folder_path):
            print("Download completed from the secondary server.")
        else:
            print("Download failed from both servers.")
       
