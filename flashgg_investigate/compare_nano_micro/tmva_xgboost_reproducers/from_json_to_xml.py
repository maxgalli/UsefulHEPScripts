""" Use PyMVA experimental tools to convert JSON (XGBoost) to XML
"""
import ROOT
import xgboost



def main():
    #booster = xgboost.Booster()
    #booster.load_model("bdt.json")
    bdt = xgboost.XGBClassifier()
    bdt.load_model("bdt_original.json")
    bdt.max_depth = 6
    bdt._features_count = 12

    ROOT.TMVA.Experimental.SaveXGBoost(bdt, "BDT", "bdt_original.root")


if __name__ == "__main__":
    main()