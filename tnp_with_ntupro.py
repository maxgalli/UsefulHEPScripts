import ntupro
from ntupro import Dataset, Histogram, Unit, UnitManager, GraphManager, RunManager


def main():

    # Data config
    data_base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_data_UL17/'
    data_base_file_name = 'output_SingleElectron_alesauva-UL2017-10_6_4-v0-Run2017{}-09Aug2019_UL2017{}_USER_{}.root'
    number = 500
    runs_id = [
            ('B', '-v1-8940b7b9416f1cbf6fbb86981f4883ea'), ('C', '-v1-c086301171e46d9c80ca640d553ab2cd'),
            ('D', '-v1-c086301171e46d9c80ca640d553ab2cd'), ('E', '-v1-c086301171e46d9c80ca640d553ab2cd'),
            ('F', '_rsb-v2-c086301171e46d9c80ca640d553ab2cd')
            ]
    data_file_names = []
    for ri in runs_id:
        for num in range(number):
            data_file_names.append(data_base_file_name.format(ri[0], ri[1], num))
    data_tree_path = 'tagAndProbeDumper/trees/Data_13TeV_All'
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

    # MC config
    mc_base_dir = '/eos/cms/store/group/phys_higgs/cmshgg/gallim/TnPProduction/_mc_UL17/'
    mc_base_file_name = 'output_DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_alesauva-UL2017-10_6_4-v2-RunIISummer19UL17MiniAOD-106X_mc2017_realistic_v6-v2-c148a697ba5b08ec1e824b73db044236_USER_{}.root'
    mc_file_names = [mc_base_file_name.format(num) for num in range(number)]
    mc_tree_path = 'tagAndProbeDumper/trees/DYJetsToLL_amcatnloFXFX_13TeV_All'
    var_binning_uncorr = {
            'probeChIso03worst_uncorr': (100, 0, 10),
            'probeChIso03_uncorr': (100, 0, 10),
            'probePhoIdMVA_uncorr': (200, -1, 1),
            'probeSigmaIeIe_uncorr': (400, 0, 0.04),
            'probeCovarianceIeIp_uncorr': (100, -0.0005, 0.0005),
            'probeS4_uncorr': (100, 0, 1)
            }

    tnp_data = ntupro.dataset_from_files('tnp_data', data_tree_path, [data_base_dir + file_name for file_name in data_file_names], be_picky = False)
    tnp_mc = ntupro.dataset_from_files('tnp_mc', mc_tree_path, [mc_base_dir + file_name for file_name in mc_file_names], be_picky = False)

    data_histos = [Histogram(var, var, binning) for var, binning in var_binning.items()]
    mc_histos = data_histos + [Histogram(var, var, binning) for var, binning in var_binning_uncorr.items()]

    data_unit = Unit(tnp_data, [], data_histos)
    mc_unit = Unit(tnp_mc, [], mc_histos)

    um = UnitManager()

    um.book([data_unit, mc_unit])

    gm = GraphManager(um.booked_units)

    rm = RunManager(gm.graphs)
    rm.run_locally('tnp_all.root')


if __name__ == "__main__":
    main()
