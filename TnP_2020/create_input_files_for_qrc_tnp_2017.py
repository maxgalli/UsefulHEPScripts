"""
27.10.2020

This script creates the following output files:
    /eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputData.root
    /eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputMC.root

The first is produced by merging in a single root file all the root files found in:
    /eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_data_UL17
by using RDataFrame.Snapshot; the second does the same operation but with the files found in:
    /eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_mc_UL17


Where do these files come from?

The files in the two directories above mentioned were the results of running
    https://github.com/maxgalli/flashgg/blob/my_TagAndProbe/Validation/test/runUL2017.sh
which produces the tag and probe output ntuples.


What do I need it for?

outputData.root and outputMC.root are the files that work as input for:
    https://github.com/maxgalli/qRC/blob/development/legacy/training/make_dataframes.py
At a second time, of course, this file will be changed in order to perform the operation performed
here directly there (i.e. a list of multiple root files can be given as input instead of a single one).
"""

import ROOT

def fill_tchain(base_dir, file_name, number, tree_path, runs_id = None):
    if runs_id is None:
        runs_id = []

    chain = ROOT.TChain()
    if runs_id:
        for ri in runs_id:
            for num in range(number):
                chain.Add(base_dir + '/' + file_name.format(ri[0], ri[1], num) + '/' + tree_path)
    else:
        for num in range(number):
            chain.Add(base_dir + '/' + file_name.format(num) + '/' + tree_path)

    return chain

def dump_snapshot(chain, output_file, output_tree_name, variables = None):
    ROOT.EnableImplicitMT(10)
    rdf = ROOT.RDataFrame(chain)
    f = ROOT.TFile(output_file, 'RECREATE')
    if variables:
        rdf.Snapshot(output_tree_name, output_file, variables)
    else:
        rdf.Snapshot(output_tree_name, output_file)
    f.Close()

    return rdf

def main():

    # Data
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_data_UL17'
    file_name = 'output_SingleElectron_alesauva-UL2017-10_6_4-v0-Run2017{}-09Aug2019_UL2017{}_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/Data_13TeV_All'
    output_file = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputData.root'
    runs_id = [('B', '-v1-8940b7b9416f1cbf6fbb86981f4883ea'), ('C', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('D', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('E', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('F', '_rsb-v2-c086301171e46d9c80ca640d553ab2cd')]

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path, runs_id)

    # Create RDataFrame and write histos
    rdf = dump_snapshot(chain, output_file, tree_path)

    # Simulation
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/02112020_mc_UL17'
    file_name = 'output_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_alesauva-UL2017-10_6_4-v2-RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2-c148a697ba5b08ec1e824b73db044236_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/DYJetsToLL_amcatnloFXFX_13TeV_All'
    output_file = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputMC.root'

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path)

    # Create RDataFrame and write histos
    rdf = dump_snapshot(chain, output_file, tree_path)

if __name__ == "__main__":
    main()
