import ROOT
import re
from workspaces import ws_to_dict


def main():
    years = ['16', '17', '18']
    cats = ['cat0', 'cat1', 'cat2']
    edges = [
            '0p0_5p0',
            '5p0_10p0',
            '10p0_15p0',
            '15p0_20p0',
            '20p0_25p0',
            '25p0_30p0',
            '30p0_35p0',
            '35p0_45p0',
            '45p0_60p0',
            '60p0_80p0',
            '80p0_100p0',
            '100p0_120p0',
            '120p0_140p0',
            '140p0_170p0',
            '170p0_200p0',
            '200p0_250p0',
            '250p0_350p0',
            '350p0_450p0',
            '450p0_10000p0',
            ]
    sig_fl_tmpl = 'CMS-HGG_sigfit_smH_PTH_{}_{}.root' # edges, year
    data_bkg_fl_tmpl = 'CMS-HGG_multipdf_differential_Pt_{}.root' # year
    sig_pdf_tmpl = 'sigpdfrelhgg_PTH_{}_{}_{}_allProcs' # edges, cat, year
    bkg_pdf_tmpl = 'CMS_hgg_hgg_PTH_{}_{}_{}_{}_13TeV_bkgshape' # edges, cat, year, year
    data_shape_tmpl = 'roohist_data_mass_hgg_PTH_{}_{}_{}' # edges, cat, year
    title_tmpl = '{}-{}-{}' # year, edges, cat

    base_dir = '/work/gallim/DifferentialCombination_home/try_single_analyses/hig-19-016/outdir_differential_Pt/'
    out_dir = '/eos/home-g/gallim/www/plots/DifferentialCombination/WorkspacesStudies/'

    for year in years:
        data_bkg_fl = ROOT.TFile(base_dir + data_bkg_fl_tmpl.format(year))
        data_bkg_objects = ws_to_dict(data_bkg_fl.multipdf)
        for eds in edges:
            sig_fl = ROOT.TFile(base_dir + sig_fl_tmpl.format(eds, year))
            sig_objects = ws_to_dict(sig_fl.wsig_13TeV)
            for cat in cats:
                title = title_tmpl.format(year, eds, cat)
                mass = [dic['instance'] for dic in sig_objects['variables'] if dic['name'] == 'CMS_hgg_mass'][0]
                sig_pdf = [dic['instance'] for dic in sig_objects['pdfs'] if dic['name'] == sig_pdf_tmpl.format(eds, cat, year)][0]
                bkg_pdf = [dic['instance'] for dic in data_bkg_objects['pdfs'] if dic['name'] == bkg_pdf_tmpl.format(eds, cat, year, year)][0]
                data_shape = [dic['instance'] for dic in data_bkg_objects['binned_data'] if dic['name'] == data_shape_tmpl.format(eds, cat, year)][0]
                # Whole plotting business
                frame = mass.frame(ROOT.RooFit.Title(title))
                for s in [data_shape, bkg_pdf, sig_pdf]:
                    s.plotOn(frame)
                
                c = ROOT.TCanvas('', '')
                frame.Draw()
                for ext in ['png', 'pdf']:
                    c.SaveAs('{}{}.{}'.format(out_dir, title, ext))


if __name__ == "__main__":
    main()
