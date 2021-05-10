import pickle
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep

from utils import parse_arguments
from utils import file_names_tmpl
from utils import setup_logging

import logging
logger = logging.getLogger(__name__)

hep.set_style("CMS")



def rel_diff(a, b):
    return abs(a - b) / max(a, b)

def main(args):
    logger = setup_logging()

    output_dir = args.output_dir
    channel = args.channel

    pkl_name = "sigma_m_final_plots_specs_{}.pkl".format(channel)
    logger.info("Found file {}".format(pkl_name))

    with open(pkl_name, "rb") as fl:
        plots_specs = pickle.load(fl)

    x_v0 = [cat_spec["range"][0] + abs(cat_spec["range"][1] - cat_spec["range"][0]) / 2 for cat_spec in plots_specs["v0"].values()]
    x_vcustom = [cat_spec["range"][0] + abs(cat_spec["range"][1] - cat_spec["range"][0]) / 2 for cat_spec in plots_specs["vcustom"].values()]
    x_s = {
            "v0": x_v0,
            "vcustom": x_vcustom
            }
    fmts = {
            "v0": "r^",
            "vcustom": "sb"
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
        [cat_spec["fitted_sigma"] for cat_spec in plots_specs["v0"].values()],
        [cat_spec["fitted_sigma"] for cat_spec in plots_specs["vcustom"].values()])
        ]
    rax_y_rel_unc = [
            np.sqrt((v0_specs["fitted_sigma_unc"] / v0_specs["fitted_sigma"])**2 \
                    + (vcustom_specs["fitted_sigma_unc"]/vcustom_specs["fitted_sigma"])**2) for v0_specs, vcustom_specs in zip(list(plots_specs["v0"].values()), list(plots_specs["vcustom"].values()))]
    rax_y_abs_unc = [val*unc for val, unc in zip(rax_y, rax_y_rel_unc)]
    rax.errorbar(
            x_s["v0"], 
            rax_y,
            yerr = rax_y_abs_unc,
            fmt="ko"
            )

    for x in [ax, rax]:
        for cat in plots_specs["v0"].values():
            low = cat["range"][0]
            x.axvline(low, color="black", alpha=0.4)

    rax.set_xlabel("$\sigma_M / M$")
    ax.set_ylabel("$\sigma_{fitted}$")
    rax.set_ylabel("$rel\ diff$")
    ax.set_xlim(0.)
    ax.set_ylim(0.)
    rax.set_ylim(-0.01, 0.2)
    ax.legend()
    hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
    fig.savefig("{}/allbin.png".format(output_dir), bbox_inches='tight')
    fig.savefig("{}/allbin.pdf".format(output_dir), bbox_inches='tight')



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
