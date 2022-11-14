import pandas as pd
import matplotlib.pyplot as plt


class Formatter(object):
    _lower_bound = 3800
    _upper_bound = 200
    _overrides = 25

    def __init__(self, filename):
        """
        self.df:    Data read from csv
        self.data:  Data without rows where buttong was pressed or color status
        """

        # Read data
        self.df = pd.read_csv(filename, header=[0, 1])

        # Change column names
        self.df = self.df.rename(columns={'Unnamed: 1_level_0': 'ID',
                                          'Unnamed: 3_level_0': 'Timestamp',
                                          'Unnamed: 7_level_0': 'SHT31D'})

        # Drop last column (it is empty)
        self.df = self.df.iloc[:, :-1]

        # Drop rows where button was pressed
        idxBtnPressed = self.df[self.df[('Button', 'Pressed?')] == 1].index
        self.df.drop(idxBtnPressed, inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        # Drop rows where status color was neither green nor yellow.
        idxColorStatus = self.df[(self.df[('Status', 'Color')] != "Green") &
                                 (self.df[('Status', 'Color')] != "Yellow")].index
        self.df.drop(idxColorStatus, inplace=True)
        self.df.reset_index(drop=True, inplace=True)

        # self.data = self.df.copy(deep=True)

    def format(self, lower_bound=200, upper_bound=3800, max_overrides=25):
        """
        Remove entries where the change in displacement is greater or equal to 350
        """

        self.data = self.clean_sheet()

        prevIdx, prevSerial = 0, self.data.iloc[0][('AS5311', 'Serial_Value')]
        initial, wrap = self.data.iloc[0][('AS5311', 'Serial_Value')], 0
        curIdx = 1
        while curIdx < self.data.shape[0]:
            curSerial = self.data.iloc[curIdx][('AS5311', 'Serial_Value')]

            change = abs((curSerial - prevSerial)/(curIdx - prevIdx))
            self.data.at[curIdx, 'Change'] = change

            # if (prevSerial > 3500 and curSerial < 200) or (prevSerial < 250 and curSerial > (4096 - 250)):
            if change < lower_bound or change > upper_bound:

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
                self.data.at[curIdx, 'Calculated'] = curCalcSerial

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
            while change >= lower_bound and change <= upper_bound and curIdx + 1 < self.data.shape[0] and overrides < max_overrides:

                # Should update current row with the values of the previous row.
                self.data.at[curIdx, ('AS5311', 'Serial_Value')] = prevSerial

                # TODO: Need to fix the 'Calculated' column.
                # Serial data is keeping the previous value during spikes
                # But Calculated value is showing as NaN

                curIdx += 1
                curSerial = self.data.iloc[curIdx][('AS5311', 'Serial_Value')]
                overrides += 1

            # Calculate the displacement data
            curCalcSerial = prevSerial + wrap - initial

            # Data to use in the plot
            self.data.at[curIdx, 'Calculated'] = curCalcSerial
            prevSerial = curSerial
            prevIdx = curIdx
            curIdx += 1

    def clean_sheet(self):
        return self.df.copy(deep=True)

    def plot(self):
        fig1 = plt.subplot()
        fig1.plot(self.data['Calculated'])
        fig1.plot(self.data[('AS5311', 'Serial_Value')])
        fig1.plot(self.df[('AS5311', 'Serial_Value')])
        fig1.legend(['Calculated',  'Calculated raw', 'Raw'])
        fig1.set_xlabel("Time")
        fig1.set_ylabel("Displacement")
        fig1.set_xticklabels([])
        plt.show()
