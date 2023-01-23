import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict


class Plotter:
    def __init__(self) -> None:
        cur_path = Path.cwd()
        deployment_file = Path.joinpath(cur_path, "data", "deployment.csv")
        deployment_df = pd.read_csv(deployment_file)

        deployment_df = deployment_df.fillna("")
        self.pairs = defaultdict(list)

        for _, row in deployment_df.iterrows():
            plot_id, dev_id, note = row["Plot ID"], row["Device ID"], row["Notes"]

            # There is a comment about this dendrometer not deployed
            if note:
                continue

            self.pairs[plot_id].append(dev_id)

    def get_pair_mapping(self):
        return self.pairs

    def save_plot(self, filename, df: pd.DataFrame) -> None:
        filename = filename.with_suffix('')
        dend_file_name = str(filename).split("/")[-2:]
        plot_title = f"Dendrometer_{dend_file_name[0]}_{dend_file_name[1]}"

        plt.figure(dpi=600, figsize=(11.69, 8.27))
        fig1 = plt.subplot()
        fig1.set_title(plot_title)
        fig1.plot(df["Time"], df[('AS5311', 'Serial_Value')])
        fig1.plot(df["Time"], df['Calculated'])
        fig1.legend(['Raw data', 'Over/Under flow adjusted'])
        fig1.set_xlabel("Time")
        fig1.set_ylabel("Displacement (serial value)")
        plt.savefig(f"data/{dend_file_name[0]}/{dend_file_name[1]}.pdf")
        plt.close()

    def save_plot_pair(self,
                       dend1: Tuple[str, pd.DataFrame],
                       dend2: Tuple[str, pd.DataFrame]
                       ) -> None:

        filename1 = str(dend1[0].with_suffix('')).split("/")[-2:]
        filename2 = str(dend2[0].with_suffix('')).split("/")[-2:]

        plot_title = f"Dendrometer_{filename1[0]}_and_{filename2[0]}"
        print(plot_title)

        plt.figure(dpi=600, figsize=(11.69, 8.27))
        fig1 = plt.subplot()
        fig1.set_title(plot_title)
        # fig1.plot(dend1[1]["Time"], dend1[1][('AS5311', 'Serial_Value')])
        # fig1.plot(dend2[1]["Time"], dend2[1][('AS5311', 'Serial_Value')])
        fig1.plot(dend1[1]["Time"], dend1[1]['Calculated'])
        fig1.plot(dend2[1]["Time"], dend2[1]['Calculated'])
        # fig1.legend([f"{filename1[0]} raw", f"{filename2[0]} raw",
        #             f"{filename1[0]} corrected", f"{filename2[0]} corrected"])
        fig1.legend([f"Dendrometer {filename1[0]} corrected",
                    f"Dendrometer {filename2[0]} corrected"])

        fig1.set_xlabel("Time")
        fig1.set_ylabel("Displacement (serial value)")
        plt.savefig(f"data/pairs/{plot_title}.pdf")
        plt.close()
