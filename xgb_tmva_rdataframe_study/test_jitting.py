import ROOT

inject_bdt = """
            using namespace TMVA::Experimental;
            RBDT<> bdt("myBDT", "classifier.root");
            """

to_inject = """
            ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager, void> {function_name}(
            ROOT::RDataFrame &df) {{
                auto dfret = df.Define("{predict_column}", Compute<4, float>(bdt), {{"{v1}", "{v2}", "{v3}", "{v4}"}});
                return dfret;
            }}

            ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager, void> {function_name}(
            ROOT::RDF::RInterface<ROOT::Detail::RDF::RLoopManager, void> &df) {{
                auto dfret = df.Define("{predict_column}", Compute<4, float>(bdt), {{"{v1}", "{v2}", "{v3}", "{v4}"}});
                return dfret;
            }}

            """

def main():
    df_sig = ROOT.RDataFrame('Events', 'test_sys_signal.root')

    dic = {
            'function_name': 'Apply',
            'predict_column': 'y',
            'v1': 'Muon_pt_1',
            'v2': 'Muon_pt_2',
            'v3': 'Electron_pt_1',
            'v4': 'Electron_pt_2'
            }
    dic_up = {
            'function_name': 'ApplyUp',
            'predict_column': 'y_up',
            'v1': 'Muon_pt_1_Up',
            'v2': 'Muon_pt_2_Up',
            'v3': 'Electron_pt_1_Up',
            'v4': 'Electron_pt_2_Up'
            }

    dic_down = {
            'function_name': 'ApplyDown',
            'predict_column': 'y_down',
            'v1': 'Muon_pt_1_Down',
            'v2': 'Muon_pt_2_Down',
            'v3': 'Electron_pt_1_Down',
            'v4': 'Electron_pt_2_Down'
            }

    # Inject bdt
    ROOT.gInterpreter.Declare(inject_bdt)

    for d in [dic, dic_up, dic_down]:
        ROOT.gInterpreter.Declare(to_inject.format(**d))
        df_sig = getattr(ROOT, d['function_name'])(df_sig)

    display_sig = df_sig.Display("", 200)
    display_sig.Print()

if __name__ == '__main__':
    main()


