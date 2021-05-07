import ROOT
import os
from array import array

from utils import parse_arguments
from utils import file_names_tmpl
from utils import tree_name
from utils import setup_logging

import logging
logger = logging.getLogger(__name__)


def main(args):
    logger = setup_logging()

    v0_input_dir = args.v0_input_dir
    vcustom_input_dir = args.vcustom_input_dir
    output_dir = args.output_dir
    channel = args.channel

    # Needed names for files and trees
    file_dirs = {
            "v0": v0_input_dir,
            "vcustom": vcustom_input_dir
            }

    fit_colors = {
            "v0": "kGreen",
            "vcustom": "kRed"
            }

    tree_name = "diphotonDumper/trees/ggH_125_13TeV_All_$SYST"

    categories = {
            "EBEB": "max(abs(lead_eta), abs(sublead_eta)) < 1.5",
            "EBEE": "min(abs(lead_eta), abs(sublead_eta)) < 1.5 && max(abs(lead_eta), abs(sublead_eta)) > 1.5",
            "EEEE" : "max(abs(lead_eta), abs(sublead_eta)) > 1.5"
            }

    for vtx_name, direc in file_dirs.items():
        logger.info("Working with vertex {}".format(vtx_name))
        for cat_name, cut in categories.items():
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
            mu = ROOT.RooRealVar("mu", "mu", 125, 120, 135)
            sigma = ROOT.RooRealVar("sigma", "sigma", 1, 0.1, 10)
            mu_cb = ROOT.RooRealVar("mu_cb", "mu_cb", 125, 100, 140)
            sigma_cb = ROOT.RooRealVar("sigma_cb", "sigma_cb", 4, 0.1, 10)
            alpha = ROOT.RooRealVar("alpha", "alpha", 1, 0, 20)
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

            del mu, sigma, mu_cb, sigma_cb, alpha, n, frac, gauss, cb, model, fit_result, mass_frame



if __name__ == "__main__":
    args = parse_arguments()
    main(args)
