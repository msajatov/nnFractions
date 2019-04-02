import ROOT as R
import root_pandas as rp
import root_numpy as rn
import utils.Plotting as pl
from Tools.VarObject.VarObject import Var
from Tools.Weights.Weights import Weight


def main():

    sourcefiles = ["TT", "VV", "DY", "W", "EMB", "Data"]
    channel = "et"

    for source in sourcefiles:
        sample_path = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/predictions_fracplot_oldcode_2017/{0}-NOMINAL_ntuple_{1}.root".format(channel, source)
        file = R.TFile(sample_path)

        outdir = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/plots/{0}".format(channel)

        select = "predicted_prob_0 < 2"

        bin_var = "m_vis"

        var = Var(bin_var, channel)

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        getHistosForFractions(sample_path, select, branches, var, bin_var, outdir, source, channel)
        getHistosForFullData(sample_path, select, branches, var, bin_var, outdir, source, channel)

def getHistosForFractions(sample_path, select, branches, var, bin_var, outdir, source, channel):
    histograms = {}
    for i in range(0, 4):
        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        template = "test"
        hist = fillHisto(events, template, "predicted_prob_{0}".format(i), var)
        histograms["predicted_prob_{0}".format(i)] = hist

    pl.plot(histograms, canvas="semi", signal=[],
            descriptions={"plottype": "ProjectWork", "xaxis": var.tex, "channel": channel, "CoM": "13",
                          "lumi": "35.87"},
            outfile=outdir + "/frac_" + source + "_" + bin_var + ".png")


def getHistosForFullData(sample_path, select, branches, var, bin_var, outdir, source, channel):
    histograms = {}
    events = rp.read_root(paths=sample_path, where=select,
                          columns=branches)
    template = "test"

    hist = fillHisto(events, template, "1.0", var)
    histograms["full"] = hist

    pl.plot(histograms, canvas="semi", signal=[],
            descriptions={"plottype": "ProjectWork", "xaxis": var.tex, "channel": channel, "CoM": "13", "lumi": "35.87"},
            outfile=outdir + "/full_" + source + "_" + bin_var + ".png")

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



#path = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/source/sandbox/htt_tt.inputs-sm-Run2017-ML.root"
#file = R.TFile(path)


#thing = copy.deepcopy(self.fillHisto(events=events,template=template_name, weight=weight, category=category,jec_shift=selection.jec_shift))


#sample_path = "/afs/hephy.at/data/higgs01/v10/mt-NOMINAL_ntuple_TT.root"



if __name__ == '__main__':
    main()


