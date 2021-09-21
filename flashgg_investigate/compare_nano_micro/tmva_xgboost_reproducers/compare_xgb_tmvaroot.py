import awkward as ak
import ROOT
import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import xgboost
hep.style.use("CMS")


def main():

    processed_nano = "lead_processed_nano.root"
    root_model = "bdt.root"
    xgb_model = "bdt.json"

    f = uproot.open(processed_nano)
    t = f["Events"]
    events = t.arrays()

    # Explicitely recompute also XGBoost
    print("Recomputing MVA with XGBoost")
    mva = xgboost.Booster()
    mva.load_model(xgb_model)
    var_order = list(events.fields)
    bdt_inputs = np.column_stack([ak.to_numpy(events[name]) for name in var_order])
    tempmatrix = xgboost.DMatrix(bdt_inputs, feature_names=var_order)
    lead_idmva_xgboost = mva.predict(tempmatrix)
    lead_idmva_xgboost = 1. / (1. + np.exp(-1. * (lead_idmva_xgboost + 1.)))
    #lead_idmva_xgboost = 2. / (1. + np.exp(-2. * (lead_idmva_xgboost + 1.))) - 1.

    # TMVA with RDataFrame
    print("Predicting using model found in ROOT file")
    bdt = ROOT.TMVA.Experimental.RBDT[""]("BDT", root_model)
    x = np.column_stack([events[field].to_numpy() for field in events.fields])
    lead_idmva_tmva = bdt.Compute(x).squeeze()

    # Plot
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

    fig.savefig("xgb_vs_roottmva.png", bbox_inches='tight')
    fig.savefig("xgb_vs_roottmva.pdf", bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(lead_idmva_xgboost, lead_idmva_tmva)
    ax.set_xlabel("XGBoost")
    ax.set_ylabel("TMVA")

    fig.savefig("xgb_vs_roottmva_scatter.png", bbox_inches='tight')
    fig.savefig("xgb_vs_roottmva_scatter.pdf", bbox_inches='tight')
   

if __name__ == "__main__":
    main()