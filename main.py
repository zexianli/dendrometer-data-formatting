import pandas as pd

# Read data
data = pd.read_csv("data/18/dend00modified.csv", header=[0, 1])

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

print(data.head(5))

data["Change"] = data[('AS5311', 'Serial_Value')].diff()
print(data.dtypes)

newData = pd.DataFrame()
toRemove = []
prevIdx, prevSerial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
# print(prevIdx, prevSerial)
# print(newData)

# Durring itertuples iteration, _9 is the name for Serial_Value
# data.loc[1:] returns a copy of the data starting at index 1
for row in data.loc[1:15].itertuples():
    curIdx = getattr(row, "Index")
    curSerial = getattr(row, "_9")

    # print(prevSerial, curSerial)
    # Wrap up
    if prevSerial > 3950 and curSerial < 200:
        print("-- Wrapped up")
        # Wrap down
    elif prevSerial < 250 and curSerial > (4096 - 250):
        print("-- Wrapped down")

    # print(curIdx, curSerial)
    elif abs(curSerial - prevSerial) > 500:
        # print(curSerial, prevSerial)
        toRemove.append(curIdx)

    # print(
    #     f"Updating idx and values. Old: {prevIdx}, {prevSerial}. New: {curIdx}, {curSerial}")
    prevIdx, prevSerial = curIdx, curSerial
# print(toRemove)
# data.drop(toRemove, inplace=True)
# data.reset_index(drop=True, inplace=True)
# print(data.iloc[500:550])
