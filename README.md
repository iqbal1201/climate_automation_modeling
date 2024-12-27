## Software Engineering: Python Automation (Arcpy) For Climate Data Modeling ##

#### Background ###
This project was developed with the aim of displaying rainfall data and rain characteristics over various periods (10-day and monthly) in Indonesia. The system consists of an automation system to re-interpolate weather data, display it, and generate analytical reports on national and provincial rainfall and rain characteristics in Indonesia. In this section, the device reads initial data in the form of CSV files that represent location data related to rainfall (measured in millimeters) and rain characteristics (expressed as a percentage unit). There are two types of CSV data in this system: 10-day period data and monthly period data. Thus, the system generally processes four types of data, which are combinations of 10-day rainfall analysis data (ACHdas), monthly rainfall analysis data (ACHbln), 10-day rain characteristics analysis data (ASHdas), and monthly rain characteristics analysis data (ASHbln). An overview of the data used in this system can be seen in the image below.

The system can essentially be described as an automation of the real-time re-analysis process of rainfall and rain characteristics data into interpolated raster forms. It is called re-analysis because the input data, as shown in the image, is rainfall data in raster form that is converted into tabular form. The system will create re-interpolated rasters for the CH column and the SH% column for both 10-day and monthly periods. Thus, four interpolations will be produced for this system in each processing cycle: ACHdas interpolation, ACHbln interpolation, ASHdas interpolation, and ASHbln interpolation.

The interpolation method used in this system is the Inverse Distance Weighted (IDW) method in ArcGIS Pro software. This method estimates cell values by averaging the values of sample data points around each processing cell. In the IDW interpolation process, the grid/pixel size of the resulting raster is set to 0.01x0.01 for small islands (Bali, Riau Islands, Bangka Belitung Islands, East Nusa Tenggara Islands, West Nusa Tenggara Islands, Maluku Islands, North Maluku Islands) and 0.05x0.05 for large islands (Sumatra, Java, Kalimantan, Sulawesi, Papua). The interpolation process is conducted for each island (both large and small). Subsequently, the interpolation results are stitched into a mosaic dataset to create ACHdas/ACHbln/ASHdas/ASHbln rasters for all of Indonesia and clipped by province to produce ACHdas/ACHbln/ASHdas/ASHbln rasters for each province.

![image](https://github.com/user-attachments/assets/844aa931-f80a-4435-a12b-1e0c1a859cd4)

#### Example Output ###
##### Maps #####
All these outputs are produced automatically by the system on each month (monthly) or on each 10 days.

![image](https://github.com/user-attachments/assets/d60df59f-2b90-45b5-a845-d1d01826e225)

![image](https://github.com/user-attachments/assets/91688bfe-a549-4cb8-8cc9-603c6ac49c03)

![image](https://github.com/user-attachments/assets/a18cc005-bdb6-4788-a42f-0759f1e7feab)

![image](https://github.com/user-attachments/assets/684b20fe-04ee-4cba-9eaf-8aa2bdc26a7f)

![image](https://github.com/user-attachments/assets/04f7cc41-b1ee-4972-b8fe-8d325c663c9a)


##### Dashboard #####

![image](https://github.com/user-attachments/assets/bb390df4-d925-419f-8ae8-ffabe35d40b9)
![image](https://github.com/user-attachments/assets/2c073ae2-414a-4a04-9cb9-bdd5e3a9f0cc)


