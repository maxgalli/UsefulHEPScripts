This folder includes a study performed to investigate the possibility of  
efficiently apply tags and systematics in an RDataFrame analysis flow.  
The application would be the new flashgg framework.  
  
The idea consists in train a model with XGBoost for some variables and then  
apply it, in the context of an RDataFrame flow, to a new dataset which has the  
same variables the model was trained with plus two "modified" versions (Up and  
Down, which represent the systematics).  
  
### Workflow
* ```prepare_data_with_sys.py```: this program fetches two different remote datasets, ```SMHiggsToZZTo4L.root``` and ```ZZTo2e2mu.root```, which will be respectively our signal and background. Data is processed to flatten the variable of interest (```Muon_pt_1```, ```Muon_pt_2```, ```Electron_pt_1```, ```Electron_pt_2```) and ```Define``` is applied to produce fake branches of systematic variations (variables + ```_Up``` and variables + ```_Down```), for a total amount of 12 branches in each dataset (signal and background). Then, both datasets are split into training and test, ending up with ```train_sys_signal.root```, ```train_sys_background.root```, ```test_sys_signal.root``` and ```test_sys_background.root```.
* ```train_and_save_models.py```: here we use XGBoost to train a classifiers that separates signal events from background events. The classifier is saved into two different formats: plain XGBoost in ```classifier.pkl``` and in TMVA digestible format as ```myBDT``` inside ```classifier.root```.
*  ```test_jitting.py```: here we set-up a trick (necessary due to the fact that ```RDataFrame.Define``` accepts strings of C++ code as arguments) to conveniently make signal-bkg predictions for the events stored in ```test_sys_signal.root```, ending up in the branches ```y```, ```y_up``` and ```y_down```. The bdt is set up only once for the three predictions. The predictions for the first 200 events are printed (run with ```python test_jitting.py > test_jitting.log``` to store it in a log file).

### Double-check
Run ```python test_pure_xgb.py > test_pure_xgb.log``` to perform the test for signal dataset using only XGBoost from Python and compare the results.
