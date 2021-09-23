# ML Conversions

Goal of this subfolder is to have quick reproducers to investigate conversions between different ML tools.

## XGBoost vs TMVA

Three scripts for this:

- ```data_preparation.py```: taken from [here](https://root.cern/doc/master/tmva100__DataPreparation_8py.html)
- ```training.py```: taken from [here](https://root.cern/doc/master/tmva101__Training_8py.html)
- ```test_and_compare.py```: based on [this](https://root.cern/doc/master/tmva102__Testing_8py.html); produces the usual superimposed shapes and a scatter plot
- ```produce_xml_file.py```: uses the train samples produced before to train a BDT in the standard TMVA way; the result is dumped to ```dataset/weights/TMVAClassification_BDT.weights.xml```
- ```compare_xgb_tmva_jonas.py``` requires that the xml file produced in the previous step is converted to an xgboost model using [this tool](https://github.com/guitargeek/tmva-to-xgboost) (dump to ```dataset/weights/TMVAClassification_BDT.weights.json```); dumps the usual plot of comparison in the current directory
