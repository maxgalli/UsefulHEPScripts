import argparse
import ROOT
import pandas


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Show ROOT file contents in a nice way")

    parser.add_argument(
        "--file_name",
        required=True,
        type=str,
        help="Full path to the ROOT file")

    return parser.parse_args()


def main(args):
    file_name = args.file_name

    # Open file
    f = ROOT.TFile.Open(file_name)

    # Create list of RDataFrames with all the TTrees contained in the TFile
    rdfs = [ROOT.RDataFrame(f.Get(key.GetName())) for key in f.GetListOfKeys() if 'GetLeaf' in dir(f.Get(key.GetName()))]
    tree_names = [key.GetName() for key in f.GetListOfKeys() if 'GetLeaf' in dir(f.Get(key.GetName()))]

    # Visualize all the RDataFrames with pandas
    for tree_name, rdf in zip(tree_names, rdfs):
        print('Tree Name: {}'.format(tree_name))
        p = pandas.DataFrame(list(rdf.GetColumnNames()))
        print(p)
        print('\n\n')


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
