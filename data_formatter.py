import pandas as pd
import matplotlib.pyplot as plt
import os
from collections import defaultdict


class DataFormatter:
    def __init__(self) -> None:
        self.time_offset = 0
        print("Constructor")

    def find_valid_files(self, min_file_size: int = 1000000) -> dict:
        """
        Find the valid data files inside the data folder

        min_file_size -- the minimum valid size for a file in bytes (default 1000000 bytes)
        """

        cur_path = os.getcwd()
        data_path = cur_path + "/data"
        folders = os.listdir(data_path)
        self.folder_file_map = defaultdict(list)

        for folder in folders:
            files_path = os.path.join(data_path, folder)
            files = os.listdir(files_path)

            for file in files:
                file_size = os.stat(os.path.join(files_path, file)).st_size

                if file_size > min_file_size:
                    self.folder_file_map[folder].append(file)

        return self.folder_file_map


def main():
    formatter = DataFormatter()
    print(formatter.find_valid_files())


if __name__ == "__main__":
    main()
