import utils.Plotting as pl
from utils.VarObject import Var
import root_numpy as rn
import ROOT as R
import root_pandas as rp
from FileManager import FileManager
from Settings import Settings
from ConfigParser import ConfigParser
from TargetCategory import TargetCategory
from SampleSet import SampleSet
from pandas import DataFrame, concat
import copy


class PlotCreator:

    def __init__(self, settings, file_manager, config_parser):
        self.settings = settings
        self.file_manager = file_manager
        self.config_parser = config_parser
        self.target_names = self.config_parser.get_target_names()
        self.branch_frac_dict = self.get_branch_frac_dict()

    def get_branch_frac_dict(self):
        branch_frac_dict = {}
        for key in self.target_names:
            print key
            if key != -1:
                frac_name = self.target_names[key]
                branch_name = "predicted_prob_{0}".format(key)
                branch_frac_dict[branch_name] = frac_name
        return branch_frac_dict

    def get_frac_branches(self):
        branches = list(self.branch_frac_dict.keys())
        return branches

    def make_val_plots(self, sample_sets, bin_var, prefix, outdirpath):
        val_histo_summary = []

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            val_histo = self.get_histo_for_val(sample_set, var)
            val_histo_summary.append(val_histo)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87", "title": "Fraction Validation"}
            outfilepath = "{0}/{1}_val_{2}_{3}.png".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(val_histo, descriptions, outfilepath)

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87", "title": "Fraction Validation"}
        outfileprefix = "{0}/{1}_val_{2}_{3}".format(outdirpath, prefix, "inclusive", bin_var)

        inclusive_histos = self.get_inclusive(var, val_histo_summary)
        self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    # for each sample individually (TTJ, VVT etc.) and inclusive (all together)
    # legend: fractions, (tt_jet, w_jet, qcd_jet, other) or (tt, w, qcd)
    def make_fraction_plots(self, sample_sets, bin_var, prefix, outdirpath):
        fraction_histo_summary = []

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos_for_fractions(sample_set, var)
            fraction_histo_summary.append(frac_histos)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87", "title": "Fractions"}
            outfile = "{0}/{1}_frac_{2}_{3}".format(outdirpath, prefix, sample_set.name, bin_var)
            self.create_plot(frac_histos, descriptions, "{0}.png".format(outfile))
            self.create_normalized_plot(frac_histos, descriptions, "{0}_norm.png".format(outfile))

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87", "title": "Fractions"}
        outfileprefix = "{0}/{1}_frac_{2}_{3}".format(outdirpath, prefix, "inclusive", bin_var)

        inclusive_histos = self.get_inclusive(var, fraction_histo_summary)
        self.create_normalized_plot(inclusive_histos, descriptions, "{0}_norm.png".format(outfileprefix))
        self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    def get_histos_for_fractions(self, sample_set, var):
        histograms = {}
        bin_var = var.name
        branches = [bin_var] + self.get_frac_branches()

        events = self.get_events_for_sample_set(sample_set, branches)

        for i in range(0, len(self.get_frac_branches())):
            hist = self.fill_histo(events, "", "predicted_prob_{0}".format(i), var)
            histograms["predicted_prob_{0}".format(i)] = hist

        return histograms

    def get_histo_for_val(self, sample_set, var):
        histograms = {}
        bin_var = var.name
        branches = [bin_var]

        events = self.get_events_for_sample_set(sample_set, branches)

        hist = self.fill_histo(events, "", "1.0", var)
        histograms["val"] = hist

        return histograms

    def fill_histo(self, events, template, weight, var):
        tmpHist = R.TH1F(template, template, *(var.bins("def")))

        tmpHist.Sumw2(True)
        events.eval("event_weight=" + weight, inplace=True)

        fill_with = var.getBranches(jec_shift="")
        if not fill_with in events.columns.values.tolist():
            fill_with = var.getBranches(jec_shift="")

        rn.fill_hist(tmpHist, array=events[fill_with].values,
                     weights=events["event_weight"].values)

        return tmpHist

    def get_events_for_sample_set(self, sample_set, branches):
        root_path = self.file_manager.get_prediction_dirpath()
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

    def create_plot(self, histograms, descriptions, outfile):
        pl.simple_plot(histograms, canvas="linear", signal=[],
                       descriptions=descriptions, outfile=outfile)

    def create_normalized_plot(self, histos, descriptions, outfile):
        frac_histos = self.normalize(histos)
        self.create_plot(frac_histos, descriptions, outfile)

    def normalize(self, histos):
        bin_totals = []
        frac_histos = copy.deepcopy(histos)

        # get arbitrary entry from dict (number of bins must be the same for all histos)
        dummy_histo = frac_histos.itervalues().next()
        nbinsx = dummy_histo.GetXaxis().GetNbins()

        # iterate over bins
        for i in range(0, nbinsx + 1):
            bin_totals.append(0)
            # iterate over fractions to sum up all contributions
            for key in frac_histos:
                frac_histo = frac_histos[key]
                bin_content = frac_histo.GetBinContent(i)
                bin_totals[i] += bin_content
            # iterate over fractions again and normalize
            for key in frac_histos:
                frac_histo = frac_histos[key]
                bin_content = frac_histo.GetBinContent(i)
                if bin_totals[i] != 0 and bin_content != 0:
                    normalized_content = bin_content / bin_totals[i]
                    frac_histo.SetBinContent(i, normalized_content)

        return frac_histos

    def get_inclusive(self, var, input_histos):
        if not input_histos:
            print "Cannot create inclusive histograms: List of histograms is empty!"
            return

        histograms = copy.deepcopy(input_histos)

        # get first list entry (arbitrary, number of histos must be the same for all entries)
        dummy_frac_histos = histograms[0]
        keys = dummy_frac_histos.keys()

        fraction_histo_dict = {}
        for key in keys:
            fraction_histo_dict[key] = R.TH1F("", "", *(var.bins("def")))

        # iterate over source files
        for histos in histograms:
            # iterate over fractions
            for key in histos:
                frac_histo = histos[key]
                fraction_histo_dict[key].Add(frac_histo)

        return fraction_histo_dict

