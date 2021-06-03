"""
Produce <n-files> ROOT files containing a dummy TTree with <n-branches> branches containing
<n-evs> randomly generated events.
The files are saved with the names "file*.root" at the path specified by <base-dir>.
"""

import argparse
import ROOT
from ROOT import TFile, TTree
from array import array


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-branches", type=int, required=True)
    parser.add_argument("--n-evs", type=int, required=True)
    parser.add_argument("--n-files", type=int, required=True)
    parser.add_argument("--base-dir", type=str, required=True)

    return parser.parse_args()


def main(args):
    n_branches = args.n_branches
    n_evs = args.n_evs
    n_files = args.n_files
    base_dir = args.base_dir

    file_name_tmpl = "file{}_{}branches_{}evs.root"
    tree_name = "DummyTree"

    print("Produce {} TTrees with {} branches, {} events each".format(n_files, n_branches, n_evs))

    for i in range(n_files):
        f = TFile(base_dir + "/" + file_name_tmpl.format(i, n_branches, n_evs), 'recreate')
        t = TTree(tree_name, tree_name)

        arrays = []
        for n in range(n_branches):
            branch_name = "branch_{}".format(n)
            br = array('d', [ 0. ])
            arrays.append(br)
            t.Branch(branch_name, br, '{}/D'.format(branch_name))

        for k in range(n_evs):
            for br in arrays:     
                br[0] = ROOT.gRandom.Gaus(5,2)
            t.Fill()

        f.Write()
        f.Close()


if __name__ == "__main__":
    args = parse_arguments()
    main(args)
