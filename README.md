# 4PSA-FreePBX-CDR-Generator
Automatically generate total calls &amp; duration for both FreePBX software and 4PSA VoIP Now for each agent combined

PBX and VAPRO Data Processing Script
====================================

Overview
--------

This script processes PBX and VAPRO call data, generates reports, and combines the data into a final report. The script performs the following tasks:

1.  Processes PBX call data.
2.  Processes VAPRO call data.
3.  Combines PBX and VAPRO call data.
4.  Generates a final combined report with call statistics.

Requirements
------------

*   Python 3.x
*   `pandas` library

You can install the required library using:

    pip install pandas

Files
-----

*   `pbx.csv`: Input file containing PBX call data.
*   `vapro.csv` and `mapro.csv`: Input files containing VAPRO and MAPRO call data.
*   `combined.csv`: Intermediate file combining `vapro.csv` and `mapro.csv`.
*   `xau.csv`: Output file for processed PBX call data.
*   `xvapro.csv`: Output file for processed VAPRO call data.
*   `talktime_tanggal_<date>.csv`: Final combined report file.

Configuration
-------------

### Constants

*   `START_TIME`: Start time for filtering calls (format: 'YYYY-MM-DD HH:MM:SS').
*   `END_TIME`: End time for filtering calls (format: 'YYYY-MM-DD HH:MM:SS').
*   `FILE_PATH_PBX`: Path to the PBX input file.
*   `FILE_PATH_VAPRO`: Path to the combined VAPRO and MAPRO input file.
*   `OUTPUT_FILE_PBX`: Output file for processed PBX data.
*   `OUTPUT_FILE_VAPRO`: Output file for processed VAPRO data.
*   `OUTPUT_FILE_COMBINED`: Base name for the final combined report file.

### Mappings

*   `CNAM_MAPPING`: Mapping of PBX caller names to standard names.
*   `NUMBER_TO_NAME`: Mapping of VAPRO numbers to standard names.

Script Execution
----------------

### Main Functions

*   `check_and_run_script(file_path, script_name)`: Checks if a file exists and runs a specified script if it does not.
*   `process_pbx_file(file_path, output_file)`: Processes the PBX input file, filters data, and generates a summary report.
*   `process_vapro_file(file_path, output_file)`: Processes the VAPRO input file, filters data, and generates a summary report.
*   `combine_and_clean_csv(file1, file2, output_file)`: Combines `vapro.csv` and `mapro.csv` into a single file, cleans the data, and sorts it.
*   `main()`: Main function that orchestrates the processing of PBX and VAPRO data and generates the final report.

### Execution Flow

1.  The script checks if the combined VAPRO file (`combined.csv`) exists. If not, it combines `vapro.csv` and `mapro.csv`.
2.  It processes the PBX file and generates a summary report (`xau.csv`).
3.  It processes the VAPRO file and generates a summary report (`xvapro.csv`).
4.  It combines the processed PBX and VAPRO data into a final report (`talktime_tanggal_<date>.csv`).

### Running the Script

To execute the script, run:

    python script_name.py

Replace `script_name.py` with the actual name of your script file.

Logging
-------

The script uses Python's logging module to log informational messages during its execution. The logs include timestamps and log levels for better traceability.

Example Output
--------------

The final combined report (`talktime_tanggal_<date>.csv`) contains the following columns:

*   `Caller ID`
*   `Total Calls`
*   `Total Talking Time`
*   `First Call Time`
*   `Last Call Time`

The report is sorted by `Caller ID` and provides a comprehensive view of call activities within the specified time frame.

Notes
-----

*   Ensure the input files are in the correct format and located in the specified paths.
*   Modify the constants and mappings as needed to fit your data and requirements.

For any issues or further customization, please refer to the script and adjust the logic as necessary.
