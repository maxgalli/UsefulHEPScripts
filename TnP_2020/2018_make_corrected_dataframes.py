from quantile_regression_chain import quantileRegression_chain as qRC
from quantile_regression_chain import quantileRegression_chain_disc as qRCd
import numpy as np
import yaml
from distributed import LocalCluster, Client
from dask_jobqueue import SLURMCluster
import argparse


import logging
logger = logging.getLogger("")


def parse_arguments():
    parser = argparse.ArgumentParser(
            description = '')

    parser.add_argument(
        "-cl",
        "--cluster_id",
        required=True,
        type=str,
        help="")

    return parser.parse_args()

def setup_logging(output_file, level=logging.DEBUG):
    logger.setLevel(level)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(output_file, "w")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

def main(args):
    cluster = args.cluster_id
    stream = open('config.yaml','r')
    inp=yaml.safe_load(stream)
    dataframes = inp['dataframes']

    ss = ['probeCovarianceIeIp','probeS4','probeR9','probePhiWidth','probeSigmaIeIe','probeEtaWidth']
    ch = ['probeChIso03','probeChIso03worst']
    ph = ['probePhoIso']
    year = '2018'
    n_evts = 4700000
    workDir = '/work/gallim/dataframes/2018'
    weightsDirs = '/work/gallim/weights/2018_mc_full_dask'

    cols = ["mass","probeScEnergy","probeScEta","probePhi","run","weight",
            "weight_clf","rho","probeR9","probeSigmaIeIe","probePhiWidth",
            "probeEtaWidth","probeCovarianceIeIp","probeCovarianceIpIp",
            "probeS4","probePhoIso","probeChIso03","probeChIso03worst",
            "probeSigmaRR","probePt","tagPt","probePassEleVeto","tagScEta"]

    client = Client(cluster)


    # ### Shower Shapes

    qrc_EB = qRC(year, 'EB', workDir, ss)
    qrc_EB.loadMCDF(dataframes['mc']['EB']['input'],0,n_evts,columns=cols)
    qrc_EB.loadDataDF(dataframes['data']['EB']['input'],0,n_evts,columns=cols)

    qrc_EE = qRC(year, 'EE', workDir, ss)
    qrc_EE.loadMCDF(dataframes['mc']['EE']['input'],0,n_evts,columns=cols)
    qrc_EE.loadDataDF(dataframes['data']['EE']['input'],0,n_evts,columns=cols)

    for qrc in [qrc_EB, qrc_EE]:
        for var in qrc.vars:
            qrc.loadClfs(var,weightsDir=weightsDirs)
            qrc.correctY(var, client)

    # ### Photon Iso

    qrc_ph_EB = qRCd(year, 'EB', workDir, ph)

    qrc_ph_EB.MC = qrc_EB.MC
    qrc_ph_EB.data = qrc_EB.data

    qrc_ph_EB.loadp0tclf('probePhoIso', weightsDir=weightsDirs)
    qrc_ph_EB.loadClfs('probePhoIso',weightsDir=weightsDirs)
    qrc_ph_EB.correctY('probePhoIso', client)

    qrc_ph_EE = qRCd(year, 'EE', workDir, ph)

    qrc_ph_EE.MC = qrc_EE.MC
    qrc_ph_EE.data = qrc_EE.data

    qrc_ph_EE.loadp0tclf('probePhoIso', weightsDir=weightsDirs)
    qrc_ph_EE.loadClfs('probePhoIso',weightsDir=weightsDirs)
    qrc_ph_EE.correctY('probePhoIso', client)

    # ### Charged Iso

    qrc_ch_EB = qRCd(year, 'EB', workDir, ch)

    qrc_ch_EB.MC = qrc_ph_EB.MC
    qrc_ch_EB.data = qrc_ph_EB.data

    qrc_ch_EB.load3Catclf(ch, weightsDir=weightsDirs)
    qrc_ch_EB.loadTailRegressors(ch,weightsDirs)
    for var in qrc_ch_EB.vars:
        qrc_ch_EB.loadClfs(var,weightsDirs)
        qrc_ch_EB.correctY(var, client)

    qrc_ch_EE = qRCd(year, 'EE', workDir, ch)

    qrc_ch_EE.MC = qrc_ph_EE.MC
    qrc_ch_EE.data = qrc_ph_EE.data

    qrc_ch_EE.load3Catclf(ch, weightsDir=weightsDirs)
    qrc_ch_EE.loadTailRegressors(ch,weightsDirs)
    for var in qrc_ch_EE.vars:
        qrc_ch_EE.loadClfs(var,weightsDirs)
        qrc_ch_EE.correctY(var, client)

    # Produce output files

    output_name_EB = 'final_output_EB'
    output_name_EE = 'final_output_EE'

    qrc_ch_EB.MC.to_hdf('{}/{}.h5'.format(workDir, output_name_EB),'df',mode='w',format='t')
    qrc_ch_EE.MC.to_hdf('{}/{}.h5'.format(workDir, output_name_EE),'df',mode='w',format='t')
    #qrc_ch_EB.MC.to_hdf('{}/{}.h5'.format(weightsDirs, output_name_EB),'df',mode='w',format='t')
    #qrc_ch_EE.MC.to_hdf('{}/{}.h5'.format(weightsDirs, output_name_EE),'df',mode='w',format='t')


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging('train_all_with_scheduler.log', logging.INFO)
    main(args)
