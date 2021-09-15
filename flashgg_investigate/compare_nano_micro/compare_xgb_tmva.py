"""
Environment: hgg-coffea + install ROOT with mamba

Compare the PhotonIDMVA for the lead photon performed using XGBoost and plain TMVA.
The input-dataframe is a pandas dataframe produced with dump_plots.py, which stores variables
for both lead and sublead photon coming from both microaod (flashgg) and nanoaod (hgg-coffea).
The dataframe is ordered by event and lumi, which makes sure that the events are actually the same.
Reference to apply TMVA model: https://root.cern.ch/doc/v610/ApplicationClassificationKeras_8py_source.html
"""
import argparse
import awkward as ak
import pandas as pd
import ROOT
import uproot3
from array import array
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
hep.style.use("CMS")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Compare application of XGBoost and TMVA for classification")

    parser.add_argument(
        "--input-dataframe",
        required=True
    )

    parser.add_argument(
        "--tmva-model",
        required=True
    )

    parser.add_argument(
        "--output-dir",
        default="/eos/home-g/gallim/www/plots/Hgg/NanoMicroCompare"
    )

    return parser.parse_args()


def main(args):

    processed_nano = "lead_processed_nano.root"
    df = pd.read_parquet(args.input_dataframe)
    print("Read input dataframe:\n{}".format(df))

    inputs = {
        "lead_energyRaw": "SCRawE", 
        "lead_r9": "r9", 
        "lead_sieie":"sigmaIetaIeta", 
        "lead_etaWidth": "etaWidth", 
        "lead_phiWidth": "phiWidth", 
        "lead_sieip": "covIEtaIPhi", 
        "lead_s4": "s4", 
        "lead_pfPhoIso03": "phoIso03", 
        "lead_pfChargedIsoPFPV": "chgIsoWrtChosenVtx", 
        "lead_pfChargedIsoWorstVtx": "chgIsoWrtWorstVtx",
        "lead_eta": "scEta", 
        "lead_fixedGridRhoAll": "rho"
        }

    # This is needed just to not hardcore the branch type later
    arr_dict = {}
    for name in inputs.keys():
        name_orig = name
        # Since I don't remember which ones have the suffix _nano
        if name_orig not in list(df.columns):
            name += "_nano"
        arr_dict[name_orig] = df[name]
    ak_arr = ak.Array(arr_dict)

    # Dump nanoaod inputs to a TTree
    with uproot3.recreate(processed_nano) as f:
        branchdict = {}
        arraydict = {}
    
        for name in inputs.keys():
            branchdict[name] = str(ak_arr[name].type.type).replace('?', '')
            arraydict[name] = ak_arr[name]
    
        f["Events"] = uproot3.newtree(branchdict)
        f["Events"].extend(arraydict)

    # Setup TMVA
    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()
    reader = ROOT.TMVA.Reader("Color:!Silent")

    # Load data
    data = ROOT.TFile(processed_nano)
    events = data.Get("Events")

    # Build reader in TMVA
    branches = {}
    for branch in events.GetListOfBranches():
        name = branch.GetName()
        tmva_name = inputs[name]
        branches[tmva_name] = array("f", [-999])
        reader.AddVariable(tmva_name, branches[tmva_name])
        events.SetBranchAddress(name, branches[tmva_name])

    reader.BookMVA("BDT", ROOT.TString(args.tmva_model))

    # Prediction
    lst = []
    print("Starting event loop")
    for i in range(len(ak_arr)): # not exactly fast
        events.GetEntry(i)
        lst.append(reader.EvaluateMVA("BDT"))
    lead_idmva_tmva = np.array(lst)

    # Plot
    print("Plotting to {}".format(args.output_dir))
    bins = 200
    rng = (-1, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(df["lead_mvaID_recomputed"], bins=bins, range=rng, histtype="step", label="XGBoost", linewidth=2)
    up.hist(lead_idmva_tmva, bins=bins, range=rng, histtype="step", label="TMVA", linewidth=2)

    up.set_xlabel("lead PhoIDMVA after corrections")
    up.legend(fontsize=18, loc="upper left")

    down.hist(100 * (df["lead_mvaID_recomputed"] - lead_idmva_tmva) / lead_idmva_tmva, 
              bins=500,
              range=(-100, 100),
              histtype="step",
              density=True,
              linewidth=2
             )
    down.set_xlabel("$(XGB - TMVA)/TMVA$ [%]")
    down.set_yscale("log")

    fig.tight_layout()

    fig.savefig("{}/lead_nano_cfr_tmva.png".format(args.output_dir), bbox_inches='tight')
    fig.savefig("{}/lead_nano_cfr_tmva.pdf".format(args.output_dir), bbox_inches='tight')

    

if __name__ == "__main__":
    args = parse_arguments()
    main(args)