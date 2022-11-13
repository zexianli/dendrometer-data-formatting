import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data/18/dend00modified.csv", header=[0, 1])

# Change column names
df = df.rename(
    columns={'Unnamed: 1_level_0': 'ID', 'Unnamed: 3_level_0': 'Timestamp', 'Unnamed: 7_level_0': 'SHT31D'})

# Drop last column (it is empty)
df = df.iloc[:, :-1]

# Drop rows where button was pressed
idxBtnPressed = df[df[('Button', 'Pressed?')] == 1].index
df.drop(idxBtnPressed, inplace=True)
df.reset_index(drop=True, inplace=True)
print(f"-- Dropped {idxBtnPressed.shape[0]} rows where button was pressed.")

# Drop rows where status color was neither green nor yellow.
idxColorStatus = df[(df[('Status', 'Color')] != "Green") &
                    (df[('Status', 'Color')] != "Yellow")].index
df.drop(idxColorStatus, inplace=True)
df.reset_index(drop=True, inplace=True)
print(
    f"-- Dropped {idxColorStatus.shape[0]} rows where status color was neither green nor yellow.")


data = df.copy(deep=True)
# print(data.iloc[500:520])

"""
Remove entries where the change in displacement is greater or equal to 350
"""
toRemove = []
prevIdx, prevSerial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
curIdx = 1
while curIdx < data.shape[0]:
    curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]

    change = abs((curSerial - prevSerial)/(curIdx - prevIdx))
    data.at[curIdx, 'Change'] = change

    # if (prevSerial > 3500 and curSerial < 200) or (prevSerial < 250 and curSerial > (4096 - 250)):
    if change < 200 or change > 3800:

        # Wrap up
        if prevSerial > 3500 and curSerial < 200:
            # print("-- Wrapped up", prevSerial, curSerial, change)
            wrap += 4095

        # Wrap down
        elif prevSerial < 250 and curSerial > (4096 - 250):
            # print("-- Wrapped down", prevSerial, curSerial, change)
            wrap -= 4095

        # Calculate the displacement data
        curCalcSerial = curSerial + wrap - initial

        # Data to use in the plot
        data.at[curIdx, 'Calculated'] = curCalcSerial

        prevSerial = curSerial
        prevIdx = curIdx
        curIdx += 1
        continue

    """
    We place a pointer at the current row and start the loop.
    The loop will keep going until it finds a displacement that is relatively close to the refence.

    This could be changed to number of entries we remove before backing out
    since the data is collected every ~15 minutes
    """
    overrides = 0
    while change >= 200 and change <= 3800 and curIdx + 1 < data.shape[0] and overrides < 25:

        # Should update current row with the values of the previous row.
        data.at[curIdx, ('AS5311', 'Serial_Value')] = prevSerial

        # TODO: Need to fix the 'Calculated' column.
        # Serial data is keeping the previous value during spikes
        # But Calculated value is showing as NaN

        curIdx += 1
        curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]
        overrides += 1

    # Calculate the displacement data
    curCalcSerial = prevSerial + wrap - initial

    # Data to use in the plot
    data.at[curIdx, 'Calculated'] = curCalcSerial
    prevSerial = curSerial
    prevIdx = curIdx
    curIdx += 1


print(data.iloc[500:550])
# print(data.head(10))

# Create a new column and fill with displacement from previous row to this row.
# data["Change"] = data[('AS5311', 'Serial_Value')].diff()

# Plot stuff
fig1 = plt.subplot()
fig1.plot(data['Calculated'])
fig1.plot(data[('AS5311', 'Serial_Value')])
fig1.plot(df[('AS5311', 'Serial_Value')])
fig1.legend(['Calculated',  'Calculated raw', 'Raw'])
fig1.set_xlabel("Time")
fig1.set_ylabel("Displacement")
fig1.set_xticklabels([])
plt.show()
plt.close()


# fig2 = plt.subplot()
# fig2.hist(data['Change'], bins=100)
# plt.xlim([-500, 500])
# plt.yscale('log')
# plt.show()
