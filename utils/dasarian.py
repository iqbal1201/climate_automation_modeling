'''
Script ini digunakan untuk mendapatkan jenis dasarian dari waktu berjalan saat script dijalankan
'''


from datetime import datetime


def get_current_dasarian(date):
    day = date.day

    if 1 <= day <= 10:
        dasarian = 1
        dasarian_txt = 'I'
    elif 11 <= day <= 20:
        dasarian = 2
        dasarian_txt = 'II'
    else:
        dasarian = 3
        dasarian_txt = 'III'
    return dasarian, dasarian_txt


# def get_current_dasarian_pseudo():
#     if 1 <= day <= 10:
#         dasarian = 3
#         dasarian_txt = 'III'
#     elif 11 <= day <= 20:
#         dasarian = 1
#         dasarian_txt = 'I'
#     elif 21 <= day <= 30:
#         dasarian = 2
#         dasarian_txt = 'II'
#     else:
#         dasarian = 3
#         dasarian_txt = 'III'
#     return dasarian, dasarian_txt