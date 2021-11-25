import ROOT

def ws_to_dict(ws):
    """
    Convert a workspace to a dictionary of objects.
    """
    ws_dict = {}

    # variables
    ws_dict['variables'] = []
    for var in ws.allVars():
        ws_dict['variables'].append({
            "name": var.GetName(),
            "value": var.getVal(),
            "error": var.getError(),
            "range": (var.getMin(), var.getMax()),
            }
        )

    # functions
    ws_dict['functions'] = []
    for func in ws.allFunctions():
        ws_dict['functions'].append({
            "name": func.GetName(),
            "object": func
            }
        )

    # pdfs
    ws_dict['pdfs'] = []
    for pdf in ws.allPdfs():
        ws_dict['pdfs'].append({
            "name": pdf.GetName(),
            "object": pdf
            }
        )

    # datasets
    ws_dict['datasets'] = []
    for data in ws.allData():
        ws_dict['datasets'].append({
            "name": data.GetName(),
            "object": data
            }
        )

    return ws_dict