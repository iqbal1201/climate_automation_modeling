# Parameter for interpolation
extent_pulau = {'NTT' : '118.927002959119 -11.0076153767482 125.193332857026 -7.77865793181803 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'NTB' : '115.820981003271 -9.10965601960959 119.346162224907 -8.08005395782385 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Bali' : '114.431628140926 -8.84925896962568 115.712436009614 -8.06162162313933 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]' ,
                  'Malut' : '124.283099246633 -6.64183298230625 129.923590280667 2.64524507410096 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Maluku' : '125.722520307167 -8.34541150093997 134.908456811133 -2.72545123828399 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kepri': '103.279684216553 -1.27537377987602 109.167114597261 4.79579910164728 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Babel' : '105.108508705812 -3.80160971581569 108.871826028249 -1.49339863673765 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sumatera' : '94.9719518118267 -6.16796564429899 106.220687422587 6.0767684013407 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'NAD' : '94.9719518118267 1.97715200096411 98.2874408863879 6.0767684013407 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sumut' : '97.0574708260179 -0.638797358811019 100.434456035817 4.30254668807925 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sumbar' : '98.5965019151313 -3.57302000037265 101.892882963778 0.906722222852352 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Riau' : '100.049719928432 -1.12760203040932 103.813577353112 2.92115400035686 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Jambi' : '101.130556666657 -2.77005799038392 104.500728368919 -0.730430926046324 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',\
                  'Sumsel' :  '102.063888894357 -4.92415918240027 106.220687422587 -1.62693146341627 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Bengkulu' :  '101.022391691423 -5.51443935888926 103.790488044688 -2.28865368971594 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Lampung' :  '103.590696917129 -6.16796564429899 106.1110309739 -3.72366604425247 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Jawa' : '105.099873731188 -8.78022255682549 116.270189000022 -5.0429653290866 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Banten' :  '105.099873731188 -7.01628117283781 106.779863216015 -5.80758839039186 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'DKI' :  '106.390424798266 -6.37262555572477 106.973390999895 -5.20241887802877 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Jabar' :  '106.37027230872 -7.820989562818 108.847083830654 -5.8065380586844 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Jateng' :  '108.555848823564 -8.21180553419799 111.691393655193 -5.72537100017149 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'DIY' :  '110.003529175031 -8.20562453964072 110.838827850625 -7.54116155925851 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Jatim' : '110.89528623737 -8.78022255682549 116.270189000022 -5.0429653290866 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kalimantan' : '108.598444260794 -4.94274407807671 119.03708614421 4.40846169535104 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kalbar' : '108.598444260794 -3.06791852422049 114.205522583201 2.0814594439982 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kalsel' : '114.346635820587 -4.94274407807671 117.458157058801 -1.3125795360167 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kalteng' : '110.732447353363 -3.54360722409405 115.849358829846 0.791009028144174 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kaltim' : '113.83433533171 -2.40959270094237 119.03708614421 2.61939906121773 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Kaltara' : '114.565164000119 1.11404135402529 117.985933926809 4.40846169535104 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sulawesi' : '117.038291271225 -7.75894120157517 127.163453354689 5.56594630797576 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sulbar'  :   '117.058410824 -3.57057991393185 119.874828088046 -0.849096375597185 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sulsel'  :   '117.038291271225 -7.75894120157517 122.222552631299 -1.88115016644696 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sulteng'  :   '119.42652694786 -3.64056320942456 124.181408050141 1.37428146871486 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sultra'  :   '120.864497544026 -6.21307839725017 124.6168589242 -2.77328875357307 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Sulut'  :   '123.104812308741 0.292131835415944 127.163453354689 5.56594630797576 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Gorontalo'  : '121.161229220053 0.30628139167294 123.55229455505 1.055647735055 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Pulau_Papua': '129.29993427105 -9.12554166671453 141.020041789097 1.08129531522667 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papua'  : '134.299477112279 -3.95672767993841 141.004719444047 0.938007294101396 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papbar'  : '131.577417201143 -4.33079498869773 135.334166666758 -0.713742988348201 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papsel'  : '137.495965436756 -9.12554166671452 141.020041789097 -4.5413156685832 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papteng'  :'134.585257884944 -5.14744646987862 138.301778493683 -2.27452565693346 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papgun'  : '137.826991573702 -5.26482342925783 141.002474721831 -3.1069562128589 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  'Papbarda'  : '129.29993427105 -2.28386464963381 133.493930115283 1.08129531522667 GEOGCS["GCS_WGS_1984".DATUM["D_WGS_1984".SPHEROID["WGS_1984".6378137.0.298.257223563]].PRIMEM["Greenwich".0.0].UNIT["Degree".0.0174532925199433]]',
                  }