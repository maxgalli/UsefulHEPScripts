import ROOT

def extract_all_histos_efficiently(tree, output_file):
        """
        Extract all histograms from a tree and save them in a file
        """
    rdf = ROOT.RDataFrame(tree)
    r_rst_ptrs = [rdf.Histo1D(column) for column in rdf.GetColumnNames()]
    f = ROOT.TFile(output_file, 'NEW')
    for ptr in r_rst_ptrs:
        histo = ptr.GetValue()
        histo.Write()
    f.Close()
