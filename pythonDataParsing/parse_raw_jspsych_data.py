from collections import defaultdict
import pandas as pd
from pathlib import Path
import numpy as np
import zipfile
import json
import warnings
import datetime


# Define variables
ZIP_PATH = "osfstorage-archive.zip" # path to the zip file containing the raw data
OUTPUT_NAME = "test" # creates folder with this name and saves output CSVs inside

INCREMENT = 1.0 # in seconds, time video interval for long format data (default = 1.0) 
VIDEO_START_TIME = 0 # in seconds, for long format data (default = 0)
VIDEO_END_TIME = 2.0 # in seconds, for long format data
DEFAULT_NONE_VALUE = -1 # default value for missing responses in long format data (default = -1)


def merge_if_list(value):
    return ','.join(str(x) for x in value) if isinstance(value, list) else value

def create_long_format(response, video_time, pid):
    times = np.arange(start=VIDEO_START_TIME, stop=VIDEO_END_TIME, step=INCREMENT)

    # Initialize a DataFrame with times as columns
    df = pd.DataFrame(columns=times)

    # Function to round down to the nearest increment
    def round_down_to_increment(value, increment):
        return np.floor(value / increment) * increment

    # Record the responses in the DataFrame
    recorded_responses = {}
    for vt, resp in zip(video_time, response):
        # Round to the nearest increment less than or equal to the video_time
        rounded_time = round_down_to_increment(vt, INCREMENT)
        # Only insert the response if this is the first response for that time
        if rounded_time not in recorded_responses:
            recorded_responses[rounded_time] = resp
    
    # Insert the recorded responses into the DataFrame
    for time in times:
        if time in recorded_responses:
            # Insert the response for the time
            df.loc[0, time] = recorded_responses[time]
        else:
            # If no response for this time, fill with NaN for now
            df.loc[0, time] = np.nan

    # Forward-fill the missing values with the last valid response
    df.ffill(axis=1, inplace=True)
    df = df.fillna(DEFAULT_NONE_VALUE)
    df.insert(0, column='PID', value=pid)

    return df


def from_json_to_dataframe(zip_path):
    # Create an empty DataFrame to store the extracted data
    short_format_data = defaultdict(list)
    long_format_data = []

            # Iterate over each JSON file in the folder
    if zipfile.is_zipfile(zip_path):
        with zipfile.ZipFile(zip_path, mode="r")as zip_file:
            # Iterate over each JSON file in the zip archive
            for filename in zip_file.namelist():
                with zip_file.open(filename) as json_file:
                    # Load the JSON data
                    json_file = json.load(json_file)
                    if("trials" not in json_file):
                        warnings.warn("Skipping" + filename + " as it does not have any trials.")
                        continue
                        
                    # Parse the data for each trial
                    parse_trial_data(filename, json_file, short_format_data, long_format_data)
    else:
        for file_path in zip_path.glob("*.json"):
            with open(file_path) as json_file:
                # Load the JSON data
                json_file = json.load(json_file)
                if("trials" not in json_file):
                    warnings.warn("Skipping" + filename + " as it does not have any trials.")
                    continue
                    
                # Parse the data for each trial
                parse_trial_data(filename, json_file, short_format_data, long_format_data)
    
    # Merge data into a DataFrame
    df = pd.DataFrame(short_format_data)
    df_long_format = pd.concat(long_format_data)
    
    return df, df_long_format

def save_df_to_csv(df, file_path):
    # If the file already exists, warn the user that it will be overwritten
    if file_path.exists():
        warnings.warn(str(file_path.stem) + " already exists and will be overwritten.")
    
    df.to_csv(file_path, index=False)

def parse_trial_data(filename, json_file, short_format_data, long_format_data):
        # Strip file extension from filename and convert it to date
    date = datetime.datetime.strptime(filename[:-5], "%Y%m%d%H%M%S")
    # Add metadata
    short_format_data["date"].append(date)
    short_format_data["PID"].append(json_file["PID"])
    short_format_data["STUDY_ID"].append(json_file["STUDY_ID"])

    # Add results of each trial
    for trial in json_file["trials"]:
        if("response" not in trial):
            continue
        short_format_data[merge_if_list(trial["stimulus"])].append(merge_if_list(trial["response"]))
        
        # Handle specific trials
        match trial["trial_type"]:
            case "video-several-keyboard-responses":
                long_format_data.append(create_long_format(trial["response"], trial["video_time"], json_file["PID"]))
            case _:
                continue

def main():
    short_df, long_df = from_json_to_dataframe(ZIP_PATH)

    # Check if the folder exists, if not, create it
    output_folder = Path.cwd() / OUTPUT_NAME
    if not output_folder.exists():
        output_folder.mkdir()

    save_df_to_csv(short_df, output_folder / (OUTPUT_NAME + ".csv"))
    save_df_to_csv(long_df, output_folder / (OUTPUT_NAME + "_long.csv"))

if __name__ == "__main__":
    main()