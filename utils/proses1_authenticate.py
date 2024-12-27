'''
Script ini digunakan untuk autentikasi ke file server dalam menyimpan output dari Proses I
'''

# def authenticate():
# # Map the network drive
#     subprocess.run(['net', 'use', r'\\192.168.27.19\data_bmkg', '/user:Administrator', '4rcG!$1kl1m2024'])
import os
import subprocess

def map_network_drive(network_path, username, password):
    try:
        # Attempt to map the network drive
        result = subprocess.run(['net', 'use', network_path, f'/user:{username}', password], check=True, capture_output=True)
        print(f"Successfully connected to {network_path}")

    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to {network_path}: {e.stderr.decode()}")
    except FileNotFoundError:
        print(f"The specified network path was not found: {network_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Replace these variables with your actual values
