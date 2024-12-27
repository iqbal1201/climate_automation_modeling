'''
Script ini digunakan untuk membuat chart yang ada pada infografis maupun laporan singkat
'''


import arcpy
from arcgis.features import GeoAccessor
import os
import pandas as pd
import datetime
import locale
from config import nama_stasiun, nama_prov
from dotenv import load_dotenv
load_dotenv()
import matplotlib.pyplot as plt
from utils.proses1_archiving import ArchivingFolder
from utils.dasarian import get_current_dasarian



def cut_image(original_image_path, ach_path, ash_path):
    import os
    import imageio
    
    img = imageio.imread(original_image_path)
    height, width = img.shape[:2]  # Get the height and width

    # Cut the image in half
    width_cutoff = width // 2
    s1 = img[:, :width_cutoff]
    s2 = img[:, width_cutoff:]

    # Save each half
    imageio.imwrite(ach_path, s1)
    imageio.imwrite(ash_path, s2)

    os.remove(original_image_path)


def chart_infografis_ch(dataframe):
    output_location = os.getenv("ASSET")
    fig, ax = plt.subplots(figsize=(8, 4))
    categories = ['Rendah', 'Menengah', 'Tinggi', 'Sangat Tinggi']
    colors = ['#340900', '#ffff00', '#8bd48b', '#00450c']

    # Reorder DataFrame based on categories
    dataframe['Kategori'] = pd.Categorical(dataframe['Kategori'], categories=categories)
    dataframe = dataframe.sort_values('Kategori')
    # Plot bars
    bars = ax.bar(dataframe['Kategori'], dataframe['Persentase'], color=colors, edgecolor='black', linewidth=0.5, width=0.95)
    # Add text labels
    for bar in bars:
        height = bar.get_height()
        if height < 10:  # Adjust this threshold as needed
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height}%', ha='center', va='bottom', fontsize=16, fontweight='bold',color='red')
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2, f'{height}%', ha='center', va='center', fontsize=16, fontweight='bold', color='red')
    # Set y-axis range and labels
    ax.set_ylim(0, 100)
    ax.set_ylabel('Persentase', fontsize=18, color='black', fontfamily="Arial")
    # Remove x-axis ticks and labels
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    # Set background color to transparent
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    # Set plot background color to transparent
    ax.set_facecolor('none')
    # Add gridlines for y-axis
    ax.yaxis.grid(True, color='grey', linestyle='--', linewidth=0.5, zorder=0)
    # Set bars zorder to 2 to ensure they are in front of the gridlines
    for bar in bars:
        bar.set_zorder(2)
    # Save the figure
    fig.savefig(os.path.join(output_location,'chart', 'infografis', 'chart_infografis_ch.png'), dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)


def chart_infografis_sh(dataframe):
    output_location = os.getenv("ASSET")
    fig, ax = plt.subplots(figsize=(8, 4))
    categories = ['Bawah Normal', 'Normal', 'Atas Normal']
    colors = ['#340900', '#ffff00', '#00450c']

    # Reorder DataFrame based on categories
    dataframe['Kategori'] = pd.Categorical(dataframe['Kategori'], categories=categories)
    dataframe = dataframe.sort_values('Kategori')
    # Plot bars
    bars = ax.bar(dataframe['Kategori'], dataframe['Persentase'], color=colors, edgecolor='black', linewidth=0.5, width=0.95)
    # Add text labels
    for bar in bars:
        height = bar.get_height()
        if height < 10:  # Adjust this threshold as needed
            ax.text(bar.get_x() + bar.get_width() / 2, height, f'{height}%', ha='center', va='bottom', fontsize=16, fontweight='bold', color='red')
        else:
            ax.text(bar.get_x() + bar.get_width() / 2, height / 2, f'{height}%', ha='center', va='center', fontsize=16, fontweight='bold', color='red')
    # Set y-axis range and labels
    ax.set_ylim(0, 100)
    ax.set_ylabel('Persentase', fontsize=18, color='black', fontfamily="Arial")
    # Remove x-axis ticks and labels
    ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    # Set background color to transparent
    fig.patch.set_alpha(0)
    ax.patch.set_alpha(0)
    # Set plot background color to transparent
    ax.set_facecolor('none')
    # Add gridlines for y-axis
    ax.yaxis.grid(True, color='grey', linestyle='--', linewidth=0.5, zorder=0)
    # Set bars zorder to 2 to ensure they are in front of the gridlines
    for bar in bars:
        bar.set_zorder(2)
    # Save the figure
    fig.savefig(os.path.join(output_location,'chart', 'infografis', 'chart_infografis_sh.png'), dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)


def laporan_tabel(dataframe):
    folder_aset = os.getenv("ASSET")
    row_count = dataframe.shape[0]
    fig_height = 0.1 * row_count + 2  # Adjust the multiplier and base height as needed

    fig, ax = plt.subplots(figsize=(10, fig_height))
    ax.axis('tight')
    ax.axis('off')

    # Convert column labels to uppercase
    col_labels = [label.upper() for label in dataframe.columns]

    # Create table
    table = ax.table(cellText=dataframe.values, colLabels=col_labels, cellLoc='center', loc='center')

    # Set font size
    table.auto_set_font_size(False)
    table.set_fontsize(14)

    # Make the heading bold and set cell borders
    for key, cell in table.get_celld().items():
        if key[0] == 0:  # This is the header row
            cell.set_text_props(fontweight='bold')
        cell.set_edgecolor('black')  # Set edge color for all cells
        cell.set_linewidth(1)        # Set line width for all cells

    # Adjust cell width
    for i, col in enumerate(dataframe.columns):
        max_col_width = max(dataframe[col].astype(str).apply(len).max(), len(col)) + 2
        table.auto_set_column_width([i])
        for key, cell in table.get_celld().items():
            if key[1] == i:
                cell.set_width(max_col_width * 1)

    # Adjust cell height
    for key, cell in table.get_celld().items():
        cell.set_height(0.15)  # Adjust the height multiplier as needed

    # Adjust column width
    table.scale(1.5, 1.5)

    output_file = os.path.join(folder_aset, 'table', 'table_laporan.png')
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)

def chart_laporan_ch(dataframe):
    folder_aset = os.getenv("ASSET")
    regions = dataframe['Wilayah']
    rendah_val = dataframe['Rendah (%)']
    menengah_val = dataframe['Menengah (%)']
    tinggi_val = dataframe['Tinggi (%)']
    sgt_tinggi_val = dataframe['Sangat Tinggi (%)']
    threshold = 3.5  # threshold for bar label visibility

    # Add text label
    rendah_text = [f'{val:.2f}%' if val >= threshold else '' for val in rendah_val]
    menengah_text = [f'{val:.2f}%' if val >= threshold else '' for val in menengah_val]
    tinggi_text = [f'{val:.2f}%' if val >= threshold else '' for val in tinggi_val]
    sgt_tinggi_text = [f'{val:.2f}%' if val >= threshold else '' for val in sgt_tinggi_val]

    bar_height = 0.8  # Height of the bars, reduced to make the distance between bars narrower

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))

    # Create the stacked bar chart
    bars_rendah = ax.barh(regions, rendah_val, color='#340900', edgecolor='white', height=bar_height, label='Rendah (%)')
    bars_menengah = ax.barh(regions, menengah_val, left=rendah_val, color='#eaff00', edgecolor='white', height=bar_height, label='Menengah (%)')
    bars_tinggi = ax.barh(regions, tinggi_val, left=rendah_val + menengah_val, color='#8bd48b', edgecolor='white', height=bar_height, label='Tinggi (%)')
    bars_sgt_tinggi = ax.barh(regions, sgt_tinggi_val, left=rendah_val + menengah_val + tinggi_val, color='#00450c', edgecolor='white', height=bar_height, label='Sangat Tinggi (%)')

    # Add text labels inside the bars
    for bars, text in zip([bars_rendah, bars_menengah, bars_tinggi, bars_sgt_tinggi], [rendah_text, menengah_text, tinggi_text, sgt_tinggi_text]):
        for bar, label in zip(bars, text):
            if label:  # Only add label if it's not an empty string
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, label, va='center', ha='center', fontsize=10, color='red', weight='bold')

    # Customize layout
    ax.set_xlabel('Persentase (%)', fontsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    legend = ax.legend(title='Kategori Curah Hujan', fontsize=14, title_fontsize=14, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=4)
    legend.get_frame().set_linewidth(0.0)  # Remove the legend box line
    legend.get_frame().set_edgecolor('none')  # Ensure no edge color

    # Remove gridlines and outline
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Set the background color
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Show the plot
    plt.tight_layout()
    
    output_file = os.path.join(folder_aset, 'chart','laporan', 'chart_laporan.png')
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close(fig)

def chart_laporan_sh(dataframe):
    folder_aset = os.getenv("ASSET")
    regions = dataframe['Wilayah']
    bawah_normal_val = dataframe['Bawah Normal (%)']
    normal_val = dataframe['Normal (%)']
    atas_normal_val = dataframe['Atas Normal (%)']
    threshold = 3.5  # threshold for bar label visibility

    # Add text label
    bawah_normal_text = [f'{val:.2f}%' if val >= threshold else '' for val in bawah_normal_val]
    normal_text = [f'{val:.2f}%' if val >= threshold else '' for val in normal_val]
    atas_normal_text = [f'{val:.2f}%' if val >= threshold else '' for val in atas_normal_val]

    bar_width = 0.8  # Width of the bars

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 10))

    # Create the stacked bar chart
    bars_bawah_normal = ax.barh(regions, bawah_normal_val, color='#340900', edgecolor='white', height=bar_width, label='Bawah Normal (%)')
    bars_normal = ax.barh(regions, normal_val, left=bawah_normal_val, color='#eaff00', edgecolor='white', height=bar_width, label='Normal (%)')
    bars_atas_normal = ax.barh(regions, atas_normal_val, left=bawah_normal_val + normal_val, color='#00450c', edgecolor='white', height=bar_width, label='Atas Normal (%)')

    # Add text labels inside the bars
    for bars, text in zip([bars_bawah_normal, bars_normal, bars_atas_normal], [bawah_normal_text, normal_text, atas_normal_text]):
        for bar, label in zip(bars, text):
            if label:  # Only add label if it's not an empty string
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_y() + bar.get_height() / 2, label, va='center', ha='center', fontsize=10, color='red', weight='bold')

    # Customize layout
    # ax.set_title('Persentase Kategori CH', fontsize=23, fontweight='bold', family='DejaVu Sans')
    ax.set_xlabel('Persentase (%)', fontsize=14)
    ax.tick_params(axis='x', labelsize=14)
    ax.tick_params(axis='y', labelsize=14)
    legend = ax.legend(title='Kategori Sifat Hujan', fontsize=14, title_fontsize=14, loc='upper center', bbox_to_anchor=(0.5, -0.1), ncol=3)
    legend.get_frame().set_linewidth(0.0)  # Remove the legend box line
    legend.get_frame().set_edgecolor('none') 

    # Set the background color
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Remove gridlines and outline
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # Show the plot
    plt.tight_layout()
    
    output_file = os.path.join(folder_aset, 'chart','laporan', 'chart_laporan.png')
    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1, transparent=True)
    plt.close(fig)

