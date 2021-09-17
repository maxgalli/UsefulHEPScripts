# TMVA vs XGBoost

This is yet another subfolder to make the XGBoost-TMVA comparison more clear.
```lead_processed_nano.root``` contains the input variables for the BDT after correction, coming from the nanoaods produced like explained in the upper level.
The XGBoost and TMVA models are called ```bdt.json``` and ```bdt.xml``` for simplicity.
```compare_xgb_tmva.py``` applied the two models one after the other and dumps two plots: one with the two distributions, the other with a scatter plot.
```compare_tmvas.py``` compares two different ways of performing inference with TMVAi (not particularly meaningful).