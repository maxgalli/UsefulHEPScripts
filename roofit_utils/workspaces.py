import ROOT

from cppyy.gbl import RooRealVar, RooFormulaVar, RooAbsPdf, RooConstVar, RooDataSet, RooDataHist


def make_dict(obj):

    return {
        'name': obj.GetName(),
        'instance': obj,
        'type': obj.ClassName(),
    }


def ws_to_dict(ws):
    """
    Convert a workspace to a dictionary of objects.
    """
    ws_dict = {
        "variables": [],
        "functions": [],
        "pdfs": [],
        "constants": [],
        "categories": [],
        "other": [],
        "unbinned_data": [],
        "binned_data": []
    }

    objects = ws.components()
    data = ws.allData()

    for obj in objects:
        if obj.InheritsFrom('RooRealVar'):
            ws_dict['variables'].append(make_dict(obj))
        elif obj.InheritsFrom('RooFormulaVar') or obj.InheritsFrom('RooRecursiveFraction'):
            ws_dict['functions'].append(make_dict(obj))
        elif obj.InheritsFrom('RooAbsPdf'):
            ws_dict['pdfs'].append(make_dict(obj))
        elif obj.InheritsFrom('RooConstVar'):
            ws_dict['constants'].append(make_dict(obj))
        elif obj.InheritsFrom('RooCategory'):
            ws_dict['categories'].append(make_dict(obj))
        else:
            ws_dict['other'].append(make_dict(obj))

    for obj in data:
        if obj.InheritsFrom('RooDataSet'):
            ws_dict['unbinned_data'].append(make_dict(obj))
        elif obj.InheritsFrom('RooDataHist'):
            ws_dict['binned_data'].append(make_dict(obj))
        else:
            ws_dict['other'].append(make_dict(obj))

    return ws_dict
