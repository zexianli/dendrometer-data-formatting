from operator import index
from time import process_time_ns
import pandas as pd

# Read data
data = pd.read_csv("data/18/dend00.csv", header=[0, 1])

# Change column names
data = data.rename(
    columns={'Unnamed: 1_level_0': 'ID', 'Unnamed: 3_level_0': 'Timestamp', 'Unnamed: 7_level_0': 'SHT31D'})

# Drop last column (it is empty)
data = data.iloc[:, :-1]

# Drop rows where button was pressed
idxBtnPressed = data[data[('Button', 'Pressed?')] == 1].index
data.drop(idxBtnPressed, inplace=True)
data.reset_index(drop=True, inplace=True)
print(f"-- Dropped {idxBtnPressed.shape[0]} rows where button was pressed.")

# Drop rows where status color was neither green nor yellow.
idxColorStatus = data[(data[('Status', 'Color')] != "Green") &
                      (data[('Status', 'Color')] != "Yellow")].index
data.drop(idxColorStatus, inplace=True)
data.reset_index(drop=True, inplace=True)
print(
    f"-- Dropped {idxColorStatus.shape[0]} rows where status color was neither green nor yellow.")
