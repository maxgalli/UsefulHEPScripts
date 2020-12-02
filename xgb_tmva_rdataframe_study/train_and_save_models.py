import ROOT
import numpy as np
import pickle

from prepare_data_with_sys import variables


def load_data(signal_filename, background_filename):
    # Read data from ROOT files
    data_sig = ROOT.RDataFrame("Events", signal_filename).AsNumpy()
    data_bkg = ROOT.RDataFrame("Events", background_filename).AsNumpy()

    # Convert inputs to format readable by machine learning tools
    x_sig = np.vstack([data_sig[var] for var in variables]).T
    x_bkg = np.vstack([data_bkg[var] for var in variables]).T
    x = np.vstack([x_sig, x_bkg])

    # Create labels
    num_sig = x_sig.shape[0]
    num_bkg = x_bkg.shape[0]
    y = np.hstack([np.ones(num_sig), np.zeros(num_bkg)])

    # Compute weights balancing both classes
    num_all = num_sig + num_bkg
    w = np.hstack([np.ones(num_sig) * num_all / num_sig, np.ones(num_bkg) * num_all / num_bkg])

    return x, y, w

if __name__ == "__main__":
    # Load data
    x, y, w = load_data("train_sys_signal.root", "train_sys_background.root")

    # Fit xgboost model
    from xgboost import XGBClassifier
    bdt = XGBClassifier(max_depth=3, n_estimators=500)
    bdt.fit(x, y, w)
    pickle.dump(bdt, open("classifier.pkl", "wb"))

    # Save model in TMVA format
    ROOT.TMVA.Experimental.SaveXGBoost(bdt, "myBDT", "classifier.root")
