import pickle
import matplotlib.pyplot as plt
import numpy as np
from uncertainties import ufloat
import mplhep as hep

from utils import parse_arguments
from utils import file_names_tmpl
from utils import setup_logging

import logging
logger = logging.getLogger(__name__)

hep.set_style("CMS")



def rel_diff(a, b):
    num = a - b
    num = abs(num)
    den = a if a.n > b.n else b

    return num / den

def main(args):
    logger = setup_logging()

    output_dir = args.output_dir
    channel = args.channel

    pkl_name = "sigma_m_final_plots_specs_{}.pkl".format(channel)
    logger.info("Found file {}".format(pkl_name))

    with open(pkl_name, "rb") as fl:
        plots_specs = pickle.load(fl)

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

    for vtx_name, cat_specs in plots_specs.items():
        ax.errorbar(
                x_s[vtx_name], 
                [cat_spec["fitted_sigma"] for cat_spec in plots_specs[vtx_name].values()],
                yerr=[cat_spec["fitted_sigma_unc"] for cat_spec in plots_specs[vtx_name].values()],
                fmt=fmts[vtx_name], 
                label=vtx_name
                )
    rax_y = [rel_diff(s0, sc) for s0, sc in zip(
        [ufloat(cat_spec["fitted_sigma"], cat_spec["fitted_sigma_unc"]) for cat_spec in plots_specs["Vertex 0th"].values()],
        [ufloat(cat_spec["fitted_sigma"], cat_spec["fitted_sigma_unc"]) for cat_spec in plots_specs["Vertex Reco"].values()])
        ]

    logger.info("Relative differences: {}".format(rax_y))

    rax.errorbar(
            x_s["Vertex 0th"], 
            [val.n for val in rax_y],
            yerr = [val.s for val in rax_y],
            fmt="ko"
            )

    for x in [ax, rax]:
        for cat in plots_specs["Vertex 0th"].values():
            low = cat["range"][0]
            x.axvline(low, color="black", alpha=0.4)

    rax.set_xlabel("$\sigma_M / M$")
    ax.set_ylabel("$\sigma_{fitted}$")
    rax.set_ylabel("$rel\ diff$")
    ax.set_xlim(0.)
    ax.set_ylim(0.)
    rax.set_ylim(-0.01, 0.2)
    ax.legend(loc="upper left")
    ax.grid(which="both")
    rax.grid(which="both")

    hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
    fig.savefig("{}/all_categories.png".format(output_dir), bbox_inches='tight')
    fig.savefig("{}/all_categories.pdf".format(output_dir), bbox_inches='tight')



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
