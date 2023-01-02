import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
import linecache


class DataFormatter:
    def __init__(self) -> None:
        self.time_offset = 0
        print("Constructor")

    def find_valid_files(self, min_file_size: int = 1000000) -> dict:
        """
        Find the valid data files inside the data folder

        min_file_size -- the minimum valid size for a file in bytes (default 1000000 bytes)
        """

        cur_path = Path.cwd()
        data_path = Path.joinpath(cur_path, "data")
        folders = [folder for folder in data_path.iterdir() if folder.is_dir()]
        folder_file_map = defaultdict(list)

        for folder in folders:
            files_path = Path.joinpath(data_path, folder)
            files = [file for file in Path(files_path).glob("*.csv")]

            for file in files:
                file_size = Path(Path.joinpath(
                    files_path, file)).stat().st_size

                if file_size > min_file_size:
                    folder_file_map[folder].append(file)

        return folder_file_map

    def get_time_differences(self, folders: dict):
        times = []
        for files in folders.values():
            for file in files:
                first_entry = linecache.getline(Path.as_posix(file), 3)
                linecache.clearcache()

                time_entry = first_entry.split(",")[2:4]
                cur_time = pd.to_datetime(time_entry[0] + " " + time_entry[1])
                print(cur_time)
                times.append(cur_time)

        return times

    def iter_files(self, folders: dict):
        for folder in folders.keys():
            print(folder)
            for file in folders[folder]:
                df = pd.read_csv(Path.as_posix(file), header=[0, 1])
                self.create_plot(df, file)

    def create_plot(self, df: pd.DataFrame, filename):
        # Change column names
        df = df.rename(
            columns={'Unnamed: 1_level_0': 'ID', 'Unnamed: 3_level_0': 'Timestamp', 'Unnamed: 7_level_0': 'SHT31D'})

        # Drop last column (it is empty)
        df = df.iloc[:, :-1]

        date_time_combined = pd.to_datetime(
            df[("Timestamp", "date")] +
            ' ' +
            df[("Timestamp", "time")])

        df.drop(columns=[
                ("Timestamp", "date"),
                ("Timestamp", "time")], inplace=True)

        df.insert(2, "Time", date_time_combined)

        data = df.copy(deep=True)

        toRemove = []

        prev_idx, prev_serial = 0, data.iloc[0][('AS5311', 'Serial_Value')]
        initial, calculated, wrap = data.iloc[0][(
            'AS5311', 'Serial_Value')], 0, 0
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

        filename = filename.with_suffix('')
        dend_file_name = str(filename).split("/")[-2:]
        plot_title = f"Dendrometer_{dend_file_name[0]}_{dend_file_name[1]}"

        plt.figure(dpi=600, figsize=(11.69, 8.27))
        fig1 = plt.subplot()
        fig1.set_title(plot_title)
        fig1.plot(df["Time"], df[('AS5311', 'Serial_Value')])
        fig1.plot(data["Time"], data['Calculated'])
        fig1.legend(['Raw data', 'Over/Under flow adjusted'])
        fig1.set_xlabel("Time")
        fig1.set_ylabel("Displacement (serial value)")
        plt.savefig("plots/" + plot_title + ".pdf")


def main():
    formatter = DataFormatter()
    files = formatter.find_valid_files()
    formatter.get_time_differences(files)
    formatter.iter_files(files)

if __name__ == "__main__":
    main()
