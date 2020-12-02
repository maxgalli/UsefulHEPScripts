import pickle
import ROOT
import numpy as np
import pandas as pd

from prepare_data_with_sys import variables


def main():
    bdt = pickle.load(open('classifier.pkl', 'rb'))
    test_sig_dict = ROOT.RDataFrame("Events", 'test_sys_signal.root').AsNumpy()

    test = np.vstack([test_sig_dict[var] for var in variables]).T
    test_up = np.vstack([test_sig_dict[var_up] for var_up in ['{}_Up'.format(var) for var in variables]]).T
    test_down = np.vstack([test_sig_dict[var_down] for var_down in ['{}_Up'.format(var) for var in variables]]).T

    y_pred = bdt.predict(test)
    y_up_pred = bdt.predict(test_up)
    y_down_pred = bdt.predict(test_down)

    # Make df and print
    n_lines = 200
    test = test[:n_lines]
    y_pred = y_pred[:n_lines]
    y_up_pred = y_up_pred[:n_lines]
    y_down_pred = y_down_pred[:n_lines]

    df = pd.DataFrame(data=test, columns=variables)
    df['y'] = y_pred
    df['y_up'] = y_up_pred
    df['y_down'] = y_down_pred

    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


if __name__ == '__main__':
    main()
