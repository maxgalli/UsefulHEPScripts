import awkward as ak
import ROOT
import uproot
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
import xgboost
hep.style.use("CMS")

def predict_with_xgboost(events, model):
    print("Recomputing MVA with XGBoost")
    mva = xgboost.Booster()
    mva.load_model(model)
    var_order = list(events.fields)
    bdt_inputs = np.column_stack([ak.to_numpy(events[name]) for name in var_order])
    tempmatrix = xgboost.DMatrix(bdt_inputs, feature_names=var_order)
    mva_xgboost = mva.predict(tempmatrix)
    #mva_xgboost = 1. / (1. + np.exp(-1. * (mva_xgboost + 1.)))
    #mva_xgboost = 2. / (1. + np.exp(-2. * (mva_xgboost + 1.))) - 1.

    return mva_xgboost

def predict_with_tmva(root_file, events, model):
    rdf = ROOT.RDataFrame("Events", root_file)
    
    id = root_file.replace(".root", "")
    ROOT.gInterpreter.ProcessLine('''
    TMVA::Experimental::RReader model{}("{}");
    computeModel{} = TMVA::Experimental::Compute<{}, float>(model{});
    '''.format(id, model, id, len(events.fields), id))

    rdf = rdf.Define("y", getattr(ROOT, "computeModel{}".format(id)), getattr(ROOT, "model{}".format(id)).GetVariableNames())
    print("Running RDF event loop")
    dct = rdf.AsNumpy(columns=["y"])
    mva_tmva = np.array([v[0] for v in dct["y"]])

    return mva_tmva

def main():

    test_signal = "test_signal.root"
    test_background = "test_background.root"
    xml_model = "dataset/weights/TMVAClassification_BDT.weights.xml"
    xgb_model = "dataset/weights/TMVAClassification_BDT.weights.json"

    mvas_tmva = []
    mvas_xgboost = []
    for fl in [test_signal, test_background]:
        f = uproot.open(fl)
        t = f["Events"]
        events = t.arrays()
        mvas_xgboost.append(predict_with_xgboost(events, xgb_model))
        print(predict_with_xgboost(events, xgb_model))
        mvas_tmva.append(predict_with_tmva(fl, events, xml_model))

    mva_xgboost = np.hstack(mvas_xgboost)
    mva_tmva = np.hstack(mvas_tmva)

    # Plot
    bins = 100
    rng = (-1, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(mva_xgboost, bins=bins, range=rng, histtype="step", label="XGBoost", linewidth=2)
    up.hist(mva_tmva, bins=bins, range=rng, histtype="step", label="TMVA", linewidth=2)

    up.set_xlabel("Scores")
    up.legend(fontsize=18, loc="upper left")

    down.hist(100 * (mva_xgboost - mva_tmva) / mva_tmva, 
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

    fig.savefig("xgb_vs_tmva_jonas.png", bbox_inches='tight')
    fig.savefig("xgb_vs_tmva_jonas.pdf", bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(mva_xgboost, mva_tmva)
    ax.set_xlabel("XGBoost")
    ax.set_ylabel("TMVA")

    fig.savefig("xgb_vs_tmva_scatter_jonas.png", bbox_inches='tight')
    fig.savefig("xgb_vs_tmva_scatter_jonas.pdf", bbox_inches='tight')
   

if __name__ == "__main__":
    main()