import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.max_rows = 200


# Read data
df = pd.read_csv("data/18/dend00.csv", header=[0, 1])

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

print(data.iloc[960:1100][('AS5311', 'Serial_Value')])

# print(data.head)

"""
Remove entries where the change in displacement is greater or equal to
"""
toRemove = []
prevIdx, prevSerial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
out_of_while = 0
curIdx = 1
while curIdx < data.shape[0]:
    curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]

    change = (curSerial - prevSerial)/(curIdx - prevIdx)
    data.at[curIdx, 'Change'] = change

    if abs(change) > 3800:
        # Wrap up
        if change < 0:
            # print("-- Wrapped up", prevSerial, curSerial, change)
            wrap += 4095

        # Wrap down
        elif change > 0:
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
    while abs(change) >= 250 and curIdx + 1 < data.shape[0] and overrides < 100:
        # # data.at[curIdx, ('AS5311', 'Serial_Value')] = prevSerial
        # # data.at[curIdx, ('Change')] = 0

        # # Calculate the displacement data
        # curCalcSerial = prevSerial + wrap - initial
        # data.at[curIdx, 'Calculated'] = curCalcSerial

        # -------------
        data.at[curIdx, ('AS5311', 'Serial_Value')] = prevSerial
        prevCalculated = float(data.iloc[prevIdx][('Calculated')])
        # if curIdx > 960 and curIdx < 1000:
        #     print(prevCalculated)
        data.at[curIdx, ('Calculated')] = prevCalculated

        # curCalcSerial = prevSerial + wrap - initial

        # data.at[curIdx, 'Calculated'] = curCalcSerial
        # -------------

        toRemove.append(curIdx)

        curIdx = curIdx + 1
        overrides += 1
        curSerial = data.iloc[curIdx][('AS5311', 'Serial_Value')]

        change = (curSerial - prevSerial)

    if abs(change) < 250:
        data.at[curIdx, ('Change')] = change

    # Calculate the displacement data
    curCalcSerial = prevSerial + wrap - initial

    # Data to use in the plot
    data.at[curIdx, 'Calculated'] = curCalcSerial
    prevSerial = curSerial
    prevIdx = curIdx
    curIdx += 1

print(toRemove)
print(data.iloc[960:1100][('AS5311', 'Serial_Value')],
      data.iloc[960:1100][('Calculated')])
# print(data.iloc[500:540][('AS5311', 'Serial_Value')], "\n",
#       data.iloc[500:540][('Change')])
# print(data.head(10))

# Plot stuff
fig1 = plt.subplot()
fig1.plot(data["Time"], data['Calculated'])
fig1.plot(df["Time"], df[('AS5311', 'Serial_Value')])
fig1.legend(['Calculated', 'Raw'])
fig1.set_xlabel("Time")
fig1.set_ylabel("Displacement")
# fig1.set_xticklabels([])
plt.show()
plt.close()


# fig2 = plt.subplot()
# fig2.hist(data['Change'], bins=100)
# plt.xlim([-500, 500])
# plt.yscale('log')
# plt.show()
