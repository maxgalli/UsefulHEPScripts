# Nano - Micro Comparison

## XGBoost - TMVA

```compare_xgb_tmva.py``` is meant to compare the shapes coming from the same models using XGBoost and plain TMVA.
The input is the dataframe dumped when running ```dump_plots.py```: it contains variables which refer to both the lead and sublead
photon coming from both their Nano and Micro version (names of the variables can be different in Nano and Micro; if this is not the case,
suffixes _nano and _micro are appended).

The quantity compared using XGBoost and TMVA is the PhotonIDMVA of the leading photon (barrel). For UL2017-EB, flashgg has a model trained and applied in TMVA
which can be found [here](https://github.com/cms-analysis/flashgg/blob/dev_legacy_runII/MetaData/data/MetaConditions/Era2017_legacy_v1.json#L37).
To be applied inside [this branch](https://github.com/maxgalli/hgg-coffea/tree/photonIDMVA) of hgg-coffea, [this tool](https://github.com/guitargeek/tmva-to-xgboost) was used to convert it to JSON (note the transform applied in [this line](https://github.com/guitargeek/tmva-to-xgboost)).

The pure TMVA (original) version is applied inside the ```compare_xgb_tmva.py``` script itself.

The comparison can be seen [here](https://gallim.web.cern.ch/gallim/plots/Hgg/NanoMicroCompare/lead_nano_cfr_tmva.png).