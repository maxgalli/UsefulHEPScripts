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
        for num in range(1, number):
            chain.Add(base_dir + '/' + file_name.format(num) + '/' + tree_path)

    return chain

def dump_snapshot(chain, output_file, output_tree_name, variables = None):
    ROOT.EnableImplicitMT()
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
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/20201130_data_UL18'
    file_name = 'output_EGamma_alesauva-UL2018_0-10_6_4-v0-Run2018{}-12Nov2019_UL2018-{}-981b04a73c9458401b9ffd78fdd24189_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/Data_13TeV_All'
    output_file = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputData_2018.root'
    runs_id = [('A', 'v2'), ('B', 'v2'), ('C', 'v2'), ('D', 'v4')]

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path, runs_id)

    # Create RDataFrame and write histos
    rdf = dump_snapshot(chain, output_file, tree_path)

    # Simulation
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/20201130_mc_UL18'
    file_name = 'output_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2-b5e482a1b1e11b6e5da123f4bf46db27_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/DYJetsToLL_amcatnloFXFX_13TeV_All'
    output_file = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/tnp_merged_outputs/outputMC_2018.root'

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path)

    # Create RDataFrame and write histos
    rdf = dump_snapshot(chain, output_file, tree_path)

if __name__ == "__main__":
    main()
