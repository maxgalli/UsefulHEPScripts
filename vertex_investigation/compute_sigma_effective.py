import uproot
import numpy as np
import matplotlib.pyplot as plt
import os
from itertools import combinations
from scipy.optimize import minimize
import mplhep as hep

from utils import parse_arguments
from utils import file_names_tmpl
from utils import tree_name_tmpl
from utils import setup_logging

import logging
logger = logging.getLogger(__name__)

hep.set_style("CMS")


def get_edges(arr, edge_min, edge_max, n_bins):
    """Given an array of events (sigmaM_over_M), the range and the number of bins,
    return the sequence of edges that minimizes the sum of the difference in number 
    of events between the permutations of pairs of bins.
    """
    big_num = 99999999
    def compute_total_diff(arr, edge_min, edge_max, *edges_cent):
        edges = [edge_min] + list(edges_cent) + [edge_max]
        try:
            hist, _ = np.histogram(arr, edges)
        except ValueError:
            return big_num
        diff = sum([abs(first - second) for first, second in list(combinations(hist, 2))])
        return diff
    
    n_edges = n_bins + 1
    x0 = np.linspace(edge_min, edge_max, n_edges)
    
    def diff_to_minimize(edges):
            return compute_total_diff(arr, edge_min, edge_max, *edges)
    
    res = minimize(diff_to_minimize, x0=x0[1:-1], method='Powell')
    
    return [edge_min] + list(res.x) + [edge_max]


def sigma_effective(arr):
    arr.sort()
    left = np.quantile(arr, 0.16)
    right = np.quantile(arr, 0.84)

    return right - left 

def rel_diff(a, b):
    return abs(a - b) / max(a, b)

def squared_diff(a, b):
    return np.sqrt(np.abs(a**2 - b**2))

def main(args):
    logger = setup_logging()

    v0_input_dir = args.v0_input_dir
    vcustom_input_dir = args.vcustom_input_dir
    output_dir = args.output_dir
    channel = args.channel

    tree_name = tree_name_tmpl.format(channel)

    plots_specs = {}

    # Needed names for files and trees
    file_dirs = {
            "Vertex 0th": v0_input_dir,
            "Vertex Reco": vcustom_input_dir
            }

    # Create sigma_m_over_m categories
    logger.info("Creating categories of SigmaMOverM")
    file_format = {
            "Vertex 0th": v0_input_dir + "/" + file_names_tmpl[channel],
            "Vertex Reco": vcustom_input_dir + "/" + file_names_tmpl[channel]
            }

    categories = {}
    smom = "sigma_m" # due to how we defined it in flashgg, it's already divided by M
    for vtx_name, direc in file_format.items():
        categories[vtx_name] = {}
        plots_specs[vtx_name] = {}

        arr = uproot.concatenate(["{}:{}".format(direc, tree_name)], expressions=[smom], library="ak")
        arr = np.asarray([ev[0] for ev in arr.to_numpy()])

        cut_format = "({var} > {min_edge}) & ({var} < {max_edge})"
        edge_min = 0.
        edge_max = 0.035
        n_bins = 5
        edges = get_edges(arr, edge_min, edge_max, n_bins)

        low = edges[0]
        for high in edges[1:]:
            cat_name = "SigmaMOverM_{:.5f}-{:.5f}".format(low, high)
            cat_string = cut_format.format(var=smom, min_edge=low, max_edge=high)
            categories[vtx_name][cat_name] = cat_string

            plots_specs[vtx_name][cat_name] = {}
            plots_specs[vtx_name][cat_name]["range"] = (low, high)

            low = high

    logger.info("Created categories {}".format(categories))

    for vtx_name, direc in file_dirs.items():
        logger.info("Working with vertex {}".format(vtx_name))
        for cat_name, cut in categories[vtx_name].items():
            logger.info("Working with category {}".format(cat_name))

            files = [fl for fl in os.listdir(direc) if fl.startswith(file_names_tmpl[channel][:20])]

            events = uproot.concatenate(
                [direc + "/" + fl + ":" + tree_name for fl in files],
                ["mass", "weight"],
                cut,
                library="np"
            )

            mass = events["mass"]
            plots_specs[vtx_name][cat_name]["sigma_effective"] = sigma_effective(mass) 


    # Plot
    x_v0 = [cat_spec["range"][0] + abs(cat_spec["range"][1] - cat_spec["range"][0]) / 2 for cat_spec in plots_specs["Vertex 0th"].values()]
    x_vcustom = [cat_spec["range"][0] + abs(cat_spec["range"][1] - cat_spec["range"][0]) / 2 for cat_spec in plots_specs["Vertex Reco"].values()]
    x_s = {
            "Vertex 0th": x_v0,
            "Vertex Reco": x_vcustom
            }
    fmts = {
            "Vertex 0th": "r^",
            "Vertex Reco": "sb"
            }

    fig, (ax, rax) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (3, 1)},
        sharex=True
        )

    fig.suptitle(channel)

    for vtx_name, cat_specs in plots_specs.items():
        ax.plot(
                x_s[vtx_name], 
                [cat_spec["sigma_effective"] for cat_spec in plots_specs[vtx_name].values()],
                fmts[vtx_name], 
                label=vtx_name if vtx_name == "Vertex 0th" else r"PV Run2 $H \rightarrow \gamma \gamma$"
                )

    #rax_y = [rel_diff(s0, sc) for s0, sc in zip(
    rax_y = [squared_diff(s0, sc) for s0, sc in zip(
        [plots_specs["Vertex 0th"][cat]["sigma_effective"] for cat in list(categories["Vertex 0th"].keys())],
        [plots_specs["Vertex Reco"][cat]["sigma_effective"] for cat in list(categories["Vertex Reco"].keys())]
    )]

    #logger.info("Relative differences: {}".format(rax_y))
    logger.info("Squared differences: {}".format(rax_y))

    rax.plot(
            x_s["Vertex 0th"], 
            rax_y,
            "ko"
            )

    for x in [ax, rax]:
        for cat in plots_specs["Vertex 0th"].values():
            low = cat["range"][0]
            x.axvline(low, color="black", alpha=0.4)

    rax.set_xlabel("$\sigma_M / M$")
    ax.set_ylabel("$\sigma_{effective}$")
    #rax.set_ylabel("$rel\ diff$")
    rax.set_ylabel("$\sqrt{\sigma_{\mathrm{eff}, 0}^2 - \sigma_{\mathrm{eff}, \gamma\gamma}^2}$")
    ax.set_xlim(0.)
    ax.set_ylim(0.)
    #rax.set_ylim(-0.01, 0.2)
    rax.set_ylim(-0.01, 2)
    ax.legend(loc="upper left")
    ax.grid(which="both")
    rax.grid(which="both")

    logger.info("Dumping plot in {}".format(output_dir))
    hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
    fig.savefig("{}/sigma_effective.png".format(output_dir), bbox_inches='tight')
    fig.savefig("{}/sigma_effective.pdf".format(output_dir), bbox_inches='tight')



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
