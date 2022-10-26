import pandas as pd

# Read data
data = pd.read_csv("data/17/dend000.csv", header=[0, 1])

# Change column names
data = data.rename(
    columns={'Unnamed: 1_level_0': 'ID', 'Unnamed: 3_level_0': 'Timestamp', 'Unnamed: 7_level_0': 'SHT31D'})

# Drop last column
data = data.iloc[:, :-1]


print(data.head())


indexesToDrop = data[data[('Button', 'Pressed?')] == 1].index
print(indexesToDrop)
data = data.drop(indexesToDrop, inplace=True)


print(data)
