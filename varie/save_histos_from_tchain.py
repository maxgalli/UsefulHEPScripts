import argparse
import ROOT


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Save in output file all the histograms from a TTree split into multiple files (i.e. TChain)")

    parser.add_argument(
        "--directory",
        required=True,
        type=str,
        help="Directory where the ROOT files are stored")

    parser.add_argument(
        "--file_base_name",
        required=True,
        type=str,
        help="Part of the name shared by all the ROOT files, with {} put for the parts that change (e.g. runs and number)")

    parser.add_argument(
        "--number",
        required=True,
        type=str,
        help="Number of ROOT files in the chain, (i.e. if 500, we have rfile1.root to rfile500.root)")

    parser.add_argument(
        "--tree_path",
        required=True,
        type=str,
        help="Full path to the tree (including sub-TDirectoryFiles)")

    parser.add_argument(
        "--output",
        required=True,
        type=str,
        help="Output file (without .root at the end)")

    parser.add_argument(
        "--runs",
        default=[],
        type=lambda runs: [run for run in runs.split(',')],
        help="Runs in the common file base name (e.g. B,C,D,E,F), seperated by a comma without space")

    return parser.parse_args()


def main(args):
    base_dir = args.directory
    file_name = args.file_base_name
    number = int(args.number)
    tree_path = args.tree_path
    output_file = args.output + '.root'
    runs = args.runs

    # Create and fill TChain
    chain = ROOT.TChain()
    if runs:
        for run in runs:
            for num in range(number):
                chain.Add(base_dir + '/' + file_name.format(run, num) + '/' + tree_path)
    else:
        for num in range(number):
            chain.Add(base_dir + '/' + file_name.format(num) + '/' + tree_path])

    # Create RDataFrame and write histos
    ROOT.EnableImplicitMT()
    rdf = ROOT.RDataFrame(chain)
    r_rst_ptrs = [rdf.Histo1D(column) for column in rdf.GetColumnNames()]
    f = ROOT.TFile(output_file, 'NEW')
    for ptr in r_rst_ptrs:
        histo = ptr.GetValue()
        histo.Write()
    f.Close()

if __name__ == "__main__":
    args = parse_arguments()
    main(args)
