import ROOT
import re
from workspaces import ws_to_dict


def main():
    base_dir = '/work/gallim/DifferentialCombination_home/try_single_analyses/hig-19-016/outdir_differential_Pt/'

    sig_fl_path = 'CMS-HGG_sigfit_smH_PTH_15p0_20p0_18.root'
    data_bkg_fl_path = 'CMS-HGG_multipdf_differential_Pt_18.root'

    sig_fl = ROOT.TFile(base_dir + sig_fl_path)
    data_bkg_fl = ROOT.TFile(base_dir + data_bkg_fl_path)

    sig_objects = ws_to_dict(sig_fl.wsig_13TeV)
    data_bkg_object = ws_to_dict(data_bkg_fl.multipdf)

    out_dir = '/eos/home-g/gallim/www/plots/DifferentialCombination/WorkspacesStudies/'
    
    # Get signal model pdfs for 15-20
    signal_tmpl = re.compile('hggpdfsmrel_13TeV_smH_PTH_15p0_20p0_hgg_PTH_.*_18$')
    signal_pdfs = []
    for dic in sig_objects['pdfs']:
        if signal_tmpl.match(dic['name']):
            signal_pdfs.append(dic)

    # Whole plotting business
    mass = [dic['instance'] for dic in sig_objects['variables'] if dic['name'] == 'CMS_hgg_mass'][0]
    frame = mass.frame(ROOT.RooFit.Title('Signal Model'))
    for sig_pdf in signal_pdfs:
        sig_pdf['instance'].plotOn(frame)

    c = ROOT.TCanvas('', '')
    frame.Draw()
    for ext in ['png', 'pdf']:
        c.SaveAs('{}signal_model.{}'.format(out_dir, ext))

    # Get bkg model pdfs for 15-20
    bkg_tmpl = re.compile('CMS_hgg_hgg_PTH_15p0_20p0_.*_18_18_13TeV_bkgshape$')
    bkg_pdfs = []
    for dic in data_bkg_object['pdfs']:
        if bkg_tmpl.match(dic['name']):
            bkg_pdfs.append(dic)

     # Whole plotting business
    mass = [dic['instance'] for dic in data_bkg_object['variables'] if dic['name'] == 'CMS_hgg_mass'][0]
    frame = mass.frame(ROOT.RooFit.Title('Bkg Model'))
    for bkg_pdf in bkg_pdfs:
        bkg_pdf['instance'].plotOn(frame)

    c = ROOT.TCanvas('', '')
    frame.Draw()
    for ext in ['png', 'pdf']:
        c.SaveAs('{}bkg_model.{}'.format(out_dir, ext))

    # Get data for 15-20
    data_tmpl = re.compile('roohist_data_mass_hgg_PTH_15p0_20p0_.*_18')
    data = []
    for dic in data_bkg_object['binned_data']:
        if data_tmpl.match(dic['name']):
            data.append(dic)
   
      # Whole plotting business
    mass = [dic['instance'] for dic in data_bkg_object['variables'] if dic['name'] == 'CMS_hgg_mass'][0]
    frame = mass.frame(ROOT.RooFit.Title('Data'))
    for d in data:
        d['instance'].plotOn(frame)

    c = ROOT.TCanvas('', '')
    frame.Draw()
    for ext in ['png', 'pdf']:
        c.SaveAs('{}data.{}'.format(out_dir, ext))
 

if __name__ == "__main__":
    main()
