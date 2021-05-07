import ROOT
import uproot
import numpy as np
import os
from array import array
from itertools import combinations
from scipy.optimize import minimize
import pickle

from utils import parse_arguments
from utils import file_names_tmpl
from utils import tree_name
from utils import setup_logging

import logging
logger = logging.getLogger(__name__)


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


def eff_sigma_unc(
        d_sigma_eff_over_v_gauss, d_sigma_eff_over_v_cb,
        d_sigma_eff_over_frac,
        v_v_gauss, v_v_cb, v_frac,
        cov_v_gauss_v_cb, cov_v_gauss_frac, cov_v_cb_frac):

    var = d_sigma_eff_over_v_gauss**2 * v_v_gauss + d_sigma_eff_over_v_cb**2 * v_v_cb + d_sigma_eff_over_frac**2 * v_frac + 2 * d_sigma_eff_over_v_gauss * d_sigma_eff_over_v_cb * cov_v_gauss_v_cb + 2 * d_sigma_eff_over_v_gauss * d_sigma_eff_over_frac * cov_v_gauss_frac + 2 * d_sigma_eff_over_v_cb * d_sigma_eff_over_frac * cov_v_cb_frac

    return np.sqrt(var)


def main(args):
    logger = setup_logging()

    v0_input_dir = args.v0_input_dir
    vcustom_input_dir = args.vcustom_input_dir
    output_dir = args.output_dir
    channel = args.channel

    final_plots_specs = {}

    # Needed names for files and trees
    file_dirs = {
            "v0": v0_input_dir,
            "vcustom": vcustom_input_dir
            }

    fit_colors = {
            "v0": "kGreen",
            "vcustom": "kRed"
            }

    # Create sigma_m_over_m categories
    logger.info("Creating categories of SigmaMOverM")
    file_format = {
            "v0": v0_input_dir + "/" + file_names_tmpl[channel],
            "vcustom": vcustom_input_dir + "/" + file_names_tmpl[channel]
            }

    categories = {}
    smom = "sigma_m" # due to how we defined it in flashgg, it's already divided by M
    for vtx_name, direc in file_format.items():
        categories[vtx_name] = {}
        final_plots_specs[vtx_name] = {}

        arr = uproot.concatenate(["{}:{}".format(direc, tree_name)], expressions=[smom], library="ak")
        arr = np.asarray([ev[0] for ev in arr.to_numpy()])

        cut_format = "{var} > {min_edge} && {var} < {max_edge}"
        edge_min = 0.
        edge_max = 0.035
        n_bins = 5
        edges = get_edges(arr, edge_min, edge_max, n_bins)

        low = edges[0]
        for high in edges[1:]:
            cat_name = "SigmaMOverM_{:.5f}-{:.5f}".format(low, high)
            cat_string = cut_format.format(var=smom, min_edge=low, max_edge=high)
            categories[vtx_name][cat_name] = cat_string

            final_plots_specs[vtx_name][cat_name] = {}
            final_plots_specs[vtx_name][cat_name]["range"] = (low, high)

            low = high

    logger.info("Created categories {}".format(categories))

    for vtx_name, direc in file_dirs.items():
        logger.info("Working with vertex {}".format(vtx_name))
        for cat_name, cut in categories[vtx_name].items():
            logger.info("Working with category {}".format(cat_name))

            chain = ROOT.TChain()
            files = [fl for fl in os.listdir(direc) if fl.startswith(file_names_tmpl[channel][:20])]
            for fl in files:
                chain.Add("{}/{}/{}".format(direc, fl, tree_name))
            rdf = ROOT.RDataFrame(chain)
            rdf_cut = rdf.Filter(cut)
            mass_arr = rdf_cut.Take[float]("mass").GetValue()
            weight_arr = rdf_cut.Take[float]("weight").GetValue()
            mass_fake_arr = array("d", [0.])
            weight_fake_arr = array("d", [0.])
            cut_tree = ROOT.TTree("cut_tree", "cut_tree")
            cut_tree.Branch("mass", mass_fake_arr, "mass/D")
            cut_tree.Branch("weight", weight_fake_arr, "weight/D")
            for ev_mass, ev_weight in zip(mass_arr, weight_arr):
                mass_fake_arr[0] = ev_mass
                weight_fake_arr[0] = ev_weight
                cut_tree.Fill()

            # RooFit objects
            mass = ROOT.RooRealVar("mass", "Invariant mass [GeV]", 125, 115, 135)
            weight = ROOT.RooRealVar("weight", "weight", -1, 1)
            mu = ROOT.RooRealVar("mu", "mu", 125, 120, 130)
            sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.1, 10)
            mu_cb = ROOT.RooRealVar("mu_cb", "mu_cb", 125, 120, 130)
            sigma_cb = ROOT.RooRealVar("sigma_cb", "sigma_cb", 4, 0.1, 10)
            alpha = ROOT.RooRealVar("alpha", "alpha", 1, 0, 10)
            n = ROOT.RooRealVar("n", "n", 1, 0, 5)
            frac = ROOT.RooRealVar("frac", "frac", 0.5, 0., 1.)

            gauss = ROOT.RooGaussian("gauss", "gauss", mass, mu, sigma)
            cb = ROOT.RooCBShape("cb", "cb", mass, mu_cb, sigma_cb, alpha, n)

            model = ROOT.RooAddPdf("model", "model", ROOT.RooArgList(gauss, cb), ROOT.RooArgList(frac))

            # Create (weighted) dataset
            data = ROOT.RooDataSet("data".format(cat_name), "data".format(cat_name), cut_tree, ROOT.RooArgSet(mass, weight), "", weight.GetName())

            # Fit in subrange
            mass.setRange("higgs", 120, 130)
            logger.info("Performing fit")
            fit_result = fit_result = model.fitTo(
                    data, 
                    ROOT.RooFit.Range("higgs"), 
                    ROOT.RooFit.Save(1),
                    ROOT.RooFit.AsymptoticError(1)
                    )

            # Plot decoration
            mass_frame = mass.frame(ROOT.RooFit.Title("Mass-{}-{}".format(vtx_name, cat_name)))
            mass_frame.GetYaxis().SetTitleOffset(1.6)
            data.plotOn(mass_frame, ROOT.RooFit.DataError(ROOT.RooAbsData.SumW2))
            model.plotOn(mass_frame, ROOT.RooFit.LineColor(getattr(ROOT, fit_colors[vtx_name])))
            chi_sq = mass_frame.chiSquare()
            model.paramOn(mass_frame, ROOT.RooFit.Layout(0.65), ROOT.RooFit.Label("chiSq / ndof = {:.5f}".format(chi_sq)))
            data.statOn(mass_frame, ROOT.RooFit.Layout(0.46, 0.12, 0.95))

            # Dump plots
            logger.info("Dumping plots")
            c = ROOT.TCanvas("", "")
            mass_frame.Draw()
            c.SaveAs("{}/mass_{}_{}.png".format(output_dir, vtx_name, cat_name))
            c.SaveAs("{}/mass_{}_{}.pdf".format(output_dir, vtx_name, cat_name))

            # Fill values for final plots
            parameters = {var.GetName(): var.getVal() for var in list(model.getParameters(data))}

            # See https://root-forum.cern.ch/t/how-to-calculate-effective-sigma/39472/3
            final_plots_specs[vtx_name][cat_name]["fitted_sigma"] = np.sqrt(
                    (parameters["sigma"]**2)*parameters["frac"] \
                    + (parameters["sigma_cb"]**2)*(1 - parameters["frac"])
                    )
            
            # Propagate uncertainty on sigma effective

            # To get the covariances from fit result, remember the indexes
            cov_matrix = fit_result.covarianceMatrix()
            frac_index = 1
            sigma_gauss_index = 5
            sigma_cb_index = 6

            var_frac = cov_matrix[frac_index][frac_index]
            var_v_gauss = cov_matrix[sigma_gauss_index][sigma_gauss_index]
            var_cb_index = cov_matrix[sigma_cb_index][sigma_cb_index]

            cov_v_gauss_v_cb = cov_matrix[sigma_gauss_index][sigma_cb_index]
            cov_v_gauss_frac = cov_matrix[sigma_gauss_index][frac_index]
            cov_v_cb_frac = cov_matrix[sigma_cb_index][frac_index]
           

            final_plots_specs[vtx_name][cat_name]["fitted_sigma_unc"] = eff_sigma_unc(
                    parameters["frac"], 
                    1 - parameters["frac"], 
                    parameters["sigma"] - parameters["sigma_cb"],
                    var_v_gauss, var_cb_index, var_frac,
                    cov_v_gauss_v_cb, cov_v_gauss_frac, cov_v_cb_frac
                    )

            del mu, sigma, mu_cb, sigma_cb, alpha, n, frac, gauss, cb, model, fit_result, mass_frame

    logger.info("Dumping final plots specifications: {}".format(final_plots_specs))

    with open("sigma_m_final_plots_specs_{}.pkl".format(channel), "wb") as fl:
        pickle.dump(final_plots_specs, fl)



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
