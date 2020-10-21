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

def write_histos(chain, output_file, variables = None):
    if variables is None:
        variables = []
    ROOT.EnableImplicitMT(10)
    rdf = ROOT.RDataFrame(chain)
    if variables:
        r_rst_ptrs = [rdf.Histo1D(var) for var in variables]
    else:
        r_rst_ptrs = [rdf.Histo1D(column) for column in rdf.GetColumnNames()]
    f = ROOT.TFile(output_file, 'RECREATE')
    for ptr in r_rst_ptrs:
        histo = ptr.GetValue()
        histo.Write()
    f.Close()

    return rdf

def main():

    # Data
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_data_UL17/'
    file_name = 'output_SingleElectron_alesauva-UL2017-10_6_4-v0-Run2017{}-09Aug2019_UL2017{}_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/Data_13TeV_All'
    output_file = 'tnp_data.root'
    runs_id = [('B', '-v1-8940b7b9416f1cbf6fbb86981f4883ea'), ('C', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('D', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('E', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('F', '_rsb-v2-c086301171e46d9c80ca640d553ab2cd')]
    variables = ['probePhoIso03', 'probeChIso03worst', 'probeChIso03', 'probePhoIdMVA', 'probeFull5x5_r9', 'probeSigmaIeIe', 'probeCovarianceIeIp', 'probeEtaWidth_Sc', 'probePhiWidth_Sc', 'probeS4']

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path, runs_id)

    # Create RDataFrame and write histos
    rdf = write_histos(chain, output_file, variables)

    # Simulation
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_mc_UL17'
    file_name = 'output_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_alesauva-UL2017-10_6_4-v2-RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2-c148a697ba5b08ec1e824b73db044236_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/DYJetsToLL_amcatnloFXFX_13TeV_All'
    output_file = 'tnp_mc.root'
    variables = variables + ['probeChIso03worst_uncorr', 'probeChIso03_uncorr', 'probePhoIdMVA_uncorr', 'probeSigmaIeIe_uncorr', 'probeCovarianceIeIp_uncorr', 'probeS4_uncorr']

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path)

    # Create RDataFrame and write histos
    rdf = write_histos(chain, output_file, variables)

if __name__ == "__main__":
    main()
