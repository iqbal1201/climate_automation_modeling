import arcpy
import os, shutil
import datetime
import base64
from glob import glob
#from common_lib.env import constant
# from reporting_process_prediksi import reporting
import requests
from bs4 import BeautifulSoup

arcpy.env.overwriteOutput = True



class downloadBulk:
    SUBDOWNLOAD = None
    SUBDOWNLOAD_NORMAL = None

    def __init__(
        self,
        main_root_url: str,
        secondary_root_url: str,
        download_folder: str,
        progress_type: str,
        parameter: str,
        today_date=datetime.datetime.today(),
    ):
        """
        main_root_url = http://172.19.1.208/direktori-bidang-avi/MODEL_ECMWF

        secondary_root_url = http://172.19.3.97/REPOSITORI/05_prediksi/HUJAN/MODEL_ECMWF

        download_folder = path/to/folder for downloading

        progress_type = BULANAN or DASARIAN

        today_date = object today date by default

        """
        self.main_root_url = main_root_url
        self.secondary_root_url = secondary_root_url
        self.download_folder = download_folder
        self.progress_type = progress_type
        self.parameter = parameter
        self.today_date = today_date

    def file_from_folder(self):
        get_year = self.today_date.strftime("%Y")
        get_month = self.today_date.strftime("%m")
        get_date = self.today_date.strftime("%d")
        get_dasa_number = downloadBulk.get_dasa_string(int(get_date))

        child_folder_main = None
        child_folder_second = None
        if self.parameter.upper() == "PREDIKSI":
            if self.progress_type.upper() == "BULANAN":
                child_folder_main = f"direktori-bidang-avi/MODEL_ECMWF/BULANAN/SEAS5_ver_{get_year}.{get_month}.01/{get_year}.{get_month}.01_seasonal/CSV/"
                child_folder_second = (
                    f"REPOSITORI/05_prediksi/HUJAN/MODEL_ECMWF/BULANAN/{get_year}.{get_month}.01_seasonal/CSV/"
                )
            elif self.progress_type.upper() == "DASARIAN":
                child_folder_main = f"direktori-bidang-avi/MODEL_ECMWF/DASARIAN_Corrected/{get_year}.{get_month}.{get_date}_dasarian/CSV/"
                child_folder_second = f"REPOSITORI/05_prediksi/HUJAN/MODEL_ECMWF/DASARIAN_Corrected/{get_year}.{get_month}.{get_date}_dasarian/CSV/"
        elif self.parameter.upper() == "ANALISIS":
            if self.progress_type.upper() == "BULANAN":
                child_folder_main = f"direktori-bidang-avi/Analisis_CH_BLENDING/Data_Analisis_Late_Perpulau/BULANAN/XLSX_ANALISIS_BULANAN/"
                child_folder_second = f"REPOSITORI/03_analisis/BLENDING_HUJAN/BULANAN/LATE_PERPULAU/XLS/"
            elif self.progress_type.upper() == "DASARIAN":
                child_folder_main = f"direktori-bidang-avi/Analisis_CH_BLENDING/Data_Analisis_Late_Perpulau/DASARIAN/XLSX_ANALISIS_DASARIAN/"
                child_folder_second = f"REPOSITORI/03_analisis/BLENDING_HUJAN/DASARIAN/LATE_PERPULAU/XLS/"

        url_main = f"{self.main_root_url}{child_folder_main}"
        response_main = requests.get(url_main)
        url_secondary = f"{self.secondary_root_url}{child_folder_second}"
        response_secondary = requests.get(url_secondary)

        # Check if the request was successful
        if self.parameter.upper() == "PREDIKSI":
            if response_main.status_code == 200:
                # Parse the HTML content of the response

                soup = BeautifulSoup(response_main.content, "html.parser")
                # Find all <a> tags that represent links
                links = soup.find_all("a")
                # Extract the href attribute of each link

                if self.progress_type.upper() == "BULANAN":
                    for link in links:
                        file_href = link["href"]
                        if "pch_ensMean." in file_href:
                            print(file_href)
                            url_file = f"{url_main}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                    url_normal = f"{self.main_root_url}direktori-bidang-avi/NORMAL_HUJAN_1991-2020/NormalHujan9120versi_2110/curah_hujan/bulanan/CSV/"
                    subdownload_folder_normal = os.path.join(self.download_folder, "NORMAL", self.progress_type.upper())
                    downloadBulk.SUBDOWNLOAD_NORMAL = subdownload_folder_normal
                    downloadBulk.check_and_create_folder(subdownload_folder_normal)
                    response_normal = requests.get(url_normal)

                    soup_normal = BeautifulSoup(response_normal.content, "html.parser")
                    # Find all <a> tags that represent links
                    links = soup_normal.find_all("a")

                    for i in range(0, 8):
                        if i == 0:
                            future_date = self.today_date + datetime.timedelta(weeks=i)

                        elif i > 0:
                            months_to_week = i * 4
                            future_date = self.today_date + datetime.timedelta(weeks=months_to_week)
                            get_date = int(future_date.strftime("%d"))

                            if get_date >= 25 or get_date <= 31:
                                future_date = future_date + datetime.timedelta(weeks=1)
                            else:
                                future_date = future_date

                        get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        if get_month < 10:
                            get_month = f"0{get_month}"
                        elif get_month >= 10:
                            get_month = f"{get_month}"

                        for link in links:
                            file_href_normal = link["href"]
                            if f"BlendCHIRP_POS_RTOTBLN_NORMAL_{get_month}" in file_href_normal:
                                local_file_download = os.path.join(subdownload_folder_normal, file_href_normal)
                                with requests.get(url_normal, stream=True) as r:
                                    with open(local_file_download, "wb") as f:
                                        shutil.copyfileobj(r.raw, f)

                elif self.progress_type.upper() == "DASARIAN":
                    for link in links:
                        file_href = link["href"]
                        if "pch_det." in file_href:
                            print(file_href)
                            url_file = f"{url_main}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                        url_normal = f"{self.main_root_url}direktori-bidang-avi/NORMAL_HUJAN_1991-2020/NormalHujan9120versi_2110/curah_hujan/dasarian/csv_ntt/"
                        subdownload_folder_normal = os.path.join(
                            self.download_folder, "NORMAL", self.progress_type.upper()
                        )
                        downloadBulk.SUBDOWNLOAD_NORMAL = subdownload_folder_normal
                        downloadBulk.check_and_create_folder(subdownload_folder_normal)
                        response_normal = requests.get(url_normal)

                        soup_normal = BeautifulSoup(response_normal.content, "html.parser")
                        # Find all <a> tags that represent links
                        links = soup_normal.find_all("a")

                    url_normal = f"{self.main_root_url}direktori-bidang-avi/NORMAL_HUJAN_1991-2020/NormalHujan9120versi_2110/curah_hujan/dasarian/csv_ntt/"
                    subdownload_folder_normal = os.path.join(self.download_folder, "NORMAL", self.progress_type.upper())
                    downloadBulk.check_and_create_folder(subdownload_folder)

                    soup_normal = BeautifulSoup(response_normal.content, "html.parser")
                    # Find all <a> tags that represent links
                    links = soup_normal.find_all("a")

                    n_week = int(get_dasa_number)
                    for i in range(0, 4):
                        future_date = self.today_date + datetime.timedelta(weeks=i + 1)

                        get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        if get_month < 10:
                            get_month = f"0{get_month}"
                        elif get_month >= 10:
                            get_month = f"{get_month}"

                        if n_week == 4:
                            n_week = 1
                            future_date = future_date + datetime.timedelta(weeks=1)
                            get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        else:
                            n_week = n_week

                        for link in links:
                            file_href_normal = link["href"]
                            if f"BlendCHIRP_POS_RTOTDAS_NORMAL_{get_month}0{n_week}" in file_href_normal:
                                local_file_download = os.path.join(subdownload_folder_normal, file_href_normal)
                                with requests.get(url_normal, stream=True) as r:
                                    with open(local_file_download, "wb") as f:
                                        shutil.copyfileobj(r.raw, f)

                        n_week = n_week + 1

            elif response_secondary.status_code == 200:
                # Parse the HTML content of the response
                full_link = f"{self.secondary_root_url}{child_folder_second}"
                soup = BeautifulSoup(response_secondary.content, "html.parser")
                # Find all <a> tags that represent links
                links = soup.find_all("a")
                # Extract the href attribute of each link
                if self.progress_type.upper() == "BULANAN":
                    for link in links:
                        file_href = link["href"]
                        if "pch_ensMean." in file_href:
                            print(file_href)
                            url_file = f"{url_secondary}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                    url_normal = f"{self.secondary_root_url}REPOSITORI/06_normal/NORMAL_1991-2020/NormalHujan9120versi_2110/curah_hujan/bulanan/CSV/"
                    subdownload_folder_normal = os.path.join(self.download_folder, "NORMAL", self.progress_type.upper())
                    downloadBulk.SUBDOWNLOAD_NORMAL = subdownload_folder_normal
                    downloadBulk.check_and_create_folder(subdownload_folder)
                    response_normal = requests.get(url_normal)

                    soup_normal = BeautifulSoup(response_normal.content, "html.parser")
                    # Find all <a> tags that represent links
                    links = soup_normal.find_all("a")

                    for i in range(0, 8):
                        if i == 0:
                            future_date = self.today_date + datetime.timedelta(weeks=i)

                        elif i > 0:
                            months_to_week = i * 4
                            future_date = self.today_date + datetime.timedelta(weeks=months_to_week)
                            get_date = int(future_date.strftime("%d"))

                            if get_date >= 25 or get_date <= 31:
                                future_date = future_date + datetime.timedelta(weeks=1)
                            else:
                                future_date = future_date

                        get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        if get_month < 10:
                            get_month = f"0{get_month}"
                        elif get_month >= 10:
                            get_month = f"{get_month}"

                        for link in links:
                            file_href_normal = link["href"]
                            if f"BlendCHIRP_POS_RTOTBLN_NORMAL_{get_month}" in file_href_normal:
                                local_file_download = os.path.join(subdownload_folder_normal, file_href_normal)
                                with requests.get(url_normal, stream=True) as r:
                                    with open(local_file_download, "wb") as f:
                                        shutil.copyfileobj(r.raw, f)

                elif self.progress_type.upper() == "DASARIAN":
                    for link in links:
                        file_href = link["href"]
                        if "pch_det." in file_href:
                            print(file_href)
                            url_file = f"{url_secondary}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                    url_normal = f"{self.secondary_root_url}REPOSITORI/06_normal/NORMAL_1991-2020/NormalHujan9120versi_2110/curah_hujan/bulanan/CSV/"
                    subdownload_folder_normal = os.path.join(self.download_folder, "NORMAL", self.progress_type.upper())
                    downloadBulk.SUBDOWNLOAD_NORMAL = subdownload_folder_normal
                    downloadBulk.check_and_create_folder(subdownload_folder)
                    response_normal = requests.get(url_normal)

                    soup_normal = BeautifulSoup(response_normal.content, "html.parser")
                    # Find all <a> tags that represent links
                    links = soup_normal.find_all("a")

                    n_week = int(get_dasa_number)
                    for i in range(0, 4):
                        future_date = self.today_date + datetime.timedelta(weeks=i + 1)

                        get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        if get_month < 10:
                            get_month = f"0{get_month}"
                        elif get_month >= 10:
                            get_month = f"{get_month}"

                        if n_week == 4:
                            n_week = 1
                            future_date = future_date + datetime.timedelta(weeks=1)
                            get_month = int(datetime.datetime.strftime(future_date, "%m"))
                        else:
                            n_week = n_week

                        for link in links:
                            file_href_normal = link["href"]
                            if f"BlendCHIRP_POS_RTOTDAS_NORMAL_{get_month}0{n_week}" in file_href_normal:
                                local_file_download = os.path.join(subdownload_folder_normal, file_href_normal)
                                with requests.get(url_normal, stream=True) as r:
                                    with open(local_file_download, "wb") as f:
                                        shutil.copyfileobj(r.raw, f)

                        n_week = n_week + 1

        elif self.parameter.upper() == "ANALISIS":
            if response_main.status_code == 200:
                # Parse the HTML content of the response

                soup = BeautifulSoup(response_main.content, "html.parser")
                # Find all <a> tags that represent links
                links = soup.find_all("a")
                # Extract the href attribute of each link
                if self.progress_type.upper() == "BULANAN":
                    for link in links:
                        file_href = link["href"]
                        if f"BlendGSMAP_POS.{get_year}{get_month}" in file_href:
                            print(file_href)
                            url_file = f"{url_main}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                elif self.progress_type.upper() == "DASARIAN":
                    for link in links:
                        file_href = link["href"]
                        if f"BlendGSMAP_POS.{get_year}{get_month}dec{get_dasa_number}" in file_href:
                            print(file_href)
                            url_file = f"{url_main}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

            elif response_secondary.status_code == 200:
                # Parse the HTML content of the response

                soup = BeautifulSoup(response_secondary.content, "html.parser")
                # Find all <a> tags that represent links
                links = soup.find_all("a")
                # Extract the href attribute of each link
                if self.progress_type.upper() == "BULANAN":
                    for link in links:
                        file_href = link["href"]
                        if f"BlendGSMAP_POS.{get_year}{get_month}" in file_href:
                            print(file_href)
                            url_file = f"{url_secondary}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

                elif self.progress_type.upper() == "DASARIAN":
                    for link in links:
                        file_href = link["href"]
                        if f"BlendGSMAP_POS.{get_year}{get_month}dec{get_dasa_number}" in file_href:
                            print(file_href)
                            url_file = f"{url_secondary}{file_href}"
                            subdownload_folder = os.path.join(self.download_folder, self.progress_type.upper())
                            downloadBulk.SUBDOWNLOAD = subdownload_folder
                            downloadBulk.check_and_create_folder(subdownload_folder)

                            local_file_download = os.path.join(subdownload_folder, file_href)
                            with requests.get(url_file, stream=True) as r:
                                with open(local_file_download, "wb") as f:
                                    shutil.copyfileobj(r.raw, f)

    def remove_folder(self, is_normal: bool):
        if is_normal is True:
            shutil.rmtree(downloadBulk.SUBDOWNLOAD_NORMAL, ignore_errors=True)
        if is_normal is False:
            shutil.rmtree(downloadBulk.SUBDOWNLOAD, ignore_errors=True)

    @staticmethod
    def check_and_create_folder(input_folder):
        if os.path.isdir(input_folder):
            pass
        else:
            os.mkdir(input_folder)

    @staticmethod
    def get_dasa_string(value: int):
        dasa = None
        if value > 1 and value <= 10:
            dasa = "01"
        elif value > 10 and value <= 20:
            dasa = "02"
        elif value > 20 and value <= 30:
            dasa = "03"
        elif value == 31:
            dasa = "04"
        return dasa




