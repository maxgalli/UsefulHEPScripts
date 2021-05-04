import uproot
import awkward as ak
import coffea.hist as hist
import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep
import zfit
from scipy.stats import chisquare
from rich.logging import RichHandler

import logging
logger = logging.getLogger(__name__)

hep.set_style("CMS")

def setup_logging(level=logging.INFO):
    logger = logging.getLogger()

    logger.setLevel(level)
    formatter = logging.Formatter("%(message)s")

    stream_handler = RichHandler(show_time=False, rich_tracebacks=True)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def EBEB_mask(df):
    return np.maximum(abs(df.lead_eta), abs(df.sublead_eta)) < 1.5

def EBEE_mask(df):
    return np.logical_and(
            np.minimum(abs(df.lead_eta), abs(df.sublead_eta)) < 1.5,
            np.maximum(abs(df.lead_eta), abs(df.sublead_eta)) > 1.5
            )

def EEEE_mask(df):
    return np.maximum(abs(df.lead_eta), abs(df.sublead_eta)) > 1.5

def format_fit_info(data, result, res,*args):
    mu1_est = result.params[args[0]]["value"]
    sigma1_est = result.params[args[1]]["value"]
    mu2_est = result.params[args[2]]["value"]
    sigma2_est = result.params[args[3]]["value"]
    n_est = result.params[args[4]]["value"]
    alpha_est = result.params[args[5]]["value"]
    frac_est = result.params[args[6]]["value"]

    mu1_err = result.params[args[0]]["minuit_hesse"]["error"]
    sigma1_err = result.params[args[1]]["minuit_hesse"]["error"]
    mu2_err = result.params[args[2]]["minuit_hesse"]["error"]
    sigma2_err = result.params[args[3]]["minuit_hesse"]["error"]
    n_err = result.params[args[4]]["minuit_hesse"]["error"]
    alpha_err = result.params[args[5]]["minuit_hesse"]["error"]
    frac_err = result.params[args[6]]["minuit_hesse"]["error"]

    s = "Data:\n" \
            + "mass = {:.5f} +/- {:.5f}\n".format(np.mean(data["mass"]), np.std(data["mass"])) \
            + "sigma_m_over_m = {:.5f} +/- {:.5f}\n".format(np.mean(data["sigma_m"]), np.std(data["sigma_m"])) \
            + "\n" \
            + "Fit:\n" \
            + "mass1 = {:.5f} +/- {:.5f}\n".format(mu1_est, mu1_err) \
            + "sigma1 = {:.5f} +/- {:.5f}\n".format(sigma1_est, sigma1_err) \
            + "mass2 = {:.5f} +/- {:.5f}\n".format(mu2_est, mu2_err) \
            + "sigma2 = {:.5f} +/- {:.5f}\n".format(sigma2_est, sigma2_err) \
            + "n = {:.5f} +/- {:.5f}\n".format(n_est, n_err) \
            + "alpha = {:.5f} +/- {:.5f}\n".format(alpha_est, alpha_err) \
            + "frac = {:.5f} +/- {:.5f}\n".format(frac_est, frac_err) \
            + "\n" \
            + "chiSq / ndof = {:.5f}\n".format(res.statistic) \
            + "p_value = {:.5f}\n".format(res.pvalue)

    return s



def main():
    logger = setup_logging()

    # Needed names for files and trees
    v0_file = "/work/gallim/root_files/vertex_investigation/VertexInvestigation_vtx0/output_GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3f96409841a3cc85b911eb441562baae_USER_*.root"
    v_custom_file = "/work/gallim/root_files/vertex_investigation/VertexInvestigation/output_GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3f96409841a3cc85b911eb441562baae_USER_*.root"

    tree_name = "diphotonDumper/trees/ggH_125_13TeV_All_$SYST"

    output_dir = "/eos/home-g/gallim/www/plots/Hgg/VertexInvestigation/mass_fit"

    # Read two trees lazily
    imp_variables = ["weight", "lead_eta", "sublead_eta", "sigma_m", "mass"]

    arr_vtx0 = uproot.lazy(["{}:{}".format(v0_file, tree_name)], imp_variables)
    arr_vtxc = uproot.lazy(["{}:{}".format(v_custom_file, tree_name)], imp_variables)

    arrays = {
            "vtx0": arr_vtx0,
            "vtxc": arr_vtxc
            }

    # Define categories
    categories = {
            "EBEB": EBEB_mask,
            "EBEE": EBEE_mask,
            "EEEE": EEEE_mask
            }

    masked_arrays = {
            "EBEB": {},
            "EBEE": {},
            "EEEE": {}
            }

    histos = {}

    fits = {
            "EBEB": {},
            "EBEE": {},
            "EEEE": {}
            }

    # Define zfit objects for fits
    logger.info("Creating zfit objects")

    fit_range = [115, 135]
    obs = zfit.Space("M", limits=fit_range)
    mu1 = zfit.Parameter("mu1", 125, 120, 130)
    sigma1 = zfit.Parameter("sigma1", 1, 0.1, 10)
    mu2 = zfit.Parameter("mu2", 125, 120, 130)
    sigma2 = zfit.Parameter("sigma2", 1, 0.1, 10)
    n = zfit.Parameter("n", 1, 0, 10)
    alpha = zfit.Parameter("alpha", 1, 0, 10)
    frac = zfit.Parameter("frac", 0.5, 0, 1)

    gauss = zfit.pdf.Gauss(obs=obs, mu=mu1, sigma=sigma1)
    cb = zfit.pdf.CrystalBall(obs=obs, mu=mu2, sigma=sigma2, n=n, alpha=alpha)

    model = zfit.pdf.SumPDF(pdfs=[gauss, cb], fracs=frac)

    minimizer = zfit.minimize.Minuit()

    variables = [
            {
                "name": "mass",
                "bins": 100,
                "range": [115, 135]
            },
            {
                "name": "sigma_m",
                "bins": 80,
                "range": [0., 0.035]
            }
        ]

    # Loop over categories
    for cat_name, func in categories.items():
        logger.info("Working with category {}".format(cat_name))
        for vtx_name, arr in arrays.items():
            masked_arrays[cat_name][vtx_name] = arr[func(arr)]

        histos[cat_name] = hist.Hist(
                "Density",
                hist.Cat("vertex", "Vertex"),
                *[hist.Bin(spec["name"], spec["name"], spec["bins"], *spec["range"]) for spec in variables]
                )
        # fill histos
        for vtx_name, arr in masked_arrays[cat_name].items():
            histos[cat_name].fill(vertex=vtx_name, mass=arr["mass"], sigma_m=arr["sigma_m"], weight=arr["weight"])

        # Plot superimposed vertex values for mass and sigma_m (from flashgg)
        for var in variables:
            logger.info("Creating plot for variable {}".format(var["name"]))

            fig, ax = plt.subplots()
            loc_vars = [sp["name"] for sp in variables]
            loc_vars.remove(var["name"])
            hist.plot1d(histos[cat_name].sum(*loc_vars), density=True)
            output_name = "{}_{}".format(var["name"], cat_name)
            hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
            fig.savefig("{}/{}.png".format(output_dir, output_name), bbox_inches='tight')
            fig.savefig("{}/{}.pdf".format(output_dir, output_name), bbox_inches='tight')

        # Fits
        logger.info("Proceed with fits")
        x = np.linspace(115, 135, 1000) # x values for model in plots
        for vtx_name, arr in masked_arrays[cat_name].items():
            data = zfit.Data.from_numpy(obs=obs, array=arr["mass"].to_numpy())
            nll = zfit.loss.UnbinnedNLL(model=model, data=data)
            fits[cat_name]["result"] = minimizer.minimize(nll)
            fits[cat_name]["param_errors"] = fits[cat_name]["result"].hesse()

            # Compute chi-square and p-value
            logger.info("Computing goodness of fit")
            parameters = [mu1, sigma1, mu2, sigma2, n, alpha, frac]
            observed_values, observed_edges = np.histogram(arr["mass"].to_numpy(), variables[0]["bins"], variables[0]["range"])
            observed_centers = .5*(observed_edges[1:] + observed_edges[:-1])
            plot_scale = len(arr["mass"]) / variables[0]["bins"] * obs.area().numpy()
            expected_values = model.pdf(observed_centers).numpy() * plot_scale
            res = chisquare(observed_values, f_exp=expected_values)
            textstr = format_fit_info(arr, fits[cat_name]["result"], res, *parameters)
            logger.info(textstr)

            # Plot superimposed histogram and model
            logger.info("Creating plot for category {}, vertex {} with model".format(cat_name, vtx_name))
            fig, ax = plt.subplots()
            y = model.pdf(x, norm_range=fit_range).numpy()
            plt.plot(x, y, label="Model")
            err_opts = {
                'linestyle': 'none',
                'marker': '.',
                'markersize': 10.,
                'color': 'k',
                'elinewidth': 1,
                }
            hist.plot1d(
                    histos[cat_name].sum("sigma_m")[vtx_name],
                    density=True,
                    error_opts=err_opts
                    )

            # Stats box
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12, verticalalignment='top', bbox=props)

            output_name = "mass_{}_{}_with_model".format(vtx_name, cat_name)
            hep.cms.label(loc=0, data=True, llabel="Work in Progress", rlabel="", ax=ax, pad=.05)
            fig.savefig("{}/{}.png".format(output_dir, output_name), bbox_inches='tight')
            fig.savefig("{}/{}.pdf".format(output_dir, output_name), bbox_inches='tight')


if __name__ == "__main__":
    main()
