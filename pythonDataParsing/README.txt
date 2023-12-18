# Parse raw data from jspsych using python

Takes in a path to zipped (or unzipped) folder that contains .json files from jspsych library and saves the data to two .csv file: short version containing all results and long version with the data only from video responses

## Installation

1. Download and install [python](https://www.python.org/downloads/). Tested with Python 3.12.0
2. In console go into this folder and run `pip install -r requirements.txt` to install other requirements needed to run the code

## Run
1. Open `parse_raw_jspsych_data.py` and edit parameters at the start of the file, especially ZIP_PATH that takes in the path to the folder containing .json files
2. In a console run `python parse_raw_jspsych_data.py` inside the same folder as the file


