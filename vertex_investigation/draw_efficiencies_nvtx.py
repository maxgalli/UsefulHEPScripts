import uproot
import coffea.hist as hist
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import ROOT

from utils import parse_arguments
from utils import file_names_tmpl
from utils import tree_name
from utils import setup_logging

hep.set_style("CMS")

import logging
logger = logging.getLogger(__name__)



def count_fraction(awk_arr, var, limits):
    """ Given an awkward array, a variable (will be p_t) and a list of values (i.e. list of lists of variable length), loop over these values
    to compute the fraction of events with diff_z < 1. (cm).
    Return two lists containing the computed values (for each range) and theis uncertainties.
    Uncertainties are computed using ROOT.TEfficiency.ClopperPearson, and it is thus a list of elements [low, up]
    """
    vals = []
    uncs = []
    for rng in limits:
        logger.info("Working with number of vertexes {}".format(rng))
        part_arr = awk_arr[[i in rng for i in awk_arr[var]]] # Highly inefficient but no better solution found
        part_arr['diff_z'] = abs(part_arr.gen_vtx_z - part_arr.vtx_z)
        total = len(part_arr)
        passed = len(part_arr[part_arr.diff_z < 1.])
        frac = passed / total
        vals.append(frac)
        unc = [
                abs(ROOT.TEfficiency.ClopperPearson(total, passed, .99, 0) - frac),
                abs(ROOT.TEfficiency.ClopperPearson(total, passed, .99, 1) - frac)
                ]
        uncs.append(unc)

    return vals, uncs


def rel_diff(a, b):
    return abs(a - b) / max(a, b)


def main(args):
    logger = setup_logging()

    v0_input_dir = args.v0_input_dir
    vcustom_input_dir = args.vcustom_input_dir
    output_dir = args.output_dir
    channel = args.channel

    # Needed names for files and trees
    v0_file = v0_input_dir + "/" + file_names_tmpl[channel]
    v_custom_file = vcustom_input_dir + "/" + file_names_tmpl[channel]

    ranges = {
            "nvtx": {
                "range": (0, 60),
                "label": "$N_{vertices}$"
                }
            }

    for var, specs in ranges.items():
        logger.info("Working with {}".format(var))

        # Read two trees lazily
        imp_variables = [var] + ["vtx_z", "gen_vtx_z", "weight"]

        arr_vtx0 = uproot.lazy(["{}:{}".format(v0_file, tree_name)], imp_variables)
        arr_vtxc = uproot.lazy(["{}:{}".format(v_custom_file, tree_name)], imp_variables)

        # Compute quantities
        var_range = np.arange(*specs["range"])

        var_ranges = []
        start = 0
        step =  2
        for i in range(*specs["range"], step):
            var_ranges.append([i + s for s in range(step)])
            start = i

        x_vtx0, x_vtxc, y_vtx0, y_vtxc = {}, {}, {}, {}
        xs = [rng[:-1] for rng in var_ranges]
        x_vtx0["values"] = xs
        x_vtxc["values"] = xs
        x_vtx0["unc"] = np.zeros(len(var_ranges))
        x_vtxc["unc"] = np.zeros(len(var_ranges))

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

        rdiff = [rel_diff(v0, vc) for v0, vc in zip(y_vtx0["values"], y_vtxc["values"])]
        rdiff_err_low = []
        rdiff_err_up = []
        for rd, y0, yc, y0_unc, yc_unc in zip(rdiff, y_vtx0["values"], y_vtxc["values"], [unc[0] for unc in y_vtx0["unc"]], [unc[0] for unc in y_vtxc["unc"]]):
            rdiff_unc = rd * np.sqrt((y0_unc/y0)**2 + (yc_unc/yc)**2)
            rdiff_err_low.append(rdiff_unc)
        for rd, y0, yc, y0_unc, yc_unc in zip(rdiff, y_vtx0["values"], y_vtxc["values"], [unc[1] for unc in y_vtx0["unc"]], [unc[1] for unc in y_vtxc["unc"]]):
            rdiff_unc = rd * np.sqrt((y0_unc/y0)**2 + (yc_unc/yc)**2)
            rdiff_err_up.append(rdiff_unc)

        rax.errorbar(
                x_vtx0["values"], 
                rdiff,
                yerr = np.array(list(zip(rdiff_err_low, rdiff_err_up))).T,
                fmt='ko'
            )
        ax.legend(fontsize=18, loc="lower left")
        rax.set_xlabel(specs["label"])
        ax.set_ylabel("Fraction of |$Z_{reco}$ - $Z_{true}$| < 10 mm")
        rax.set_ylabel("$rel\ diff$")
        ax.set_ylim(bottom=0.)
        ax.set_xlim(left=0.)
        rax.set_ylim(0., 0.3)

        output_name = "{}_id_efficiency".format(var)
        hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
        fig.savefig("{}/{}_.png".format(output_dir, output_name), bbox_inches='tight')
        fig.savefig("{}/{}_.pdf".format(output_dir, output_name), bbox_inches='tight')

        logger.info("Dumped plot in {}".format(output_dir))


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
