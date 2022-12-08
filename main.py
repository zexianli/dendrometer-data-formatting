import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.max_rows = 200


# Read data
df = pd.read_csv("data/18/dend00modified.csv", header=[0, 1])

# Change column names
df = df.rename(
    columns={'Unnamed: 1_level_0': 'ID', 'Unnamed: 3_level_0': 'Timestamp', 'Unnamed: 7_level_0': 'SHT31D'})

# Drop last column (it is empty)
df = df.iloc[:, :-1]

# print(df.head())
date_time_combined = pd.to_datetime(
    df[("Timestamp", "date")] + ' ' + df[("Timestamp", "time")])
df.drop(columns=[("Timestamp", "date"), ("Timestamp", "time")], inplace=True)
df.insert(2, "Time", date_time_combined)

original = df.copy(deep=True)

# # Drop rows where button was pressed
# idxBtnPressed = df[df[('Button', 'Pressed?')] == 1].index
# df.drop(idxBtnPressed, inplace=True)
# print(f"-- Dropped {idxBtnPressed.shape[0]} rows where button was pressed.")

# # Drop rows where status color was neither green nor yellow.
# idxColorStatus = df[(df[('Status', 'Color')] != "Green") &
#                     (df[('Status', 'Color')] != "Yellow")].index
# df.drop(idxColorStatus, inplace=True)
# print(
#     f"-- Dropped {idxColorStatus.shape[0]} rows where status color was neither green nor yellow.")

# df.reset_index(drop=True, inplace=True)
data = df.copy(deep=True)

toRemove = []
prevIdx, prevSerial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
data.at[0, 'Calculated'] = 0

curIdx = 1
while curIdx < data.shape[0]:
    curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]

    change = (curSerial - prevSerial)/(curIdx - prevIdx)
    data.at[curIdx, 'Change'] = change

    curCalcSerial = prevSerial + wrap - initial

    if abs(change) > 3800:
        # Wrap up
        if change < 0:
            print("-- Wrapped up", prevSerial, curSerial, change)
            wrap += 4095

        # Wrap down
        elif change > 0:
            print("-- Wrapped down", prevSerial, curSerial, change)
            wrap -= 4095

        # Calculate the displacement data
        curCalcSerial = curSerial + wrap - initial

    # Data to use in the plot
    data.at[curIdx, 'Calculated'] = curCalcSerial

    prevSerial = curSerial
    prevIdx = curIdx
    curIdx += 1

# Plot stuff
fig1 = plt.subplot()
fig1.plot(df["Time"], df[('AS5311', 'Serial_Value')])
fig1.plot(data["Time"], data['Calculated'])
# fig1.legend(['Original', 'Simple clean', 'Calculated'])
fig1.legend(['Simple clean', 'Calculated'])
fig1.set_xlabel("Time")
fig1.set_ylabel("Displacement")
# fig1.set_xticklabels([])
plt.show()
plt.close()
