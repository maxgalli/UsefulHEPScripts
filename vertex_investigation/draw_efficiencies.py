import uproot
import coffea.hist as hist
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep

hep.set_style("CMS")



def count_fraction(awk_arr, var, limits):
    """ Given an awkward array, a variable (will be p_t) and a list of ranges (i.e. list of 2-tuples), loop over the ranges
    to compute the fraction of events with diff_z < 1. (cm) in every range of var.
    Return two lists containing the computed values (for each range) and theis uncertainties.
    """
    vals = []
    for rng in limits:
        part_arr = awk_arr[(awk_arr[var] > rng[0]) & (awk_arr[var] < rng[1])]
        part_arr['diff_z'] = abs(part_arr.gen_vtx_z - part_arr.vtx_z)
        frac = len(part_arr[part_arr.diff_z < 1.]) / len(part_arr)
        vals.append(frac)
    uncs = np.zeros(len(vals))
    return vals, uncs


def main():

    # Needed names for files and trees
    v0_file = "/work/gallim/root_files/vertex_investigation/VertexInvestigation_vtx0/output_GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3f96409841a3cc85b911eb441562baae_USER_*.root"
    v_custom_file = "/work/gallim/root_files/vertex_investigation/VertexInvestigation/output_GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3f96409841a3cc85b911eb441562baae_USER_*.root"

    tree_name = "diphotonDumper/trees/ggH_125_13TeV_All_$SYST"

    # Read two trees lazily
    imp_variables = ["pt", "vtx_z", "gen_vtx_z", "weight"]

    arr_vtx0 = uproot.lazy(["{}:{}".format(v0_file, tree_name)], imp_variables)
    arr_vtxc = uproot.lazy(["{}:{}".format(v_custom_file, tree_name)], imp_variables)

    # Compute quantities
    n_ranges = 25
    pt_range = np.linspace(0, 300, n_ranges)

    pt_ranges = []
    inf = pt_range[0]
    for sup in pt_range[1:]:
        pt_ranges.append((inf, sup))
        inf = sup

    x_vtx0, x_vtxc, y_vtx0, y_vtxc = {}, {}, {}, {}
    xs = [np.mean(rng) for rng in pt_ranges]
    x_vtx0["values"] = xs
    x_vtxc["values"] = xs
    x_vtx0["unc"] = np.zeros(len(x_vtx0["values"]))
    x_vtxc["unc"] = np.zeros(len(x_vtxc["values"]))
    y_vtx0["values"], y_vtx0["unc"] = count_fraction(arr_vtx0, 'pt', pt_ranges)
    y_vtxc["values"], y_vtxc["unc"] = count_fraction(arr_vtxc, 'pt', pt_ranges)

    # Plot
    fig, ax = plt.subplots()
    plt.errorbar(x_vtx0["values"], y_vtx0["values"], xerr=x_vtx0["unc"], yerr=y_vtx0["unc"], fmt='ko', label="Vertex 0th")
    plt.errorbar(x_vtxc["values"], y_vtxc["values"], xerr=x_vtxc["unc"], yerr=y_vtxc["unc"], fmt='ro', label="Vertex Reco")
    ax.legend(fontsize=18, loc="lower right")
    ax.set_xlabel("$p_T$")
    ax.set_ylabel("Fraction of |$Z_{reco}$ - $Z_{true}$| < 10 mm")

    output_dir = "/eos/home-g/gallim/www/plots/Hgg/VertexInvestigation"
    output_name = "identification_efficiency"
    hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
    fig.savefig("{}/{}.png".format(output_dir, output_name), bbox_inches='tight')
    fig.savefig("{}/{}.pdf".format(output_dir, output_name), bbox_inches='tight')



if __name__ == "__main__":
    main()
