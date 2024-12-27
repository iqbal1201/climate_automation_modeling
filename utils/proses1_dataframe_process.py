import arcpy
from arcgis.features import GeoAccessor
from arcgis.gis import GIS
import os
import pandas as pd
import datetime
import locale
from config import nama_stasiun, nama_prov, nama_prov_folder
from dotenv import load_dotenv
load_dotenv()
import matplotlib.pyplot as plt
from utils.proses1_archiving import ArchivingFolder
from utils.dasarian import get_current_dasarian



def dataframe_indo(dataframe, tipe_informasi):
    data = dataframe[['Kategori', 'PROPINSI', 'Pulau_B', 'Area_H']]

    # Agregasi Indonesia
    sum_area = data['Area_H'].sum()
    cat_df = data.groupby('Kategori')['Area_H'].sum()
    indo_df = round(cat_df / sum_area, 4)
    indo_df = indo_df.reset_index()
    indo_df = indo_df.rename({'Area_H' : 'Persentase',}, axis='columns')
    indo_df['Persentase'] = round(indo_df['Persentase']*100,2)
    indo_df['Persentase%'] = round(indo_df['Persentase'],2).astype(str) + '%'
    indo_df.drop(indo_df.index[0], inplace=True)
    indo_df["Wilayah"] = 'INDONESIA'

   

    categories_ch = ['Rendah', 'Menengah', 'Tinggi', 'Sangat Tinggi']
    categories_sh = ['Bawah Normal', 'Normal', 'Atas Normal']

    if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
        all_combinations = pd.MultiIndex.from_product([indo_df['Wilayah'].unique(), categories_ch], names=['Wilayah', 'Kategori']).to_frame(index=False)
        indo_df_complete = all_combinations.merge(indo_df, on=['Wilayah', 'Kategori'], how='left')
        indo_df_complete['Persentase'] = indo_df_complete['Persentase'].fillna(0)
        indo_df_complete['Persentase%'] = indo_df_complete['Persentase%'].fillna('0%')
        non_zero_df = indo_df_complete[indo_df_complete['Persentase'] > 0].copy()
        total_non_zero = non_zero_df['Persentase'].sum()
        non_zero_df['Persentase'] = (non_zero_df['Persentase'] * (100 / total_non_zero)).round(2)
        indo_df_complete.loc[non_zero_df.index, 'Persentase'] = non_zero_df['Persentase']
        if 'Persentase%' in indo_df_complete.columns:
            indo_df_complete['Persentase%'] = indo_df_complete['Persentase'].astype(str) + '%'

        indo_df_pivot = pd.pivot(indo_df_complete, index='Wilayah', columns='Kategori', values='Persentase')
        indo_df_pivot = indo_df_pivot.reset_index()
        indo_df_pivot.columns.name = None

        # Proses statistik wilayah wilayah Provinsi
        prov_area_sum = data.groupby('PROPINSI')['Area_H'].sum()
        prov_cat_area_sum = data.groupby(['Kategori','PROPINSI'])['Area_H'].sum()
        prov_df = round(prov_cat_area_sum / prov_area_sum, 2)
        prov_df = prov_df.reset_index()
        prov_df = prov_df[(prov_df['Kategori'] != " ") & (prov_df['PROPINSI'] != " ")]
        prov_df['Area_H'] = round(prov_df['Area_H']*100, 2)
        all_combinations_prov = pd.MultiIndex.from_product([prov_df['PROPINSI'].unique(), categories_ch], names=['PROPINSI', 'Kategori']).to_frame(index=False)
        prov_df_complete = all_combinations_prov.merge(prov_df, on=['PROPINSI', 'Kategori'], how='left')
        prov_df_complete['Area_H'] = prov_df_complete['Area_H'].fillna(0)
        prov_df_complete_clean = pd.DataFrame()
        for name, group in prov_df_complete.groupby('PROPINSI'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            prov_df_complete_clean = pd.concat([prov_df_complete_clean, group])

        prov_df_complete_clean = prov_df_complete_clean.reset_index(drop=True)

        top_13_areas = prov_df_complete_clean.groupby('Kategori').apply(lambda x: x.nlargest(13, 'Area_H')).reset_index(drop=True)
        top_by_kategori = top_13_areas.groupby('Kategori')['PROPINSI'].apply(lambda x: ', '.join(x)).to_dict()


        prov_df_complete_clean = pd.pivot(prov_df_complete_clean, index='PROPINSI', columns='Kategori', values='Area_H')
        prov_df_complete_clean = prov_df_complete_clean.reset_index()
        prov_df_complete_clean.columns.name = None
        # prov_df_complete_clean.drop(prov_df_complete_clean.index[0], inplace=True)

        # Concat Agregasi Indo to Propinsi
        prov_df_complete_clean = prov_df_complete_clean.rename(columns={'PROPINSI': 'Wilayah'})
        prov_df_complete_clean = pd.concat([indo_df_pivot, prov_df_complete_clean], ignore_index=True)

        prov_df_complete_clean = prov_df_complete_clean.rename(columns={'Rendah': 'Rendah (%)', 'Menengah': 'Menengah (%)','Tinggi': 'Tinggi (%)', 'Sangat Tinggi': 'Sangat Tinggi (%)'})
        new_order = ['Wilayah', 'Rendah (%)', 'Menengah (%)', 'Tinggi (%)', 'Sangat Tinggi (%)']
        prov_df_complete_clean = prov_df_complete_clean[new_order]


        # Get kategori value for agregasi propinsi
        sgt_tinggi = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Sangat Tinggi', 'Persentase'].values[0]
        tinggi = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Tinggi', 'Persentase'].values[0]
        rendah = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Rendah', 'Persentase'].values[0]
        menengah =  indo_df_complete.loc[indo_df_complete['Kategori'] == 'Menengah', 'Persentase'].values[0]



        # Proses statistik wilayah Pulau Besar
        pulau_area_sum = data.groupby('Pulau_B')['Area_H'].sum()
        pulau_cat_df3 = data.groupby(['Kategori','Pulau_B'])['Area_H'].sum()
        pulau_df = round(pulau_cat_df3 / pulau_area_sum, 2)
        pulau_df = pulau_df.reset_index()
        pulau_df = pulau_df[(pulau_df['Kategori'] != " ") & (pulau_df['Pulau_B'] != " ")]

        pulau_df['Area_H'] = round(pulau_df['Area_H']*100, 2)
        all_combinations_pulau = pd.MultiIndex.from_product([pulau_df['Pulau_B'].unique(), categories_ch], names=['Pulau_B', 'Kategori']).to_frame(index=False)
        pulau_df_complete = all_combinations_pulau.merge(pulau_df, on=['Pulau_B', 'Kategori'], how='left')
        pulau_df_complete['Area_H'] = pulau_df_complete['Area_H'].fillna(0)
        pulau_df_complete_clean = pd.DataFrame()
        for name, group in pulau_df_complete.groupby('Pulau_B'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            pulau_df_complete_clean = pd.concat([pulau_df_complete_clean, group])

        pulau_df_complete_clean = pulau_df_complete_clean.reset_index(drop=True)

        pulau_df_complete_clean = pd.pivot(pulau_df_complete_clean, index='Pulau_B', columns='Kategori', values='Area_H')
        pulau_df_complete_clean = pulau_df_complete_clean.reset_index()
        pulau_df_complete_clean.columns.name = None
        # pulau_df_complete_clean.drop(pulau_df_complete_clean.index[0], inplace=True)

        # Concat Agregasi Indo to Pulau_B
        pulau_df_complete_clean = pulau_df_complete_clean.rename(columns={'Pulau_B': 'Wilayah'})
        pulau_df_complete_clean = pd.concat([indo_df_pivot, pulau_df_complete_clean], ignore_index=True)


        pulau_df_complete_clean = pulau_df_complete_clean.rename(columns={'Rendah': 'Rendah (%)', 'Menengah': 'Menengah (%)','Tinggi': 'Tinggi (%)', 'Sangat Tinggi': 'Sangat Tinggi (%)'})
        new_order = ['Wilayah', 'Rendah (%)', 'Menengah (%)', 'Tinggi (%)', 'Sangat Tinggi (%)']
        pulau_df_complete_clean = pulau_df_complete_clean[new_order]


        
        
        return indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah





    else:    # tipe_informasi == 'ANALISIS_SIFAT_HUJAN'

        all_combinations = pd.MultiIndex.from_product([indo_df['Wilayah'].unique(), categories_sh], names=['Wilayah', 'Kategori']).to_frame(index=False)
        indo_df_complete = all_combinations.merge(indo_df, on=['Wilayah', 'Kategori'], how='left')
        indo_df_complete['Persentase'] = indo_df_complete['Persentase'].fillna(0)
        indo_df_complete['Persentase%'] = indo_df_complete['Persentase%'].fillna('0%')
        non_zero_df = indo_df_complete[indo_df_complete['Persentase'] > 0].copy()
        total_non_zero = non_zero_df['Persentase'].sum()
        non_zero_df['Persentase'] = (non_zero_df['Persentase'] * (100 / total_non_zero)).round(2)
        indo_df_complete.loc[non_zero_df.index, 'Persentase'] = non_zero_df['Persentase']
        if 'Persentase%' in indo_df_complete.columns:
            indo_df_complete['Persentase%'] = indo_df_complete['Persentase'].astype(str) + '%'

        indo_df_pivot = pd.pivot(indo_df_complete, index='Wilayah', columns='Kategori', values='Persentase')
        indo_df_pivot = indo_df_pivot.reset_index()
        indo_df_pivot.columns.name = None


        # Proses statistik wilayah wilayah Provinsi
        prov_area_sum = data.groupby('PROPINSI')['Area_H'].sum()
        prov_cat_area_sum = data.groupby(['Kategori','PROPINSI'])['Area_H'].sum()
        prov_df = round(prov_cat_area_sum / prov_area_sum, 2)
        prov_df = prov_df.reset_index()
        prov_df = prov_df[(prov_df['Kategori'] != " ") & (prov_df['PROPINSI'] != " ")]
        prov_df['Area_H'] = round(prov_df['Area_H']*100, 2)
        all_combinations_prov = pd.MultiIndex.from_product([prov_df['PROPINSI'].unique(), categories_sh], names=['PROPINSI', 'Kategori']).to_frame(index=False)
        prov_df_complete = all_combinations_prov.merge(prov_df, on=['PROPINSI', 'Kategori'], how='left')
        prov_df_complete['Area_H'] = prov_df_complete['Area_H'].fillna(0)
        prov_df_complete_clean = pd.DataFrame()
        for name, group in prov_df_complete.groupby('PROPINSI'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            prov_df_complete_clean = pd.concat([prov_df_complete_clean, group])

        prov_df_complete_clean = prov_df_complete_clean.reset_index(drop=True)

        top_13_areas = prov_df_complete_clean.groupby('Kategori').apply(lambda x: x.nlargest(13, 'Area_H')).reset_index(drop=True)
        top_by_kategori = top_13_areas.groupby('Kategori')['PROPINSI'].apply(lambda x: ', '.join(x)).to_dict()


        prov_df_complete_clean = pd.pivot(prov_df_complete_clean, index='PROPINSI', columns='Kategori', values='Area_H')
        prov_df_complete_clean = prov_df_complete_clean.reset_index()
        prov_df_complete_clean.columns.name = None
        #prov_df_complete_clean.drop(prov_df_complete_clean.index[0], inplace=True)

        # Concat Agregasi Indo to Propinsi
        prov_df_complete_clean = prov_df_complete_clean.rename(columns={'PROPINSI': 'Wilayah'})
        prov_df_complete_clean = pd.concat([indo_df_pivot, prov_df_complete_clean], ignore_index=True)

        prov_df_complete_clean = prov_df_complete_clean.rename(columns={'Bawah Normal': 'Bawah Normal (%)', 'Normal': 'Normal (%)','Atas Normal': 'Atas Normal (%)'})
        new_order = ['Wilayah', 'Bawah Normal (%)', 'Normal (%)', 'Atas Normal (%)']
        prov_df_complete_clean = prov_df_complete_clean[new_order]

        # Get kategori value for agregasi propinsi
        atas_normal = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Atas Normal', 'Persentase'].values[0]
        normal = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Normal', 'Persentase'].values[0]
        bawah_normal = indo_df_complete.loc[indo_df_complete['Kategori'] == 'Bawah Normal', 'Persentase'].values[0]



        # Proses statistik wilayah Pulau Besar
        pulau_area_sum = data.groupby('Pulau_B')['Area_H'].sum()
        pulau_cat_df3 = data.groupby(['Kategori','Pulau_B'])['Area_H'].sum()
        pulau_df = round(pulau_cat_df3 / pulau_area_sum, 2)
        pulau_df = pulau_df.reset_index()
        pulau_df = pulau_df[(pulau_df['Kategori'] != " ") & (pulau_df['Pulau_B'] != " ")]

        pulau_df['Area_H'] = round(pulau_df['Area_H']*100, 2)
        all_combinations_pulau = pd.MultiIndex.from_product([pulau_df['Pulau_B'].unique(), categories_sh], names=['Pulau_B', 'Kategori']).to_frame(index=False)
        pulau_df_complete = all_combinations_pulau.merge(pulau_df, on=['Pulau_B', 'Kategori'], how='left')
        pulau_df_complete['Area_H'] = pulau_df_complete['Area_H'].fillna(0)
        pulau_df_complete_clean = pd.DataFrame()
        for name, group in pulau_df_complete.groupby('Pulau_B'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            pulau_df_complete_clean = pd.concat([pulau_df_complete_clean, group])

        pulau_df_complete_clean = pulau_df_complete_clean.reset_index(drop=True)

        pulau_df_complete_clean = pd.pivot(pulau_df_complete_clean, index='Pulau_B', columns='Kategori', values='Area_H')
        pulau_df_complete_clean = pulau_df_complete_clean.reset_index()
        pulau_df_complete_clean.columns.name = None
        # pulau_df_complete_clean.drop(pulau_df_complete_clean.index[0], inplace=True)

        # Concat Agregasi Indo to Pulau_B
        pulau_df_complete_clean = pulau_df_complete_clean.rename(columns={'Pulau_B': 'Wilayah'})
        pulau_df_complete_clean = pd.concat([indo_df_pivot, pulau_df_complete_clean], ignore_index=True)


        pulau_df_complete_clean = pulau_df_complete_clean.rename(columns={'Bawah Normal': 'Bawah Normal (%)', 'Normal': 'Normal (%)','Atas Normal': 'Atas Normal (%)'})
        new_order = ['Wilayah', 'Bawah Normal (%)', 'Normal (%)', 'Atas Normal (%)']
        pulau_df_complete_clean = pulau_df_complete_clean[new_order]
        
        
        return indo_df_complete, prov_df_complete_clean, pulau_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal



def dataframe_upt(dataframe, tipe_informasi, wilayah_upt):
    data = dataframe[['Kategori', 'PROPINSI', 'KABUPATEN', 'KECAMATAN', 'Area_H']]

    data = data[data['PROPINSI'] == wilayah_upt]

    # Agregasi Propinsi
    sum_area = data['Area_H'].sum()
    cat_df = data.groupby('Kategori')['Area_H'].sum()
    prov_df = round(cat_df / sum_area, 4)
    prov_df = prov_df.reset_index()
    prov_df = prov_df.rename({'Area_H' : 'Persentase',}, axis='columns')
    prov_df['Persentase'] = round(prov_df['Persentase']*100,2)
    prov_df['Persentase%'] = round(prov_df['Persentase'],2).astype(str) + '%'
    prov_df.drop(prov_df.index[0], inplace=True)
    prov_df["Wilayah"] = f'PROVINSI {wilayah_upt}'

    categories_ch = ['Rendah', 'Menengah', 'Tinggi', 'Sangat Tinggi']
    categories_sh = ['Bawah Normal', 'Normal', 'Atas Normal']

    if tipe_informasi == 'ANALISIS_CURAH_HUJAN':
        all_combinations = pd.MultiIndex.from_product([prov_df['Wilayah'].unique(), categories_ch], names=['Wilayah', 'Kategori']).to_frame(index=False)
        prov_df_complete = all_combinations.merge(prov_df, on=['Wilayah', 'Kategori'], how='left')
        prov_df_complete['Persentase'] = prov_df_complete['Persentase'].fillna(0)
        prov_df_complete['Persentase%'] = prov_df_complete['Persentase%'].fillna('0%')
        non_zero_df = prov_df_complete[prov_df_complete['Persentase'] > 0].copy()
        total_non_zero = non_zero_df['Persentase'].sum()
        non_zero_df['Persentase'] = (non_zero_df['Persentase'] * (100 / total_non_zero)).round(2)
        prov_df_complete.loc[non_zero_df.index, 'Persentase'] = non_zero_df['Persentase']
        if 'Persentase%' in prov_df_complete.columns:
            prov_df_complete['Persentase%'] = prov_df_complete['Persentase'].astype(str) + '%'

        prov_df_pivot = pd.pivot(prov_df_complete, index='Wilayah', columns='Kategori', values='Persentase')
        prov_df_pivot = prov_df_pivot.reset_index()
        prov_df_pivot.columns.name = None

        # Agregasi Kabupaten
        kab_area_sum = data.groupby('KABUPATEN')['Area_H'].sum()
        kab_cat_area_sum = data.groupby(['Kategori','KABUPATEN'])['Area_H'].sum()
        kab_df = round(kab_cat_area_sum / kab_area_sum, 4)
        kab_df = kab_df.reset_index()
        kab_df = kab_df[(kab_df['Kategori'] != " ") & (kab_df['KABUPATEN'] != " ")]
        kab_df['Area_H'] = round(kab_df['Area_H']*100, 2)
        all_combinations_kab = pd.MultiIndex.from_product([kab_df['KABUPATEN'].unique(), categories_ch], names=['KABUPATEN', 'Kategori']).to_frame(index=False)
        kab_df_complete = all_combinations_kab.merge(kab_df, on=['KABUPATEN', 'Kategori'], how='left')
        kab_df_complete['Area_H'] = kab_df_complete['Area_H'].fillna(0)
        kab_df_complete_clean = pd.DataFrame()
        for name, group in kab_df_complete.groupby('KABUPATEN'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            kab_df_complete_clean = pd.concat([kab_df_complete_clean, group])

        kab_df_complete_clean = kab_df_complete_clean.reset_index(drop=True)


        top_5_areas = kab_df_complete_clean.groupby('Kategori').apply(lambda x: x.nlargest(5, 'Area_H')).reset_index(drop=True)
        top_by_kategori = top_5_areas.groupby('Kategori')['KABUPATEN'].apply(lambda x: ', '.join(x)).to_dict()

        kab_df_complete_clean = pd.pivot(kab_df_complete_clean, index='KABUPATEN', columns='Kategori', values='Area_H')
        kab_df_complete_clean = kab_df_complete_clean.reset_index()
        kab_df_complete_clean.columns.name = None
        # kab_df_complete_clean.drop(kab_df_complete_clean.index[0], inplace=True)


        # Agregasi Kecamatan
        kec_adm = data[[ 'KABUPATEN', 'KECAMATAN']]
        kec_adm = kec_adm.rename(columns={'KECAMATAN': 'Wilayah'})
        kec_adm = kec_adm.drop_duplicates(subset='Wilayah', keep='last')

        kec_area_sum = data.groupby('KECAMATAN')['Area_H'].sum()
        kec_cat_area_sum = data.groupby(['Kategori','KECAMATAN'])['Area_H'].sum()
        kec_df = round(kec_cat_area_sum / kec_area_sum, 4)
        kec_df = kec_df.reset_index()
        kec_df = kec_df[(kec_df['Kategori'] != " ") & (kec_df['KECAMATAN'] != " ")]
        kec_df['Area_H'] = round(kec_df['Area_H']*100, 2)
        all_combinations_kec = pd.MultiIndex.from_product([kec_df['KECAMATAN'].unique(), categories_ch], names=['KECAMATAN', 'Kategori']).to_frame(index=False)
        kec_df_complete = all_combinations_kec.merge(kec_df, on=['KECAMATAN', 'Kategori'], how='left')
        kec_df_complete['Area_H'] = kec_df_complete['Area_H'].fillna(0)
        kec_df_complete_clean = pd.DataFrame()
        for name, group in kec_df_complete.groupby('KECAMATAN'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            kec_df_complete_clean = pd.concat([kec_df_complete_clean, group])

        kec_df_complete_clean = kec_df_complete_clean.reset_index(drop=True)

        kec_df_complete_clean = pd.pivot(kec_df_complete_clean, index='KECAMATAN', columns='Kategori', values='Area_H')
        kec_df_complete_clean = kec_df_complete_clean.reset_index()
        kec_df_complete_clean.columns.name = None
        kec_df_complete_clean.drop(kec_df_complete_clean.index[0], inplace=True)

        # concat kecamatan, kabupaten, provinsi
        kec_df_complete_clean = kec_df_complete_clean.rename(columns={'KECAMATAN': 'Wilayah'})
        kab_df_complete_clean = kab_df_complete_clean.rename(columns={'KABUPATEN': 'Wilayah'})
        # kec_df_complete_clean = pd.concat([kab_df_complete_clean, kec_df_complete_clean], ignore_index=True)
        # kec_df_complete_clean = pd.concat([prov_df_pivot, kec_df_complete_clean], ignore_index=True)

        # merge name kabupaten to dataframe kec
        kec_df_complete_clean = kec_df_complete_clean.merge(kec_adm, on='Wilayah', how='inner')



        # # Concat Propinsi to kabupaten
        # kab_df_complete_clean = kab_df_complete_clean.rename(columns={'KABUPATEN': 'Wilayah'})
        kab_df_complete_clean_copy = kab_df_complete_clean.copy()

        kab_df_complete_clean = pd.concat([prov_df_pivot, kab_df_complete_clean], ignore_index=True)

        # Get kategori value for agregasi propinsi
        sgt_tinggi = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Sangat Tinggi', 'Persentase'].values[0]
        tinggi = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Tinggi', 'Persentase'].values[0]
        rendah = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Rendah', 'Persentase'].values[0]
        menengah =  prov_df_complete.loc[prov_df_complete['Kategori'] == 'Menengah', 'Persentase'].values[0]
        

        kab_df_complete_clean = kab_df_complete_clean.rename(columns={'Rendah': 'Rendah (%)', 'Menengah': 'Menengah (%)','Tinggi': 'Tinggi (%)', 'Sangat Tinggi': 'Sangat Tinggi (%)'})
        new_order = ['Wilayah', 'Rendah (%)', 'Menengah (%)', 'Tinggi (%)', 'Sangat Tinggi (%)']
        kab_df_complete_clean = kab_df_complete_clean[new_order]
        
        return prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, sgt_tinggi, tinggi, menengah, rendah
        
        
        

    elif tipe_informasi == 'ANALISIS_SIFAT_HUJAN':
        all_combinations = pd.MultiIndex.from_product([prov_df['Wilayah'].unique(), categories_sh], names=['Wilayah', 'Kategori']).to_frame(index=False)
        prov_df_complete = all_combinations.merge(prov_df, on=['Wilayah', 'Kategori'], how='left')
        prov_df_complete['Persentase'] = prov_df_complete['Persentase'].fillna(0)
        prov_df_complete['Persentase%'] = prov_df_complete['Persentase%'].fillna('0%')
        non_zero_df = prov_df_complete[prov_df_complete['Persentase'] > 0].copy()
        total_non_zero = non_zero_df['Persentase'].sum()
        non_zero_df['Persentase'] = (non_zero_df['Persentase'] * (100 / total_non_zero)).round(2)
        prov_df_complete.loc[non_zero_df.index, 'Persentase'] = non_zero_df['Persentase']

        # Update the 'Persentase%' column if it exists
        if 'Persentase%' in prov_df_complete.columns:
            prov_df_complete['Persentase%'] = prov_df_complete['Persentase'].astype(str) + '%'

        prov_df_pivot = pd.pivot(prov_df_complete, index='Wilayah', columns='Kategori', values='Persentase')
        prov_df_pivot = prov_df_pivot.reset_index()
        prov_df_pivot.columns.name = None

        # Agregasi Kabupaten
        kab_area_sum = data.groupby('KABUPATEN')['Area_H'].sum()
        kab_cat_area_sum = data.groupby(['Kategori','KABUPATEN'])['Area_H'].sum()
        kab_df = round(kab_cat_area_sum / kab_area_sum, 4)
        kab_df = kab_df.reset_index()
        kab_df = kab_df[(kab_df['Kategori'] != " ") & (kab_df['KABUPATEN'] != " ")]
        kab_df['Area_H'] = round(kab_df['Area_H']*100, 2)
        all_combinations_kab = pd.MultiIndex.from_product([kab_df['KABUPATEN'].unique(), categories_sh], names=['KABUPATEN', 'Kategori']).to_frame(index=False)
        kab_df_complete = all_combinations_kab.merge(kab_df, on=['KABUPATEN', 'Kategori'], how='left')
        kab_df_complete['Area_H'] = kab_df_complete['Area_H'].fillna(0)
        kab_df_complete_clean = pd.DataFrame()
        for name, group in kab_df_complete.groupby('KABUPATEN'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            kab_df_complete_clean = pd.concat([kab_df_complete_clean, group])

        kab_df_complete_clean = kab_df_complete_clean.reset_index(drop=True)


        top_5_areas = kab_df_complete_clean.groupby('Kategori').apply(lambda x: x.nlargest(5, 'Area_H')).reset_index(drop=True)
        top_by_kategori = top_5_areas.groupby('Kategori')['KABUPATEN'].apply(lambda x: ', '.join(x)).to_dict()

        kab_df_complete_clean = pd.pivot(kab_df_complete_clean, index='KABUPATEN', columns='Kategori', values='Area_H')
        kab_df_complete_clean = kab_df_complete_clean.reset_index()
        kab_df_complete_clean.columns.name = None
        # kab_df_complete_clean.drop(kab_df_complete_clean.index[0], inplace=True)


        # Agregasi Kecamatan
        kec_adm = data[[ 'KABUPATEN', 'KECAMATAN']]
        kec_adm = kec_adm.rename(columns={'KECAMATAN': 'Wilayah'})
        kec_adm = kec_adm.drop_duplicates(subset='Wilayah', keep='last')

        
        kec_area_sum = data.groupby('KECAMATAN')['Area_H'].sum()
        kec_cat_area_sum = data.groupby(['Kategori','KECAMATAN'])['Area_H'].sum()
        kec_df = round(kec_cat_area_sum / kec_area_sum, 4)
        kec_df = kec_df.reset_index()
        kec_df = kec_df[(kec_df['Kategori'] != " ") & (kec_df['KECAMATAN'] != " ")]
        kec_df['Area_H'] = round(kec_df['Area_H']*100, 2)
        all_combinations_kec = pd.MultiIndex.from_product([kec_df['KECAMATAN'].unique(), categories_sh], names=['KECAMATAN', 'Kategori']).to_frame(index=False)
        kec_df_complete = all_combinations_kec.merge(kec_df, on=['KECAMATAN', 'Kategori'], how='left')
        kec_df_complete['Area_H'] = kec_df_complete['Area_H'].fillna(0)
        kec_df_complete_clean = pd.DataFrame()
        for name, group in kec_df_complete.groupby('KECAMATAN'):
            non_zero_df = group[group['Area_H'] > 0].copy()
            total_non_zero = non_zero_df['Area_H'].sum()
            
            if total_non_zero > 0:
                non_zero_df['Area_H'] = (non_zero_df['Area_H'] * (100 / total_non_zero)).round(2)
            
            group.loc[non_zero_df.index, 'Area_H'] = non_zero_df['Area_H']
            kec_df_complete_clean = pd.concat([kec_df_complete_clean, group])

        kec_df_complete_clean = kec_df_complete_clean.reset_index(drop=True)

        kec_df_complete_clean = pd.pivot(kec_df_complete_clean, index='KECAMATAN', columns='Kategori', values='Area_H')
        kec_df_complete_clean = kec_df_complete_clean.reset_index()
        kec_df_complete_clean.columns.name = None
        kec_df_complete_clean.drop(kec_df_complete_clean.index[0], inplace=True)

        # concat kecamatan, kabupaten, provinsi
        kec_df_complete_clean = kec_df_complete_clean.rename(columns={'KECAMATAN': 'Wilayah'})
        kab_df_complete_clean = kab_df_complete_clean.rename(columns={'KABUPATEN': 'Wilayah'})
        # kec_df_complete_clean = pd.concat([kab_df_complete_clean, kec_df_complete_clean], ignore_index=True)
        # kec_df_complete_clean = pd.concat([prov_df_pivot, kec_df_complete_clean], ignore_index=True)

        # Merge kecamatan with kab name
        kec_df_complete_clean = kec_df_complete_clean.merge(kec_adm, on='Wilayah', how='inner')



        # # Concat Propinsi to kabupaten
        #kab_df_complete_clean = kab_df_complete_clean.rename(columns={'KABUPATEN': 'Wilayah'})
        kab_df_complete_clean_copy = kab_df_complete_clean.copy()
        kab_df_complete_clean = pd.concat([prov_df_pivot, kab_df_complete_clean], ignore_index=True)

        # Get kategori value for agregasi propinsi
        atas_normal = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Atas Normal', 'Persentase'].values[0]
        normal = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Normal', 'Persentase'].values[0]
        bawah_normal = prov_df_complete.loc[prov_df_complete['Kategori'] == 'Bawah Normal', 'Persentase'].values[0]
        

        kab_df_complete_clean = kab_df_complete_clean.rename(columns={'Bawah Normal': 'Bawah Normal (%)', 'Normal': 'Normal (%)','Atas Normal': 'Atas Normal (%)'})
        new_order = ['Wilayah', 'Bawah Normal (%)', 'Normal (%)', 'Atas Normal (%)']
        kab_df_complete_clean = kab_df_complete_clean[new_order]
        
        
        return prov_df_complete, kab_df_complete_clean, prov_df_pivot, kab_df_complete_clean_copy, kec_df_complete_clean, top_by_kategori, atas_normal, normal, bawah_normal
    







