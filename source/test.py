import ROOT as R
import root_pandas as rp
import root_numpy as rn
import utils.Plotting as pl
from Tools.VarObject.VarObject import Var


def fillHisto(events, template, weight, var):
    tmpHist = R.TH1F(template, template, *(var.bins("def")))

    tmpHist.Sumw2(True)
    events.eval("event_weight=" + weight, inplace=True)

    fill_with = var.getBranches(jec_shift="")
    if not fill_with in events.columns.values.tolist():
        fill_with = var.getBranches(jec_shift="")

    rn.fill_hist(tmpHist, array=events[fill_with].values,
                 weights=events["event_weight"].values)

    return tmpHist

source = "TT"

sample_path = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/pred_refactor_2017/mt-NOMINAL_ntuple_{0}.root".format(source)
file = R.TFile(sample_path)

outdir = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/plots"

select = "predicted_prob_0 < 2"

bin_var = "pt_2"

branches = [bin_var,
            "predicted_prob_0",
            "predicted_prob_1",
            "predicted_prob_2",
            "predicted_prob_3"]

histograms = {}

events = rp.read_root(paths=sample_path, where=select,
                          columns=branches)

template = "test"

var = Var(bin_var, "mt")

hist = fillHisto(events, template, "1.0", var)
histograms["inclusive"] = hist

pl.plot(histograms, canvas="semi", signal=[],
        descriptions={"plottype": "ProjectWork", "xaxis": var.tex, "channel": "mt", "CoM": "13", "lumi": "35.87"},
        outfile=outdir + "/" + source + "_" + bin_var + "inclusive.png")


