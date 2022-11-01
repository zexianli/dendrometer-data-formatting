import pandas as pd
import matplotlib.pyplot as plt

# Read data
df = pd.read_csv("data/17/dend000.csv", header=[0, 1])

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

"""
Remove entries where the change in displacement is greater or equal to 500
"""
toRemove = []
prevIdx, prevSerial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
curIdx, serialBeforeUpdate = 1, None
while curIdx < data.shape[0]:
    curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]

    if serialBeforeUpdate != None:
        prevSerial = serialBeforeUpdate
        serialBeforeUpdate = None

    if curIdx == 5467:
        print(prevSerial, curSerial)

        # Wrap up
    if prevSerial > 3500 and curSerial < 200:
        print("-- Wrapped up", prevSerial, curSerial)
        wrap += 4095
    # Wrap down
    elif prevSerial < 250 and curSerial > (4096 - 250):
        print("-- Wrapped down", prevSerial, curSerial)
        wrap -= 4095

    # Calculate the displacement data
    curCalcSerial = prevSerial + wrap - initial
    data.at[curIdx, 'Calculated'] = curCalcSerial

    """
    We place a pointer at the current row and start the loop.
    The loop will keep going until it finds a displacement that is relatively close to the refence.

    This could be changed to number of entries we remove before backing out
    since the data is collected every ~15 minutes
    """
    if abs(curSerial - prevSerial) > 350:
        data.at[curIdx, ('AS5311', 'Serial_Value')
                ] = curCalcSerial - wrap + initial

        if curIdx in [5465, 5466, 5467]:
            print(data.iloc[curIdx][('AS5311', 'Serial_Value')])

        # Update curSerial so we don't roll over this old value to next row
        # if curIdx + 1 < data.shape[0]:
        #     serialBeforeUpdate = curSerial
        #     curSerial = data.iloc[curIdx +
        #                           1][('AS5311', 'Serial_Value')]

    prevSerial = curSerial

    curIdx += 1


print(data.iloc[5462:5470])
# data.drop(toRemove, inplace=True)
# data.reset_index(drop=True, inplace=True)
# print(
#     f"-- Removed {len(toRemove)} rows where data spiked.")


# Durring itertuples iteration, _9 is the name for Serial_Value
# data.loc[1:] returns a copy of the data starting at index 1

# initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
# prevSerial = data.iloc[0][('AS5311', 'Serial_Value')]
# data.at[0, 'Calculated'] = 0
# ROWS = data.loc[1:].itertuples()
# for row in ROWS:
#     curIdx = getattr(row, "Index")
#     curSerial = getattr(row, "_9")

#     # Wrap up
#     if prevSerial > 3950 and curSerial < 200:
#         print("-- Wrapped up", prevSerial, curSerial)
#         wrap += 4095
#     # Wrap down
#     elif prevSerial < 250 and curSerial > (4096 - 250):
#         print("-- Wrapped down", prevSerial, curSerial)
#         wrap -= 4095

#     # Calculate the displacement data
#     data.at[curIdx, 'Calculated'] = curSerial + wrap - initial

#     prevSerial = curSerial

# Create a new column and fill with displacement from previous row to this row.
data["Change"] = data[('AS5311', 'Serial_Value')].diff()

# Plot stuff
fig1 = plt.subplot()
fig1.plot(data['Calculated'])
fig1.plot(df[('AS5311', 'Serial_Value')])
fig1.legend(['Calculated', 'Raw'])
fig1.set_xlabel("Time")
fig1.set_ylabel("Displacement")
fig1.set_xticklabels([])
plt.show()
plt.close()


fig2 = plt.subplot()
fig2.hist(data['Change'], bins=100)
plt.xlim([-75, 75])
plt.yscale('log')

plt.show()
