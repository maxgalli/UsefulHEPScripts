import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
from pathlib import Path
import pandas as pd
import concurrent.futures
import json

hep.style.use("CMS")


def pandas_df_from_parquet(input_dir, columns):
    df = pd.DataFrame()
    for file in Path(input_dir).glob("*.parquet"):
        df_tmp = pd.read_parquet(file, columns=columns)
        df = pd.concat([df, df_tmp], ignore_index=True)
    return df


def pandas_df_from_parquet_parallel(input_dir, columns):
    df = pd.DataFrame()
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(pd.read_parquet, file, columns=columns)
            for file in Path(input_dir).glob("*.parquet")
        ]
        df = pd.concat(
            [f.result() for f in concurrent.futures.as_completed(futures)],
            ignore_index=True,
        )
    return df


def plot_variable(data_array, mc_array, variable_conf, output_dir):
    name = variable_conf["name"]
    title = variable_conf["title"]
    x_label = variable_conf["x_label"]
    bins = variable_conf["bins"]
    range = variable_conf["range"]

    print("Plotting variable: {}".format(name))

    fig, ax = plt.subplots()
    data_hist, data_bins = np.histogram(
        data_array[name], bins=bins, range=range, density=True
    )
    data_centers = (data_bins[1:] + data_bins[:-1]) / 2
    ax.plot(
        data_centers,
        data_hist,
        label=f"{name} Data",
        color="k",
        marker="o",
        linestyle="",
    )
    ax.hist(
        mc_array[name],
        bins=50,
        range=range,
        histtype="step",
        label=f"{name} MC",
        density=True,
    )
    ax.set_xlabel(x_label)
    ax.set_ylabel("Events")
    ax.legend()
    fig.savefig(output_dir + "/" + name + ".pdf", bbox_inches="tight")
    fig.savefig(output_dir + "/" + name + ".png", bbox_inches="tight")
    plt.close(fig)


def main():
    data_input_dir = (
        "/work/gallim/devel/HiggsDNA_studies/tnp/official_parquet_output/DoubleEG"
    )
    mc_input_dir = "/work/gallim/devel/HiggsDNA_studies/tnp/official_parquet_output/DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8/nominal"
    output_dir = "/eos/home-g/gallim/www/plots/Hgg/HiggsDNA/TagAndProbe"
    with open("var_specs.json", "r") as f:
        vars_config = json.load(f)
    columns = [dct["name"] for dct in vars_config]
    print("Loading data...")
    data_arr = pandas_df_from_parquet_parallel(data_input_dir, columns)
    print("Loading MC...")
    mc_arr = pandas_df_from_parquet_parallel(mc_input_dir, columns)

    for var_conf in vars_config:
        plot_variable(data_arr, mc_arr, var_conf, output_dir)


if __name__ == "__main__":
    main()
