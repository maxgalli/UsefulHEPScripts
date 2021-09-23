import ROOT
from data_preparation import variables


if __name__ == "__main__":
    train_signal = "train_signal.root"
    train_background = "train_background.root"
    output_file = "TMVA_ClassificationOutput.root"

    ROOT.TMVA.Tools.Instance()
    output = ROOT.TFile(output_file, "RECREATE")
    factory = ROOT.TMVA.Factory("TMVAClassification", output, "!V:ROC:!Silent:Color:!DrawProgressBar:AnalysisType=Classification")

    train_signal_input = ROOT.TFile(train_signal)
    train_background_input = ROOT.TFile(train_background)

    s_tree = train_signal_input.Get("Events")
    b_tree = train_background_input.Get("Events")

    loader = ROOT.TMVA.DataLoader("dataset")

    loader.AddSignalTree(s_tree)
    loader.AddBackgroundTree(b_tree)

    for var in variables:
        loader.AddVariable(var, "F")

    # Modify number of events for training (default is half, pick all)
    cut_s = ""
    cut_b = ""
    loader.PrepareTrainingAndTestTree(cut_s, cut_b, 
    "nTrain_Signal={}:nTrain_Background={}:SplitMode=Random:NormMode=NumEvents:!V".format(s_tree.GetEntries(), b_tree.GetEntries()))

    factory.BookMethod(loader, ROOT.TMVA.Types.kBDT, "BDT", 
    "!V:NTrees=200:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20"
    )

    factory.TrainAllMethods()
    #factory.TestAllMethods()
    #factory.EvaluateAllMethods()
    output.Close()
