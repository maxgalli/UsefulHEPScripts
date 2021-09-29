import ROOT
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep
from array import array
hep.style.use("CMS")


def main():

    processed_nano = "lead_processed_nano.root"
    xml_model = "bdt_original.xml"

    # Standard TMVA
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
    lead_idmva_standard = np.array(results)

    # TMVA with RDataFrame
    print("Experimental way")
    ROOT.gInterpreter.ProcessLine('''
    TMVA::Experimental::RReader model("{}");
    computeModel = TMVA::Experimental::Compute<{}, float>(model);
    '''.format(xml_model, events.GetNbranches()))

    rdf = ROOT.RDataFrame("Events", processed_nano)
    rdf = rdf.Define("lead_idmva_tmva", ROOT.computeModel, ROOT.model.GetVariableNames())
    dct = rdf.AsNumpy(columns=["lead_idmva_tmva"])
    lead_idmva_rdf = np.array([v[0] for v in dct["lead_idmva_tmva"]])

    # Plot
    bins = 100
    rng = (-1, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(lead_idmva_standard, bins=bins, range=rng, histtype="step", label="Standard", linewidth=2)
    up.hist(lead_idmva_rdf, bins=bins, range=rng, histtype="step", label="Experimental", linewidth=2)

    up.set_xlabel("lead PhoIDMVA after corrections")
    up.legend(fontsize=18, loc="upper left")

    down.hist(100 * (lead_idmva_standard - lead_idmva_rdf) / lead_idmva_rdf, 
              bins=500,
              range=(-100, 100),
              histtype="step",
              density=True,
              color="black",
              linewidth=2
             )
    down.set_xlabel("$(standard - experimental) / experimental$ [%]")
    down.set_yscale("log")

    fig.tight_layout()

    fig.savefig("st_vs_exp.png", bbox_inches='tight')
    fig.savefig("st_vs_exp.pdf", bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(lead_idmva_standard, lead_idmva_rdf)
    ax.set_xlabel("Standard")
    ax.set_ylabel("Experimental")

    fig.savefig("st_vs_exp_scatter.png", bbox_inches='tight')
    fig.savefig("st_vs_exp_scatter.pdf", bbox_inches='tight')
   

if __name__ == "__main__":
    main()