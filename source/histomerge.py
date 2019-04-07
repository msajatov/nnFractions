import utils.Plotting as pl
from Tools.VarObject.VarObject import Var
import root_numpy as rn
import ROOT as R
import root_pandas as rp
from FileManager import FileManager
from Settings import Settings
from ConfigParser import ConfigParser
from pandas import DataFrame, concat
import copy


def main():
    bin_var = "m_vis"
    channel = "tt"
    era = "2017"
    config = "conf/frac_config_{0}_{1}.json".format(channel, era)

    file_manager = FileManager("/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output")

    prediction_dir = "predictions_newcode_complete_" + era
    file_manager.set_prediction_dirname(prediction_dir)

    file_manager.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))

    plot_dir = "/test_fracplots/" + channel
    file_manager.set_plot_dirname(plot_dir)

    settings = Settings("keras", channel, era)
    parser = ConfigParser(channel, era, config)
    plot_creator = PlotCreator(settings, file_manager, parser)

    sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]

    outdirpath = file_manager.get_plot_dirpath()

    plot_creator.make_fraction_plots(sample_sets, bin_var, "histo_concat", outdirpath)
    plot_creator.make_val_plots(sample_sets, bin_var, "histo_concat", outdirpath)
    #plot_creator.plot_frac_histo_for_inclusive_samples(sample_sets, bin_var, "sample_concat", outdirpath)
    #plot_creator.plot_val_histo_for_inclusive_samples(sample_sets, bin_var, "sample_concat", outdirpath)


    # sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
    #
    # print "Filtered sample sets for prediction frac plots: \n"
    #
    # for ss in sample_sets:
    #     print ss
    #
    # outdirpath = file_manager.get_plot_dirpath()
    # plot_creator.make_fraction_plots(sample_sets, bin_var, "full", outdirpath)

    # ---------------------------------------------------------------------------------

    # sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
    #
    # print "Filtered sample sets for prediction val plots: \n"
    #
    # for ss in sample_sets:
    #     print ss
    #
    # outdirpath = file_manager.get_plot_dirpath()
    # plot_creator.make_val_plots(sample_sets, bin_var, "full", outdirpath)

    # ---------------------------------------------------------------------------------


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
        val_histo_summary = []

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            val_histo = self.get_histo_for_val(sample_set, branches, var)
            val_histo_summary.append(val_histo)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87"}
            outfilepath = "{0}/{1}_val_{2}_{3}.png".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(val_histo, descriptions, outfilepath)

        outfilepath = "{0}/{1}_val_{2}_{3}.png".format(outdirpath, prefix, "inclusive", bin_var)
        outfileprefix = "{0}/{1}_val_{2}_{3}".format(outdirpath, prefix, "inclusive", bin_var)
        keys = ["val"]
        self.create_inclusive_plot(var, keys, val_histo_summary, descriptions, outfileprefix)
        pass

    # for each sample individually (TTJ, VVT etc.) and inclusive (all together)
    # legend: the 4 fractions, tt_jet, w_jet, qcd_jet, other
    def make_fraction_plots(self, sample_sets, bin_var, prefix, outdirpath):
        fraction_histo_summary = []

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos_for_fractions(sample_set, branches, var)
            fraction_histo_summary.append(frac_histos)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87"}
            outfilepath = "{0}/{1}_frac_{2}_{3}.png".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(frac_histos, descriptions, outfilepath)

        outfilepath = "{0}/{1}_frac_{2}_{3}.png".format(outdirpath, prefix, "inclusive", bin_var)
        outfileprefix = "{0}/{1}_frac_{2}_{3}".format(outdirpath, prefix, "inclusive", bin_var)
        keys = ["predicted_prob_0", "predicted_prob_1", "predicted_prob_2", "predicted_prob_3"]
        self.create_inclusive_plot(var, keys, fraction_histo_summary, descriptions, outfileprefix)
        pass

    def get_histos_for_fractions(self, sample_set, branches, var):
        histograms = {}
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)

        for i in range(0, 4):
            # events = rp.read_root(paths=sample_path, where=select,
            #                       columns=branches)
            template = "test"
            hist = self.fillHisto(events, template, "predicted_prob_{0}".format(i), var)
            histograms["predicted_prob_{0}".format(i)] = hist

        return histograms

    def get_histo_for_val(self, sample_set, branches, var):
        histograms = {}
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
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

    def plot_val_histo_for_inclusive_samples(self, sample_sets, bin_var, prefix, outdirpath):
        event_collection = DataFrame()

        branches = [bin_var]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            events = self.get_events_for_sample_set(sample_set, branches)
            event_collection = concat([event_collection, events], axis=0)

        hist = self.fillHisto(event_collection, "", "1.0", var)
        histograms = {}
        histograms["val"] = hist

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87"}
        outfilepath = "{0}/{1}_val_{2}_{3}.png".format(outdirpath, prefix, "inclusive", bin_var)
        self.create_plot(histograms, descriptions, outfilepath)

    def plot_frac_histo_for_inclusive_samples(self, sample_sets, bin_var, prefix, outdirpath):
        print "Entering plot frac inclusive"

        event_collection = DataFrame()

        branches = [bin_var,
                    "predicted_prob_0",
                    "predicted_prob_1",
                    "predicted_prob_2",
                    "predicted_prob_3"]

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            events = self.get_events_for_sample_set(sample_set, branches)
            event_collection = concat([event_collection, events], axis=0)

        histograms = {}

        for i in range(0, 4):
            template = ""
            hist = self.fillHisto(event_collection, template, "predicted_prob_{0}".format(i), var)
            histograms["predicted_prob_{0}".format(i)] = hist

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87"}
        outfilepath = "{0}/{1}_frac_{2}_{3}.png".format(outdirpath, prefix, "inclusive", bin_var)
        self.create_plot(histograms, descriptions, outfilepath)

    def get_events_for_sample_set(self, sample_set, branches):
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

    def create_plot(self, histograms, descriptions, outfile):
        pl.plot(histograms, canvas="linear", signal=[],
                descriptions=descriptions, outfile=outfile)

    def create_normalized_plot(self, histos, descriptions, outfile):

        bin_total_dict = {}
        histograms = copy.deepcopy(histos)

        # iterate over fractions
        for key in histograms:
            frac_histo = histograms[key]
            bin_total_dict[key] = []
            #iterate over bins
            nbinsx = frac_histo.GetXaxis().GetNbins()
            for i in range (0, nbinsx + 1):
                bin_content = frac_histo.GetBinContent(i)
                bin_total_dict[key].append(bin_content)

        # calculate total bin content for each bin
        bin_totals = []
        nbinsx = frac_histo.GetXaxis().GetNbins()
        for i in range(0, nbinsx + 1):
            bin_totals.append(0)
            # iterate over fractions
            for key in histograms:
                bin_totals[i] += bin_total_dict[key][i]

        # iterate over bins
        nbinsx = frac_histo.GetXaxis().GetNbins()
        for i in range(0, nbinsx + 1):
            for key in histograms:
                frac_histo = histograms[key]
                bin_content = frac_histo.GetBinContent(i)
                if bin_totals[i] != 0 and bin_content != 0:
                    normalized_content = bin_content / bin_totals[i]
                    frac_histo.SetBinContent(i, normalized_content)

        self.create_plot(histograms, descriptions, outfile)


    def create_inclusive_plot(self, var, keys, histograms, descriptions, outfile):

        if not histograms:
            print "Cannot create inslusive plots: List of histograms is empty!"#
            return

        fraction_histo_dict = {}
        for key in keys:
            fraction_histo_dict[key] = R.TH1F("", "", *(var.bins("def")))

        # iterate over source files
        for histos in histograms:
            # iterate over fractions
            for key in histos:
                frac_histo = histos[key]
                fraction_histo_dict[key].Add(frac_histo)

        self.create_normalized_plot(fraction_histo_dict, descriptions, "{0}_norm.png".format(outfile))

        pl.plot(fraction_histo_dict, canvas="linear", signal=[],
                descriptions=descriptions, outfile="{0}.png".format(outfile))

if __name__ == '__main__':
    main()