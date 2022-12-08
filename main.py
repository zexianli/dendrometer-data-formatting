import pandas as pd
import matplotlib.pyplot as plt

pd.options.display.max_rows = 200


# Read data
df = pd.read_csv("data/28/dend00.csv", header=[0, 1])

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

data = df.copy(deep=True)

toRemove = []
prev_idx, prev_serial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
initial, calculated, wrap = data.iloc[0][('AS5311', 'Serial_Value')], 0, 0
data.at[0, 'Calculated'] = 0

cur_idx = 1
while cur_idx < data.shape[0]:
    cur_serial = data.iloc[cur_idx][('AS5311', 'Serial_Value')]

    change = (cur_serial - prev_serial)/(cur_idx - prev_idx)
    data.at[cur_idx, 'Change'] = change

    calculated_serial_data = prev_serial + wrap - initial

    if abs(change) > 2000:
        # Wrap up
        if change < 0:
            print("-- Wrapped up", prev_serial, cur_serial, change)
            wrap += 4095

        # Wrap down
        elif change > 0:
            print("-- Wrapped down", prev_serial, cur_serial, change)
            wrap -= 4095

        # Calculate the displacement data
        calculated_serial_data = cur_serial + wrap - initial

    # Data to use in the plot
    data.at[cur_idx, 'Calculated'] = calculated_serial_data

    prev_serial = cur_serial
    prev_idx = cur_idx
    cur_idx += 1

# Plot stuff
fig1 = plt.subplot()
fig1.set_title("Dendrometer #1")
fig1.plot(df["Time"], df[('AS5311', 'Serial_Value')])
fig1.plot(data["Time"], data['Calculated'])
fig1.legend(['Raw data', 'Over/Under flow adjusted'])
fig1.set_xlabel("Time")
fig1.set_ylabel("Displacement (serial value)")
# fig1.set_xticklabels([])
plt.show()
