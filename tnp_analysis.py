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

def write_histos(chain, output_file, var_binning = None):
    ROOT.EnableImplicitMT(10)
    rdf = ROOT.RDataFrame(chain)
    if var_binning:
        r_rst_ptrs = [rdf.Histo1D((var, var, binning[0], binning[1], binning[2]), var, 'weight') for var, binning in var_binning.items()]
    else:
        r_rst_ptrs = [rdf.Histo1D(column) for column in rdf.GetColumnNames()]
    f = ROOT.TFile(output_file, 'RECREATE')
    for ptr in r_rst_ptrs:
        histo = ptr.GetValue()
        print('Processing ptr for histo {}'.format(histo.GetName()))
        histo.Scale(1/histo.Integral())
        histo.Write()
    print('Run {} event loops'.format(rdf.GetNRuns()))
    f.Close()

    return rdf

def main():

    # Data
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_data_UL17'
    file_name = 'output_SingleElectron_alesauva-UL2017-10_6_4-v0-Run2017{}-09Aug2019_UL2017{}_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/Data_13TeV_All'
    output_file = 'tnp_data.root'
    runs_id = [('B', '-v1-8940b7b9416f1cbf6fbb86981f4883ea'), ('C', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('D', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('E', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('F', '_rsb-v2-c086301171e46d9c80ca640d553ab2cd')]
    var_binning = {
            'probePhoIso03': (100, 0, 10),
            'probeChIso03worst': (100, 0, 10),
            'probeChIso03': (100, 0, 10),
            'probePhoIdMVA': (200, -1, 1),
            'probeFull5x5_r9': (100, 0, 1),
            'probeSigmaIeIe': (400, 0, 0.04),
            'probeCovarianceIeIp': (100, -0.0005, 0.0005),
            'probeEtaWidth_Sc': (100, 0, 0.05),
            'probePhiWidth_Sc': (150, 0, 0.15),
            'probeS4': (100, 0, 1)
            }

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path, runs_id)

    # Create RDataFrame and write histos
    rdf = write_histos(chain, output_file, var_binning)

    # Simulation
    base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_mc_UL17'
    file_name = 'output_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_alesauva-UL2017-10_6_4-v2-RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2-c148a697ba5b08ec1e824b73db044236_USER_{}.root'
    number = 500
    tree_path = 'tagAndProbeDumper/trees/DYJetsToLL_amcatnloFXFX_13TeV_All'
    output_file = 'tnp_mc.root'
    var_binning = {
            'probePhoIso03': (100, 0, 10),
            'probeChIso03worst': (100, 0, 10),
            'probeChIso03worst_uncorr': (100, 0, 10),
            'probeChIso03': (100, 0, 10),
            'probeChIso03_uncorr': (100, 0, 10),
            'probePhoIdMVA': (200, -1, 1),
            'probePhoIdMVA_uncorr': (200, -1, 1),
            'probeFull5x5_r9': (100, 0, 1),
            'probeSigmaIeIe': (400, 0, 0.04),
            'probeSigmaIeIe_uncorr': (400, 0, 0.04),
            'probeCovarianceIeIp': (100, -0.0005, 0.0005),
            'probeCovarianceIeIp_uncorr': (100, -0.0005, 0.0005),
            'probeEtaWidth_Sc': (100, 0, 0.05),
            'probePhiWidth_Sc': (150, 0, 0.15),
            'probeS4': (100, 0, 1),
            'probeS4_uncorr': (100, 0, 1)
            }

    # Create and fill TChain
    chain = fill_tchain(base_dir, file_name, number, tree_path)

    # Create RDataFrame and write histos
    rdf = write_histos(chain, output_file, var_binning)

if __name__ == "__main__":
    main()
