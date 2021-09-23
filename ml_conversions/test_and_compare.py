import ROOT
import pickle
from training import load_data
import matplotlib.pyplot as plt
import mplhep as hep
import xgboost
hep.style.use("CMS")
from training import load_data
from data_preparation import variables

if __name__ == "__main__":
    x, y_true, w = load_data("test_signal.root", "test_background.root")
    
    # Load trained models
    tmva_model = ROOT.TMVA.Experimental.RBDT[""]("BDT", "classifier.root")
    with open("classifier.pkl", "rb") as f:
        xgb_model = pickle.load(f)

    # Make predictions
    print("Predicting with TMVA")
    y_pred_tmva = tmva_model.Compute(x).squeeze()
    print("Predicting with XGBoost")
    tmpmatrix = xgboost.DMatrix(x, feature_names=variables)
    y_pred_xgboost = xgb_model.get_booster().predict(tmpmatrix)

    # Plot
    bins = 100
    rng = (0, 1)

    fig, (up, down) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": (1, 1)}
        )

    up.hist(y_pred_xgboost, bins=bins, range=rng, histtype="step", label="XGBoost", linewidth=2)
    up.hist(y_pred_tmva, bins=bins, range=rng, histtype="step", label="TMVA", linewidth=2)

    up.set_xlabel("Scores")
    up.legend(fontsize=18, loc="upper right")

    down.hist(100 * (y_pred_xgboost - y_pred_tmva) / y_pred_tmva, 
              bins=500,
              range=(-100, 100),
              histtype="step",
              density=True,
              color="black",
              linewidth=2
             )
    down.set_xlabel("$(XGB - TMVA)/TMVA$ [%]")
    down.set_yscale("log")

    fig.tight_layout()

    fig.savefig("xgb_vs_tmva.png", bbox_inches='tight')
    fig.savefig("xgb_vs_tmva.pdf", bbox_inches='tight')

    fig, ax = plt.subplots()
    ax.scatter(y_pred_xgboost, y_pred_tmva)
    ax.set_xlabel("XGBoost")
    ax.set_ylabel("TMVA")

    fig.savefig("xgb_vs_tmva_scatter.png", bbox_inches='tight')
    fig.savefig("xgb_vs_tmva_scatter.pdf", bbox_inches='tight')