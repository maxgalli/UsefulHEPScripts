import argparse
import awkward as ak
import numpy as np
import xgboost
import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Compare nano and micro MVA")
    
    parser.add_argument(
        "--nano-input",
        required=True
    )

    parser.add_argument(
        "--micro-input",
        required=True
    )

    parser.add_argument(
        "--output-dir",
        default="/eos/home-g/gallim/www/plots/Hgg/NanoMicroCompare/MVAs"
    )

    return parser.parse_args()


def main(args):

    nano_arr = ak.from_parquet(args.nano_input)
    micro_arr = ak.from_parquet(args.micro_input)

    nano_mva = nano_arr.mva_ID
    micro_mva = micro_arr.mva_ID

    # Recompute Nano PhoID MVA
    print("Computing MVA for nano")
    input_names = nano_arr.fields[:-3]
    inputs = np.column_stack([ak.to_numpy(nano_arr[name]) for name in input_names])
    weights = "tmva_xgboost_reproducers/bdt_original.json"
    mva = xgboost.Booster()
    mva.load_model(weights)
    tempmatrix = xgboost.DMatrix(inputs, feature_names=input_names)
    nano_mva = mva.predict(tempmatrix)
    # Thomas workflow
    nano_mva = -np.log(1./nano_mva - 1.)
    nano_mva = 2. / (1. + np.exp(-2.*nano_mva)) - 1.

    # Recompute Micro PhoID MVA
    print("Computing MVA for micro")
    input_names = micro_arr.fields[:-3]
    inputs = np.column_stack([ak.to_numpy(micro_arr[name]) for name in input_names])
    weights = "tmva_xgboost_reproducers/bdt_original.json"
    mva = xgboost.Booster()
    mva.load_model(weights)
    tempmatrix = xgboost.DMatrix(inputs, feature_names=input_names)
    micro_mva = mva.predict(tempmatrix)
    # Thomas workflow
    micro_mva = -np.log(1./micro_mva - 1.)
    micro_mva = 2. / (1. + np.exp(-2.*micro_mva)) - 1.

    # Plot
    print("Plotting")
    bins = 100
    rng = (-1, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(nano_mva, bins=bins, range=rng, histtype="step", label="Nano", linewidth=2)
    up.hist(micro_mva, bins=bins, range=rng, histtype="step", label="Micro", linewidth=2)

    up.set_xlabel("PhoIDMVA")
    up.legend(fontsize=18, loc="upper left")
    up.set_yscale("log")

    down.hist(100 * (nano_mva - micro_mva) / micro_mva, 
              bins=500,
              range=(-100, 100),
              histtype="step",
              density=True,
              color="black",
              linewidth=2
             )
    down.set_xlabel("$(n - \mu)/\mu$ [%]")
    down.set_yscale("log")

    fig.tight_layout()

    fig.savefig("{}/nano_micro_mva.png".format(args.output_dir), bbox_inches='tight')
    fig.savefig("{}/nano_micro_mva.pdf".format(args.output_dir), bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(nano_mva, micro_mva)
    ax.set_xlabel("Nano")
    ax.set_ylabel("Micro")

    fig.savefig("{}/nano_micro_mva_scatter.png".format(args.output_dir), bbox_inches='tight')
    fig.savefig("{}/nano_micro_mva_scatter.pdf".format(args.output_dir), bbox_inches='tight')


if __name__ == "__main__":
    args = parse_arguments()
    main(args)