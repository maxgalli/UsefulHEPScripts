"""
Produce <n-files> ROOT files containing a dummy TTree with two branches (x and y) containing
<n-evs> randomly generated events.
The files are saved with the names "file*.root" at the path specified by <base-dir>.
"""

import argparse
import ROOT
from ROOT import TFile, TTree
from array import array


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-evs", type=int, required=True)
    parser.add_argument("--n-files", type=int, required=True)
    parser.add_argument("--base-dir", type=str, required=True)

    return parser.parse_args()


def main(args):
    n_evs = args.n_evs
    n_files = args.n_files
    base_dir = args.base_dir

    file_name_tmpl = "file{}.root"
    tree_name = "DummyTree"

    print("Produce {} TTrees with {} events each".format(n_files, n_evs))

    for i in range(n_files):
        f = TFile(base_dir + "/" + file_name_tmpl.format(i), 'recreate')
        t = TTree(tree_name, tree_name)

        x = array('d', [ 0. ])
        y = array('d', [ 0. ])
        t.Branch('x', x, 'x/D')
        t.Branch('y', y, 'y/D')

        for k in range(n_evs):
           x[0] = ROOT.gRandom.Gaus(5,2)
           # uniform [0,10]
           y[0] = ROOT.gRandom.Rndm()*10
           t.Fill()

        f.Write()
        f.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
