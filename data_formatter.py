import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
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

        cur_path = Path.cwd()
        data_path = Path.joinpath(cur_path, "data")
        folders = [folder for folder in data_path.iterdir() if folder.is_dir()]
        self.folder_file_map = defaultdict(list)

        for folder in folders:
            files_path = Path.joinpath(data_path, folder)
            files = [file for file in Path(files_path).glob("*.csv")]

            for file in files:
                file_size = Path(Path.joinpath(
                    files_path, file)).stat().st_size
                print(file_size)

                if file_size > min_file_size:
                    self.folder_file_map[folder].append(file)

        return self.folder_file_map


def main():
    formatter = DataFormatter()
    files = formatter.find_valid_files()
    for folder, file in files.items():
        print(folder, ": ", file)


if __name__ == "__main__":
    main()