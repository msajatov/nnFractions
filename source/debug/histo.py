#import ROOT as R
import root_pandas as rp
import root_numpy as rn
import utils.Plotting as pl
from Tools.VarObject.VarObject import Var
from Tools.Weights.Weights import Weight
from pandas import DataFrame


def main():

    #sourcefiles = ["TT", "VV", "DY", "WJets", "EMB", "Data"]
    sourcefiles = ["EMB"]
    channel = "mt"

    for source in sourcefiles:
        sample_path = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/pred_refactor_2017/{0}-NOMINAL_ntuple_{1}.root".format(channel, source)
        #file = R.TFile(sample_path)

        outdir = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/plots/{0}".format(channel)

        select = "mt_1 < 5000"

        bin_var = "m_vis"

        var = Var(bin_var, channel)

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        debugDataFrame(sample_path, select)

        # sample_outpath = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/predictions_oldcode_class_prob_2017/{0}-NOMINAL_ntuple_{1}.root".format(channel, source)
        #
        # events = addColumnToDataFrame(sample_path, select, branches, var, bin_var, outdir, source, channel)
        #
        # events.to_root(sample_outpath, key="TauCheck", mode="w")

        # for i in xrange(len(df)):
        #     for c in prediction[i].columns.values.tolist():
        #         df[i][c] = prediction[i][c]
        #
        #     mode = "w"
        #     df[i].to_root("{0}/{1}-{2}.root".format(outpath, channel, sample), key="TauCheck", mode=mode)

        #getHistosForFractions(sample_path, select, branches, var, bin_var, outdir, source, channel)
        #getHistosForFullData(sample_path, select, branches, var, bin_var, outdir, source, channel)

def addColumnToDataFrame(sample_path, select, branches, var, bin_var, outdir, source, channel):
    events = rp.read_root(paths=sample_path, where=select,
                          columns="")

    lst = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3"]
    prob_df = events[events.columns.intersection(lst)]

    #print "Prob df:"
    #print prob_df

    predicted_class_df = DataFrame(dtype=float, data={"predicted_class": prob_df.idxmax(axis=1).values})
    predicted_class_df = predicted_class_df.replace("predicted_prob_", "", regex=True)
    predicted_class_df = predicted_class_df.astype(float)

    predicted_prob_df = DataFrame(dtype=float, data={"predicted_prob": prob_df.max(axis=1).values})


    events['predicted_class'] = predicted_class_df["predicted_class"].values
    events['predicted_prob'] = predicted_prob_df["predicted_prob"].values

    full_list = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3", "predicted_class", "predicted_prob"]

    filtered_events_df = events[events.columns.intersection(full_list)]

    print events

    return events

    # df = DataFrame(dtype=float, data={"predicted_class": prediction.idxmax(axis=1).values,
    #                          "predicted_prob": prediction.max(axis=1).values } )

def debugDataFrame(sample_path, select):


    gen = rp.read_root(paths=sample_path, where=select,
                          columns="", chunksize=100)

    events = gen.next()

    cols = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3"]
    cols = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3", "predicted_class",
                 "predicted_prob"]

    print "DF Columns:"
    print events.columns

    lst = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3"]
    prob_df = events[events.columns.intersection(lst)]

    # print "Prob df:"
    # print prob_df

    predicted_class_df = DataFrame(dtype=float, data={"predicted_class": prob_df.idxmax(axis=1).values})
    predicted_class_df = predicted_class_df.replace("predicted_prob_", "", regex=True)
    predicted_class_df = predicted_class_df.astype(float)

    predicted_prob_df = DataFrame(dtype=float, data={"predicted_prob": prob_df.max(axis=1).values})

    events['predicted_class'] = predicted_class_df["predicted_class"].values
    events['predicted_prob'] = predicted_prob_df["predicted_prob"].values

    full_list = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3", "predicted_class",
                 "predicted_prob"]

    filtered_events_df = events[events.columns.intersection(full_list)]

    #print events

    return events

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


