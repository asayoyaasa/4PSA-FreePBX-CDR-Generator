import os
import pandas as pd
import subprocess
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
START_TIME = '2024-05-23 11:00:00'
END_TIME = '2024-05-23 23:59:00'
FILE_PATH_PBX = 'pbx.csv' 
FILE_PATH_VAPRO = 'combined.csv'
OUTPUT_FILE_PBX = 'xau.csv'
OUTPUT_FILE_VAPRO = 'xvapro.csv'
OUTPUT_FILE_COMBINED = 'talktime'

# Mapping for PBX
CNAM_MAPPING = {
    "CNAME": "AGENT NAME", 
}

# Mapping for VAPRO & MAPRO
NUMBER_TO_NAME = {
    "EXT NUM": "AGENT NAME", 
}

def check_and_run_script(file_path, script_name):
    if not os.path.exists(file_path):
        subprocess.run(["python", script_name], check=True)
        logging.info(f"{script_name} script executed")

def process_pbx_file(file_path, output_file):
    if os.path.exists(file_path):
        df_pbx = pd.read_csv(file_path)
        df_pbx['calldate'] = pd.to_datetime(df_pbx['calldate'])
        df_pbx['cnam'] = df_pbx['cnam'].map(CNAM_MAPPING)
        filtered_df_pbx = df_pbx[(df_pbx['calldate'] >= START_TIME) & (df_pbx['calldate'] <= END_TIME)]
        filtered_df_pbx = filtered_df_pbx[(filtered_df_pbx['dst'].astype(str).apply(len).isin([11, 12]))]
        grouped_data_pbx = filtered_df_pbx.groupby('cnam').agg({
            'dst': 'count',
            'billsec': 'sum',
            'calldate': ['min', 'max']
        }).reset_index()
        grouped_data_pbx.columns = ['Caller Name', 'Total Calls', 'Total Billsec (HH:MM:SS)', 'First Call Timestamp', 'Last Call Timestamp']
        grouped_data_pbx['Total Billsec (HH:MM:SS)'] = pd.to_timedelta(grouped_data_pbx['Total Billsec (HH:MM:SS)'], unit='s')
        grouped_data_pbx['Total Billsec (HH:MM:SS)'] = grouped_data_pbx['Total Billsec (HH:MM:SS)'].apply(
            lambda x: f"{x.days * 24 + x.seconds // 3600:02}:{(x.seconds // 60) % 60:02}:{x.seconds % 60:02}")
        grouped_data_pbx.to_csv(output_file, index=False)
        logging.info("PBX REPORT DONE")

def process_vapro_file(file_path, output_file):
    if os.path.exists(file_path):
        df_vapro = pd.read_csv(file_path)
        df_vapro['From number'] = df_vapro['From number'].map(NUMBER_TO_NAME)
        df_vapro['Call initiated'] = pd.to_datetime(df_vapro['Call initiated'])
        filtered_df_vapro = df_vapro[(df_vapro['Call initiated'] >= START_TIME) & (df_vapro['Call initiated'] <= END_TIME)]
        filtered_df_vapro = filtered_df_vapro[(filtered_df_vapro['To number'].astype(str).apply(len).isin([11, 12]))]
        grouped_data_vapro = filtered_df_vapro.groupby('From number').agg({
            'Call initiated': ['count', 'min', 'max'],
            'Call duration': 'sum'
        }).reset_index()
        grouped_data_vapro.columns = ['From Number', 'Total Calls', 'First Call Timestamp', 'Last Call Timestamp', 'Total Call Duration (HH:MM:SS)']
        grouped_data_vapro['Total Call Duration (HH:MM:SS)'] = pd.to_timedelta(grouped_data_vapro['Total Call Duration (HH:MM:SS)'], unit='s')
        grouped_data_vapro['Total Call Duration (HH:MM:SS)'] = grouped_data_vapro['Total Call Duration (HH:MM:SS)'].apply(
            lambda x: f"{x.days * 24 + x.seconds // 3600:02}:{(x.seconds // 60) % 60:02}:{x.seconds % 60:02}")
        grouped_data_vapro.to_csv(output_file, index=False)
        logging.info("VAPRO REPORT DONE")

def combine_and_clean_csv(file1, file2, output_file):
    # Read CSV files without headers, treating the first row as data
    df1 = pd.read_csv(file1, header=None)
    df2 = pd.read_csv(file2, header=None)

    # Drop the first row of df2, which is assumed to be the header
    df2 = df2.drop(0).reset_index(drop=True)

    # Combine the two DataFrames
    combined_df = pd.concat([df1, df2], ignore_index=True)

    # Sort by the third column (index 2) in descending order
    combined_df.sort_values(by=2, ascending=False, inplace=True)

    # Remove rows where the third column (index 2) is '0000-00-00 00:00:00'
    combined_df = combined_df[combined_df[2] != '0000-00-00 00:00:00']

    # Write the combined DataFrame to a new CSV file without headers
    combined_df.to_csv(output_file, index=False, header=False)

def main():
    # Check and run VAPRO combiner script
    if not os.path.exists(FILE_PATH_VAPRO):
        combine_and_clean_csv("vapro.csv", "mapro.csv", FILE_PATH_VAPRO)
        logging.info("VAPRO combiner script executed")

    # Process PBX file
    process_pbx_file(FILE_PATH_PBX, OUTPUT_FILE_PBX)

    # Process VAPRO file
    process_vapro_file(FILE_PATH_VAPRO, OUTPUT_FILE_VAPRO)

    # Read data from CSV files
    df_pbx = pd.read_csv('xau.csv')
    df_vapro = pd.read_csv('xvapro.csv')

    # Reorder and select columns for each dataframe
    df_pbx = df_pbx[['Caller Name', 'Total Calls', 'Total Billsec (HH:MM:SS)', 'First Call Timestamp', 'Last Call Timestamp']]
    df_vapro = df_vapro[['From Number', 'Total Calls', 'Total Call Duration (HH:MM:SS)', 'First Call Timestamp', 'Last Call Timestamp']]

    # Rename columns to match the desired output
    df_pbx.columns = ['Caller ID', 'Total Calls', 'Total Talking Time', 'First Call Time', 'Last Call Time']
    df_vapro.columns = ['Caller ID', 'Total Calls', 'Total Talking Time', 'First Call Time', 'Last Call Time']

    # Concatenate dataframes
    combined_df = pd.concat([df_vapro, df_pbx], ignore_index=True)

    # Convert 'Total Talking Time' to timedelta and sum for duplicate 'Caller ID'
    combined_df['Total Talking Time'] = pd.to_timedelta(combined_df['Total Talking Time']).groupby(combined_df['Caller ID']).transform('sum')

    # Combine 'Total Calls' for duplicate 'Caller ID'
    combined_df['Total Calls'] = combined_df.groupby('Caller ID')['Total Calls'].transform('sum')

    # Format 'Total Talking Time' to HH:MM:SS
    combined_df['Total Talking Time'] = combined_df['Total Talking Time'].apply(lambda x: str(x).split()[-1])

    # Aggregate 'First Call Time' and 'Last Call Time' based on your requirements
    combined_df['First Call Time'] = combined_df.groupby('Caller ID')['First Call Time'].transform('min')
    combined_df['Last Call Time'] = combined_df.groupby('Caller ID')['Last Call Time'].transform('max')

    # Drop duplicate 'Caller ID' entries
    combined_df = combined_df.drop_duplicates(subset='Caller ID')

    # Sort the dataframe based on 'Caller ID'
    combined_df = combined_df.sort_values(by='Caller ID').reset_index(drop=True)

    # Save the combined dataframe to a CSV file with dynamic filename
    modified_start_time = START_TIME[8:10] + " " + START_TIME[11:].replace(':', '_')
    combined_df.to_csv(f"{OUTPUT_FILE_COMBINED}_tanggal_{modified_start_time}.csv", index=False)

    # Print the combined dataframe
    print(combined_df)

if __name__ == "__main__":
    main()
