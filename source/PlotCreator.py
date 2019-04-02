from DataReader import DataReader
import utils.Plotting as pl
from Tools.VarObject.VarObject import Var
import root_numpy as rn
import ROOT as R
import root_pandas as rp

class PlotCreator:

    def __init__(self, settings, file_manager, config_parser):
        self.settings = settings
        self.file_manager = file_manager
        self.config_parser = config_parser

    # for each target category: plot the NN output (predicted_prob_i for category i)
    # legend: samples
    def make_category_plots(self, sample_sets, target_categories):

        #plot
        pass

    def make_val_plots(self, sample_sets, bin_var, prefix, outdirpath):
        val_histo_summary = {}

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            val_histo = self.get_histo_for_val(sample_set, branches, var)
            val_histo_summary[sample_set.name] = val_histo
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87"}
            outfilepath = "{0}/{1}_val_{2}_{3}.png".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(val_histo, descriptions, outfilepath)

        pass

    # for each sample individually (TTJ, VVT etc.) and inclusive (all together)
    # legend: the 4 fractions, tt_jet, w_jet, qcd_jet, other
    def make_fraction_plots(self, sample_sets, bin_var, prefix, outdirpath):
        fraction_histo_summary = {}

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos_for_fractions(sample_set, branches, var)
            fraction_histo_summary[sample_set.name] = frac_histos
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87"}
            outfilepath = "{0}/{1}_frac_{2}_{3}.png".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(frac_histos, descriptions, outfilepath)

        pass

    def get_histos_for_fractions(self, sample_set, branches, var):
        histograms = {}
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        select = sample_set.cut

        for i in range(0, 4):
            events = rp.read_root(paths=sample_path, where=select,
                                  columns=branches)
            template = "test"
            hist = self.fillHisto(events, template, "predicted_prob_{0}".format(i), var)
            histograms["predicted_prob_{0}".format(i)] = hist

        return histograms

    def get_histo_for_val(self, sample_set, branches, var):
        histograms = {}
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        template = "test"

        hist = self.fillHisto(events, template, "1.0", var)
        histograms["val"] = hist

        return histograms

    def fillHisto(self, events, template, weight, var):
        tmpHist = R.TH1F(template, template, *(var.bins("def")))

        tmpHist.Sumw2(True)
        events.eval("event_weight=" + weight, inplace=True)

        fill_with = var.getBranches(jec_shift="")
        if not fill_with in events.columns.values.tolist():
            fill_with = var.getBranches(jec_shift="")

        rn.fill_hist(tmpHist, array=events[fill_with].values,
                     weights=events["event_weight"].values)

        return tmpHist

    def create_plot(self, histograms, descriptions, outfile):
        pl.plot(histograms, canvas="semi", signal=[],
                descriptions=descriptions, outfile=outfile)
