"""
Environment: hgg-coffea + install fastparquet
"""
import argparse
import awkward as ak
import uproot 
import matplotlib.pyplot as plt
import mplhep as hep
import numpy as np
import pandas as pd
import vector
import json
hep.style.use("CMS")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Dump plots for nano-micro comparison for Hgg")
    
    parser.add_argument(
        "--nano-input-dir",
        required=True
    )

    parser.add_argument(
        "--micro-input-dir",
        required=True
    )

    parser.add_argument(
        "--output-dir",
        default="/eos/home-g/gallim/www/plots/Hgg/NanoMicroCompare"
    )

    parser.add_argument(
        "--sd",
        choices=["EB", "EE"],
        required=True
    )

    return parser.parse_args()


def main(args):

    # Read nano, micro, EB or EE cuts
    nanoaod_arr = ak.from_parquet(args.nano_input_dir)
    print("Read nanoaod: {}".format(nanoaod_arr.type))
    
    microaod_arr = uproot.concatenate(
        ["{}/*.root:diphotonDumper/trees/ggH_125_13TeV_All_$SYST".format(args.micro_input_dir)]
        )
    print("Read microaod: {}".format(microaod_arr.type))
    # Stupid typo in flashgg
    if "lead_ch_iso_worst__uncorr" in microaod_arr.fields:
        microaod_arr["lead_ch_iso_worst_uncorr"] = microaod_arr["lead_ch_iso_worst__uncorr"]

    if args.sd == "EB":
        nanoaod_arr = nanoaod_arr[np.abs(nanoaod_arr.lead_eta) < 1.5]
        nanoaod_arr = nanoaod_arr[np.abs(nanoaod_arr.sublead_eta) < 1.5]
        microaod_arr = microaod_arr[np.abs(microaod_arr.lead_eta) < 1.5]
        microaod_arr = microaod_arr[np.abs(microaod_arr.sublead_eta) < 1.5]

    if args.sd == "EE":
        nanoaod_arr = nanoaod_arr[np.abs(nanoaod_arr.lead_eta) > 1.5]
        nanoaod_arr = nanoaod_arr[np.abs(nanoaod_arr.sublead_eta) > 1.5]
        microaod_arr = microaod_arr[np.abs(microaod_arr.lead_eta) > 1.5]
        microaod_arr = microaod_arr[np.abs(microaod_arr.sublead_eta) > 1.5]

    # Read catalogue of variables to be plotted
    with open("plots_specs.json", "r") as f:
        columns = json.load(f)

    # Create dict where keys are names of variables in nano and values are names of variables in micro
    nano_micro_names = {var["nano_col"]: var["micro_col"] for var in columns}
    nano_micro_names["event"] = "event"
    nano_micro_names["lumi"] = "lumi"

    # Event by event
    nano_dict = {k: nanoaod_arr[k] for k in nano_micro_names.keys()}
    nano_dict["lead_fixedGridRhoAll"] = nanoaod_arr["lead_fixedGridRhoAll"] # needed for XGBoost vs TMVA
    test_nano = ak.Array(nano_dict)

    test_micro = microaod_arr[nano_micro_names.values()]

    pd_nano = ak.to_pandas(test_nano)
    pd_micro = ak.to_pandas(test_micro)

    pd_nano = pd_nano.set_index(["event", "lumi"])
    pd_micro = pd_micro.set_index(["event", "lumi"])

    pd_joined = pd_nano.join(pd_micro, lsuffix="_nano", rsuffix="_micro")

    print("Joined dataframe:\n{}".format(pd_joined))

    #Remove NaN values
    for nano_name, micro_name in nano_micro_names.items():
        if nano_name in ["event", "lumi"]:
            break
        if nano_name == micro_name:
            nano_name += "_nano"
            micro_name += "_micro"
        pd_joined = pd_joined[pd_joined[nano_name].notna()]
        pd_joined = pd_joined[pd_joined[micro_name].notna()]

    # Cut over delta R
    # Here https://github.com/CoffeaTeam/coffea/blob/3db3fab23064c70d0ca63b185d51c7fa3b7849dc/coffea/nanoevents/methods/vector.py#L74
    # useful info
    deltaR_threshold = 0.1

    four_lead_nano = vector.obj(
        pt=pd_joined["lead_pt"],
        phi=pd_joined["lead_phi_nano"],
        eta=pd_joined["lead_eta_nano"],
        E=pd_joined["lead_energyRaw"]
    )

    four_sublead_nano = vector.obj(
        pt=pd_joined["sublead_pt"],
        phi=pd_joined["sublead_phi_nano"],
        eta=pd_joined["sublead_eta_nano"],
        E=pd_joined["sublead_energyRaw"]
    )

    pd_joined["deltaR_nano"] = four_lead_nano.deltaR(four_sublead_nano)

    four_lead_micro = vector.obj(
        pt=pd_joined["leadPt"],
        phi=pd_joined["lead_phi_micro"],
        eta=pd_joined["lead_eta_micro"],
        E=pd_joined["lead_SCRawE"]
    )

    four_sublead_micro = vector.obj(
        pt=pd_joined["subleadPt"],
        phi=pd_joined["sublead_phi_micro"],
        eta=pd_joined["sublead_eta_micro"],
        E=pd_joined["sublead_SCRawE"]
    )

    pd_joined["lead_deltaR"] = four_lead_nano.deltaR(four_lead_micro)
    pd_joined["sublead_deltaR"] = four_sublead_nano.deltaR(four_sublead_micro)
    pd_joined = pd_joined[pd_joined["lead_deltaR"] < deltaR_threshold]
    pd_joined = pd_joined[pd_joined["sublead_deltaR"] < deltaR_threshold]
    print("Final joined dataframe:\n{}".format(pd_joined))

    # Plot
    print("Start plotting")
    for column in columns:
        fig, (up, middle, down) = plt.subplots(
            nrows=3,
            ncols=1,
            gridspec_kw={"height_ratios": (2, 1, 1)}
            )

        nano_name = column["nano_col"]
        micro_name = column["micro_col"]

        if nano_name == micro_name:
            nano_name += "_nano"
            micro_name += "_micro"
        
        range = column["range"]

        # Up
        n, n_, n__ = up.hist(pd_joined[nano_name], bins=column["bins"], range=range, histtype="step", label="NanoAOD", linewidth=2)
        m, m_, m__ = up.hist(pd_joined[micro_name], bins=column["bins"], range=range, histtype="step", label="MicroAOD", linewidth=2)

        up.legend(fontsize=18, loc="upper right")
        up.set_xlim(range)
        up.set_xlabel(column["var"])
        up.set_ylabel("Events")
        if "log" in column:
            up.set_yscale("log")
        
        # Middle
        ylim = [0, 2]
        middle.set_ylim(ylim)
        #middle.axhline(1, xmin=range[0], xmax=range[1], color="black", alpha=0.6)
        centers = (n_[:-1] + n_[1:]) / 2
        middle.plot(centers, n / m, "k.")
        middle.set_xlim(range)
        middle.set_xlabel(column["var"])
        middle.set_ylabel("$n/\mu$")
        middle.grid(which="both")

        # Down
        perc_range = (-300, 300)
        perc_bins = 500
        down.hist(100 * (pd_joined[nano_name] - pd_joined[micro_name]) / pd_joined[micro_name], 
                  bins=perc_bins,
                  range=perc_range,
                  histtype="step",
                  density=True,
                  color="black",
                  linewidth=2)
        #down.set_yscale("log")
        down.set_xlabel("$(n_{ev} - \mu_{ev})/\mu_{ev}$ [%]")
        down.set_ylabel("Events / {}%".format((perc_range[1] - perc_range[0]) / perc_bins))

        print(column["nano_col"])
        print("nano: {}".format(np.sum(n)))
        print("micro: {}".format(np.sum(m)))
        print("diff = {}".format(abs(np.sum(n) - np.sum(m))))
        print("rel diff = {}%\n".format(100 * abs(np.sum(n) - np.sum(m)) / max(np.sum(n), np.sum(m))))

        fig.tight_layout()

        fig.savefig("{}/{}_{}.png".format(args.output_dir, column["nano_col"], args.sd), bbox_inches='tight')
        fig.savefig("{}/{}_{}.pdf".format(args.output_dir, column["nano_col"], args.sd), bbox_inches='tight')

        plt.close(fig)

    # Dump pandas dataframe to parquet file
    pd_joined.to_parquet("nano_micro_{}.parquet".format(args.sd), engine="fastparquet")
    print("Dumped dataframe to parquet file")

    # Redundant: dump separate dataframes for nano and micro with PhotonID inputs
    nano_vars = {
        "r9": "lead_r9_nano", 
        "s4": "lead_s4_nano",
        "sieie": "lead_sieie_nano",
        "etaWidth": "lead_etaWidth",
        "phiWidth": "lead_phiWidth",
        "sieip": "lead_sieip_nano",
        "pfPhoIso03": "lead_pfPhoIso03",
        "pfChargedIsoPFPV": "lead_pfChargedIsoPFPV",
        "pfChargedIsoWorstVtx": "lead_pfChargedIsoWorstVtx",

        "mva_ID": "lead_mvaID_recomputed"
        }

    micro_vars = {
        "r9": "lead_r9_micro", 
        "s4": "lead_s4_micro",
        "sieie": "lead_sieie_micro",
        "etaWidth": "lead_eta_width",
        "phiWidth": "lead_phi_width",
        "sieip": "lead_sieip_micro",
        "pfPhoIso03": "lead_pho_iso",
        "pfChargedIsoPFPV": "lead_ch_iso",
        "pfChargedIsoWorstVtx": "lead_ch_iso_worst",

        "mva_ID": "lead_mva"
        }

    nano_isos = {
        "pfPhoIso03": "lead_pfPhoIso03",
        "pfChargedIsoPFPV": "lead_pfChargedIsoPFPV",
        "pfChargedIsoWorstVtx": "lead_pfChargedIsoWorstVtx",
        "pfPhoIso03_uncorr": "lead_uncorr_pfPhoIso03",
        "pfChargedIsoPFPV_uncorr": "lead_uncorr_pfChargedIsoPFPV",
        "pfChargedIsoWorstVtx_uncorr": "lead_uncorr_pfChargedIsoWorstVtx",
        }

    micro_isos = {
        "pfPhoIso03": "lead_pho_iso",
        "pfChargedIsoPFPV": "lead_ch_iso",
        "pfChargedIsoWorstVtx": "lead_ch_iso_worst",
        "pfPhoIso03_uncorr": "lead_pho_iso_uncorr",
        "pfChargedIsoPFPV_uncorr": "lead_ch_iso_uncorr",
        "pfChargedIsoWorstVtx_uncorr": "lead_ch_iso_worst_uncorr",
       }

    nano_df = pd_joined[list(nano_vars.values())]
    nano_df.rename(columns=dict((v, k) for k, v in nano_vars.items()), inplace=True)
    nano_df.to_parquet("nano_{}.parquet".format(args.sd), engine="fastparquet")
    print("Dumped nano dataframe to parquet file")

    micro_df = pd_joined[list(micro_vars.values())]
    micro_df.rename(columns=dict((v, k) for k, v in micro_vars.items()), inplace=True)
    micro_df.to_parquet("micro_{}.parquet".format(args.sd), engine="fastparquet")
    print("Dumped micro dataframe to parquet file")

    nano_df = pd_joined[list(nano_isos.values())]
    nano_df.rename(columns=dict((v, k) for k, v in nano_isos.items()), inplace=True)
    nano_df.to_parquet("nano_{}_isos.parquet".format(args.sd), engine="fastparquet")
    print("Dumped nano dataframe for isos to parquet file")

    micro_df = pd_joined[list(micro_isos.values())]
    micro_df.rename(columns=dict((v, k) for k, v in micro_isos.items()), inplace=True)
    micro_df.to_parquet("micro_{}_isos.parquet".format(args.sd), engine="fastparquet")
    print("Dumped micro dataframe for isos to parquet file")



if __name__ == "__main__":
    args = parse_arguments()
    main(args)