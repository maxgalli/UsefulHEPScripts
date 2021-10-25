import ROOT
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import xgboost
from array import array
import sys

try:
    import awkward as ak
    import uproot
    import mplhep as hep
    hep.style.use("CMS")
except:
    pass


def main():
    # check fucking python version
    py_version = int(sys.version[0])
    py2 = False
    if py_version == 2:
        py2 = True

    processed_nano = "lead_processed_nano.root"
    
    xml_model = "bdt.xml"
    xgb_model = "bdt.json"
    if py2:
        xml_model = "bdt_original_py2.xml"
        xgb_model = "bdt_original_py2.xgb"

    # Explicitely recompute also XGBoost
    if py2:
        from collections import OrderedDict
        var_order = ["SCRawE", "r9", "sigmaIetaIeta", "etaWidth", "phiWidth", 
        "covIEtaIPhi", "s4", "phoIso03", "chgIsoWrtChosenVtx", "chgIsoWrtWorstVtx", "scEta", "rho"]
        rdf = ROOT.RDataFrame("Events", processed_nano)
        events = rdf.AsNumpy()
        ordered_events = OrderedDict({k: events[k] for k in var_order})
        bdt_inputs = np.column_stack(list(ordered_events.values()))
    else:
        f = uproot.open(processed_nano)
        t = f["Events"]
        events = t.arrays()

        print("Recomputing MVA with XGBoost")
        var_order = list(events.fields)
        bdt_inputs = np.column_stack([ak.to_numpy(events[name]) for name in var_order])
    mva = xgboost.Booster()
    mva.load_model(xgb_model)
    tempmatrix = xgboost.DMatrix(bdt_inputs, feature_names=var_order)
    lead_idmva_xgboost = mva.predict(tempmatrix)
    # Thomas workflow
    lead_idmva_xgboost = 1.0 - 2.0 / (1.0 + np.exp(2.0 * lead_idmva_xgboost))
    
    #lead_idmva_xgboost = 2 * lead_idmva_xgboost - 1
    #lead_idmva_xgboost = 1. / (1. + np.exp(-1. * (lead_idmva_xgboost + 1.)))
    #lead_idmva_xgboost = 2. / (1. + np.exp(-2. * (lead_idmva_xgboost + 1.))) - 1.
    #lead_idmva_xgboost = 2. / (1. + np.exp(-2. * (lead_idmva_xgboost))) - 1.
    #lead_idmva_xgboost = 1. / (1 + np.exp(-lead_idmva_xgboost))

    # TMVA with RDataFrame
    """
    ROOT.gInterpreter.ProcessLine('''
    TMVA::Experimental::RReader model("{}");
    computeModel = TMVA::Experimental::Compute<{}, float>(model);
    '''.format(xml_model, len(events.fields)))

    rdf = ROOT.RDataFrame("Events", processed_nano)
    rdf = rdf.Define("lead_idmva_tmva", ROOT.computeModel, ROOT.model.GetVariableNames())
    print("Running RDF event loop")
    dct = rdf.AsNumpy(columns=["lead_idmva_tmva"])
    lead_idmva_tmva = np.array([v[0] for v in dct["lead_idmva_tmva"]])
    """

    print("Standard way")
    f = ROOT.TFile(processed_nano)
    events = f.Get("Events")

    ROOT.TMVA.Tools.Instance()
    ROOT.TMVA.PyMethodBase.PyInitialize()
    reader = ROOT.TMVA.Reader("Color:!Silent")

    branches = {}
    for branch in events.GetListOfBranches():
        branch_name = branch.GetName()
        branches[branch_name] = array('f', [-999])
        reader.AddVariable(branch_name, branches[branch_name])
        events.SetBranchAddress(branch_name, branches[branch_name])

    reader.BookMVA("BDT", ROOT.TString(xml_model))

    results = []
    for i in range(events.GetEntries()):
        events.GetEntry(i)
        results.append(reader.EvaluateMVA("BDT"))
    lead_idmva_tmva = np.array(results)
    # invert https://root.cern.ch/doc/master/MethodBDT_8cxx_source.html#l01429
    #lead_idmva_tmva = -1/2 * np.log(2/(lead_idmva_tmva + 1) - 1)

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
    up.set_yscale("log")

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

    fig.savefig("xgb_vs_tmva_{}.png".format(py_version), bbox_inches='tight')
    fig.savefig("xgb_vs_tmva_{}.pdf".format(py_version), bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(lead_idmva_xgboost, lead_idmva_tmva)
    ax.set_xlabel("XGBoost")
    ax.set_ylabel("TMVA")

    fig.savefig("xgb_vs_tmva_scatter_{}.png".format(py_version), bbox_inches='tight')
    fig.savefig("xgb_vs_tmva_scatter_{}.pdf".format(py_version), bbox_inches='tight')
   

if __name__ == "__main__":
    main()
