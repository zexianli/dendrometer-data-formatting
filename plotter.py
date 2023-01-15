import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
from pathlib import Path
import math

# Use to plot dendrometer pairs
PlotType = Enum('PlotType', ['SINGLE', 'PAIR'])


class Plotter:
    def __init__(self) -> None:
        cur_path = Path.cwd()
        deployment_file = Path.joinpath(cur_path, "data", "deployment.csv")
        deployment_df = pd.read_csv(deployment_file)

        deployment_df = deployment_df.fillna("")
        self.pairs = []

        current_pair = []
        for _, row in deployment_df.iterrows():
            id, note = row["Device ID"], row["Notes"]
            if note:
                continue

            current_pair.append(id)
            if len(current_pair) == 2:
                self.pairs.append(current_pair)
                current_pair = []

    def save_plot(self, df: pd.DataFrame, filename: str, PlotType: PlotType) -> None:
        plt.figure(dpi=600, figsize=(11.69, 8.27))
        fig1 = plt.subplot()

        filename = filename.with_suffix('')
        dend_file_name = str(filename).split("/")[-2:]
        plot_title = f"Dendrometer_{dend_file_name[0]}_{dend_file_name[1]}"

        fig1.set_title(plot_title)
        fig1.plot(
            df["Time"], df[('AS5311', 'Serial_Value')])
        fig1.plot(df["Time"], df['Calculated'])
        fig1.legend(
            ['Raw data', 'Over/Under flow adjusted'])
        fig1.set_xlabel("Time")
        fig1.set_ylabel("Displacement (serial value)")
        plt.savefig(
            f"data/{dend_file_name[0]}/{dend_file_name[1]}.pdf")

        pass
