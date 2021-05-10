import argparse
from rich.logging import RichHandler

import logging
logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO):
    logger = logging.getLogger()

    logger.setLevel(level)
    formatter = logging.Formatter("%(message)s")

    stream_handler = RichHandler(show_time=False, rich_tracebacks=True)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger


def parse_arguments():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
            "--v0-input-dir",
            type=str,
            default="/work/gallim/root_files/vertex_investigation/VertexInvestigation_vtx0",
            help="Full path to input directory where ROOT files for vertex 0 are stored"
            )

    parser.add_argument(
            "--vcustom-input-dir",
            type=str,
            default="/work/gallim/root_files/vertex_investigation/VertexInvestigation",
            help="Full path to input directory where ROOT files for vertex custom are stored"
            )

    parser.add_argument(
            "--output-dir",
            required=True,
            type=str,
            help="Full path to output directory where to store plots"
            )

    parser.add_argument(
            "--channel",
            type=str
            )

    return parser.parse_args()


file_names_tmpl = {
        "ggH": "output_GluGluHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3f96409841a3cc85b911eb441562baae_USER_*.root",
        "vbf": "output_VBFHToGG_M125_TuneCP5_13TeV-amcatnlo-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2-cd53024353ab74068d5c62af34cd5d53_USER_*.root",
        "vh": "output_VHToGG_M125_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-4e4629d24fb44591ff8ab61ece79898c_USER_*.root",
        "tth": "output_ttHJetToGG_M125_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_storeWeights_alesauva-UL2018_0-10_6_4-v0-RunIISummer19UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1-3fde8d2608442ffb74ed8d18d363b700_USER_*.root"
        }


tree_name_tmpl = "diphotonDumper/trees/{}_125_13TeV_All_$SYST"
