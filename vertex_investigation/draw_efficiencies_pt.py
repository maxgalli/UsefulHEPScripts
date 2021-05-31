import uproot
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import ROOT

from utils import parse_arguments
from utils import file_names_tmpl
from utils import tree_name_tmpl
from utils import setup_logging
from utils import rel_diff_asymm
from utils.plotting_specs import y_lims

hep.set_style("CMS")

import logging
logger = logging.getLogger(__name__)



def count_fraction(awk_arr, var, limits):
    """ Given an awkward array, a variable (will be p_t) and a list of ranges (i.e. list of 2-tuples), loop over the ranges
    to compute the fraction of events with diff_z < 1. (cm) in every range of var.
    Return two lists containing the computed values (for each range) and theis uncertainties.
    Uncertainties are computed using ROOT.TEfficiency.ClopperPearson, and it is thus a list of elements [low, up]
    """
    vals = []
    uncs = []
    for rng in limits:
        logger.info("Working with range {}".format(rng))
        part_arr = awk_arr[(awk_arr[var] > rng[0]) & (awk_arr[var] < rng[1])]
        part_arr['diff_z'] = abs(part_arr.gen_vtx_z - part_arr.vtx_z)
        total = len(part_arr)
        passed = len(part_arr[part_arr.diff_z < 1.])
        frac = passed / total
        vals.append(frac)
        unc = [
                abs(ROOT.TEfficiency.ClopperPearson(total, passed, .68, 0) - frac),
                abs(ROOT.TEfficiency.ClopperPearson(total, passed, .68, 1) - frac)
                ]
        uncs.append(unc)

    return vals, uncs


def main(args):
    logger = setup_logging()

    v0_input_dir = args.v0_input_dir
    vcustom_input_dir = args.vcustom_input_dir
    output_dir = args.output_dir
    channel = args.channel

    tree_name = tree_name_tmpl.format(channel)

    # Needed names for files and trees
    v0_file = v0_input_dir + "/" + file_names_tmpl[channel]
    v_custom_file = vcustom_input_dir + "/" + file_names_tmpl[channel]

    ranges = {
            "pt": {
                "range": (0, 300),
                "label": "$p_T$"
                },
            }

    for var, specs in ranges.items():
        logger.info("Working with {}".format(var))

        # Read two trees lazily
        imp_variables = [var] + ["vtx_z", "gen_vtx_z", "weight"]

        arr_vtx0 = uproot.lazy(["{}:{}".format(v0_file, tree_name)], imp_variables)
        arr_vtxc = uproot.lazy(["{}:{}".format(v_custom_file, tree_name)], imp_variables)

        # Compute quantities
        n_ranges = 35
        var_range = np.linspace(specs["range"][0], specs["range"][1], n_ranges)

        var_ranges = []
        inf = var_range[0]
        for sup in var_range[1:]:
            var_ranges.append((inf, sup))
            inf = sup

        x_vtx0, x_vtxc, y_vtx0, y_vtxc = {}, {}, {}, {}
        xs = [np.mean(rng) for rng in var_ranges]
        x_vtx0["values"] = xs
        x_vtxc["values"] = xs
        x_vtx0["unc"] = [np.std(arr_vtx0[(arr_vtx0[var] > rng[0]) & (arr_vtx0[var] < rng[1])][var].to_numpy()) for rng in var_ranges]
        x_vtxc["unc"] = [np.std(arr_vtxc[(arr_vtxc[var] > rng[0]) & (arr_vtxc[var] < rng[1])][var].to_numpy()) for rng in var_ranges]

        y_vtx0["values"], y_vtx0["unc"] = count_fraction(arr_vtx0, var, var_ranges)
        y_vtxc["values"], y_vtxc["unc"] = count_fraction(arr_vtxc, var, var_ranges)

        # Plot
        fig, (ax, rax) = plt.subplots(
                nrows=2,
                ncols=1,
                gridspec_kw={"height_ratios": (3, 1)},
                sharex=True
                )
        ax.errorbar(x_vtx0["values"], y_vtx0["values"], xerr=x_vtx0["unc"], yerr=np.array(y_vtx0["unc"]).T, fmt='ro', label="Vertex 0th")
        ax.errorbar(x_vtxc["values"], y_vtxc["values"], xerr=x_vtxc["unc"], yerr=np.array(y_vtxc["unc"]).T, fmt='bs', label="Vertex Reco")

        rdiff = [
            rel_diff_asymm(v0, vc, v0_uncs, vc_uncs) for v0, vc, v0_uncs, vc_uncs in zip(
                y_vtx0["values"], y_vtxc["values"], y_vtx0["unc"], y_vtxc["unc"]
                )
                ]

        rax.errorbar(
                x_vtx0["values"], 
                y=[rd[0] for rd in rdiff],
                yerr = np.array([rd[1] for rd in rdiff]).T,
                fmt='ko'
            )
        ax.legend(fontsize=18, loc="lower right")
        rax.set_xlabel(specs["label"])
        ax.set_ylabel("Fraction of |$Z_{reco}$ - $Z_{true}$| < 10 mm")
        rax.set_ylabel("$rel\ diff$")
        ax.set_ylim(*y_lims[var][channel]["ax"])
        rax.set_ylim(*y_lims[var][channel]["rax"])
        ax.set_xlim(left=0.)
        rax.set_xlim(left=0.)

        output_name = "{}_id_efficiency".format(var)
        hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
        fig.savefig("{}/{}.png".format(output_dir, output_name), bbox_inches='tight')
        fig.savefig("{}/{}.pdf".format(output_dir, output_name), bbox_inches='tight')

        logger.info("Dumped plot in {}".format(output_dir))



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
