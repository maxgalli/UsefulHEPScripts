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
import xgboost
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
        "--xgboost-model",
        required=True
    )

    parser.add_argument(
        "--output-dir",
        default="/eos/home-g/gallim/www/plots/Hgg/NanoMicroCompare"
    )

    return parser.parse_args()


def main(args):

    processed_nano = "tmva_xgboost_reproducers/lead_processed_nano_uncorr.root"
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
    print(ak_arr.type)

    # Explicitely recompute also XGBoost one, just because
    print("Recomputing MVA with XGBoost")
    mva = xgboost.Booster()
    mva.load_model(args.xgboost_model)
    var_order = list(arr_dict.keys())
    bdt_inputs = np.column_stack([ak.to_numpy(ak_arr[name]) for name in var_order])
    tempmatrix = xgboost.DMatrix(bdt_inputs, feature_names=var_order)
    lead_idmva_xgboost = mva.predict(tempmatrix)
    # Thomas workflow
    lead_idmva_xgboost = -np.log(1./lead_idmva_xgboost - 1.)
    lead_idmva_xgboost = 2. / (1. + np.exp(-2.*lead_idmva_xgboost)) - 1.

    # Dump nanoaod inputs to a TTree
    with uproot3.recreate(processed_nano) as f:
        branchdict = {}
        arraydict = {}
    
        for nano_name, model_name in inputs.items():
            #branchdict[model_name] = str(ak_arr[nano_name].type.type).replace('?', '')
            branchdict[model_name] = "float32"
            arraydict[model_name] = ak_arr[nano_name]
    
        f["Events"] = uproot3.newtree(branchdict)
        f["Events"].extend(arraydict)

    # TMVA with RDataFrame
    ROOT.gInterpreter.ProcessLine('''
    TMVA::Experimental::RReader model("{}");
    computeModel = TMVA::Experimental::Compute<{}, float>(model);
    '''.format(args.tmva_model, len(ak_arr.fields)))

    rdf = ROOT.RDataFrame("Events", processed_nano)
    rdf = rdf.Define("lead_idmva_tmva", ROOT.computeModel, ROOT.model.GetVariableNames())
    print("Running RDF event loop")
    dct = rdf.AsNumpy(columns=["lead_idmva_tmva"])
    lead_idmva_tmva = np.array([v[0] for v in dct["lead_idmva_tmva"]])

    # Plot
    print("Plotting to {}".format(args.output_dir))
    bins = 100
    rng = (-1, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(lead_idmva_xgboost, bins=bins, range=rng, histtype="step", label="XGBoost", linewidth=2)
    up.hist(lead_idmva_tmva, bins=bins, range=rng, histtype="step", label="TMVA", linewidth=2)

    up.set_xlabel("lead PhoIDMVA after corrections")
    up.legend(fontsize=18, loc="upper left")

    down.hist(100 * (lead_idmva_xgboost - lead_idmva_tmva) / lead_idmva_tmva, 
              bins=500,
              range=(-100, 100),
              histtype="step",
              density=True,
              color="black",
              linewidth=2
             )
    down.set_xlabel("$(XGB - TMVA)/TMVA$ [%]")
    down.set_yscale("log")

    fig.tight_layout()

    fig.savefig("{}/lead_xgb_tmva.png".format(args.output_dir), bbox_inches='tight')
    fig.savefig("{}/lead_xgb_tmva.pdf".format(args.output_dir), bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(lead_idmva_xgboost, lead_idmva_tmva)
    ax.set_xlabel("XGBoost")
    ax.set_ylabel("TMVA")

    fig.savefig("{}/xgb_tmva_scatter.png".format(args.output_dir), bbox_inches='tight')
    fig.savefig("{}/xgb_tmva_scatter.pdf".format(args.output_dir), bbox_inches='tight')
   

if __name__ == "__main__":
    args = parse_arguments()
    main(args)