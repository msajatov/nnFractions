import utils.Plotting as pl
from utils.VarObject import Var
import root_numpy as rn
import ROOT as R
from ROOT import TFile
import root_pandas as rp
from FileManager import FileManager
from Settings import Settings
from ConfigParser import ConfigParser
from TargetCategory import TargetCategory
from SampleSet import SampleSet
from pandas import DataFrame, concat
from PathObject import makeDir
import os
import copy


class FractionPlotter:

    def __init__(self, settings):
        self.settings = settings
        self.file_manager = settings.fraction_plot_file_manager
        self.config_parser = settings.config_parser
        self.target_names = self.config_parser.get_target_names()

    def set_target_names(self, target_names):
        self.target_names = target_names

    def get_branch_frac_dict(self):
        branch_frac_dict = {}
        for key in self.target_names:
            print key
            if key != -1:
                frac_name = self.target_names[key]
                branch_name = "predicted_frac_prob_{0}".format(key)
                branch_frac_dict[branch_name] = frac_name
        return branch_frac_dict

    def get_frac_branches(self):
        branches = list(self.get_branch_frac_dict().keys())
        return branches

    def make_val_plots(self, sample_sets, bin_var, prefix, outdirpath):
        val_histo_summary = []

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            val_histo = self.get_histo_for_val(sample_set, var)
            val_histo_summary.append(val_histo)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "41.5", "title": ""}
            outfilepath = "{0}/{1}_{2}_val_{3}_{4}.png".format(outdirpath, self.settings.channel, prefix, sample_set.name, bin_var)
            self.create_plot(val_histo, descriptions, outfilepath)

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "41.5", "title": ""}
        outfileprefix = "{0}/{1}_{2}_val_{3}_{4}".format(outdirpath, self.settings.channel, prefix, "inclusive", bin_var)

        # inclusive_histos = self.get_inclusive(var, val_histo_summary)
        # self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    # for each sample individually (TTJ, VVT etc.) and inclusive (all together)
    # legend: fractions, (tt_jet, w_jet, qcd_jet, other) or (tt, w, qcd)
    def make_fraction_plots(self, sample_sets, bin_var, prefix, outdirpath, inclusive=False):
        fraction_histo_summary = {}

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos_for_fractions(sample_set, var)
            fraction_histo_summary[sample_set.name] = frac_histos
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "41.5", "title": "", "yaxis": "Background Fractions"}
            outfile = "{0}/{1}_{2}_frac_{3}_{4}".format(outdirpath, self.settings.channel, prefix, sample_set.name, bin_var)
            self.create_plot(frac_histos, descriptions, "{0}.png".format(outfile))
            self.create_normalized_plot(frac_histos, descriptions, "{0}_norm.png".format(outfile))

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "41.5", "title": "", "yaxis": "Background Fractions"}
        outfileprefix = "{0}/{1}_{2}_frac_{3}_{4}".format(outdirpath, self.settings.channel, prefix, "inclusive", bin_var)

        if inclusive:
            inclusive_histos = self.get_inclusive(var, fraction_histo_summary)
            self.create_normalized_plot(inclusive_histos, descriptions, "{0}_norm.png".format(outfileprefix))
            self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    def make_classification_plots(self, sample_sets, bin_var, prefix, outdirpath, inclusive=False):
        fraction_histo_summary = {}

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            histos = self.get_histos_for_classification(sample_set, var)
            fraction_histo_summary[sample_set.name] = histos
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "41.5", "title": "", "yaxis": "Background Fractions (Classification)"}

            newoutpath = os.path.join(outdirpath, "classification")
            makeDir(newoutpath)

            outfile = "{0}/{1}_{2}_frac_{3}_{4}".format(newoutpath, self.settings.channel, prefix, sample_set.name, bin_var)
            self.create_plot(histos, descriptions, "{0}.png".format(outfile))
            self.create_normalized_plot(histos, descriptions, "{0}_norm.png".format(outfile))

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "41.5", "title": "", "yaxis": "Background Fractions (Classification)"}
        outfileprefix = "{0}/{1}_{2}_frac_{3}_{4}".format(newoutpath, self.settings.channel, prefix, "inclusive", bin_var)

        if inclusive:
            inclusive_histos = self.get_inclusive(var, fraction_histo_summary)
            self.create_normalized_plot(inclusive_histos, descriptions, "{0}_norm.png".format(outfileprefix))
            self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    def get_histos_for_fractions(self, sample_set, var):
        histograms = {}
        bin_var = var.name
        
        if "EMB" in sample_set.name:
            branches = [bin_var] + ["*weight*"] + ["*gen_match*"] + self.get_frac_branches()
        else:
            branches = [bin_var] + self.config_parser.weights + self.get_frac_branches()

        events = self.get_events_for_sample_set(sample_set, branches)

        dict = self.get_branch_frac_dict()

        for i in range(0, len(self.get_frac_branches())):
            print "index is:"
            print i
            hist = self.fill_histo(events, "", "predicted_frac_prob_{0}".format(i) + " * " + sample_set.weight, var)
            frac_name = dict["predicted_frac_prob_{0}".format(i)]
            histograms[frac_name] = hist

        # for i in xrange(len(self.get_frac_branches()) - 1, -1, -1):
        #     print "index is:"
        #     print i
        #     hist = self.fill_histo(events, "", "predicted_prob_{0}".format(i), var)
        #     histograms["predicted_prob_{0}".format(i)] = hist

        return histograms

    def get_histos_for_classification(self, sample_set, var):
        histograms = {}
        bin_var = var.name
        
        if "EMB" in sample_set.name:
            branches = [bin_var] + ["*weight*"] + ["*gen_match*"] + ["predicted_frac_class"]
        else:
            branches = [bin_var] + self.config_parser.weights + ["predicted_frac_class"]
        
        events = self.get_events_for_sample_set(sample_set, branches)

        dict = self.get_branch_frac_dict()

        for i in range(0, len(self.get_frac_branches())):
            print "index is:"
            print i

            filtered = events.query("predicted_frac_class == {0}".format(i))

            hist = self.fill_histo(filtered, "", sample_set.weight, var)
            frac_name = dict["predicted_frac_prob_{0}".format(i)]
            histograms[frac_name] = hist

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
        print "applying weight " + weight
        events.eval("event_weight=" + weight, inplace=True)

        fill_with = var.getBranches(jec_shift="")
        if not fill_with in events.columns.values.tolist():
            fill_with = var.getBranches(jec_shift="")

        rn.fill_hist(tmpHist, array=events[fill_with].values,
                     weights=events["event_weight"].values)

        return tmpHist

    def get_events_for_sample_set(self, sample_set, branches):
        root_path = self.file_manager.get_dir_path("prediction_input_dir")
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

    def get_event_count_for_sample_set(self, sample_set):
        root_path = self.file_manager.get_dir_path("prediction_input_dir")
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        file = TFile(sample_path)

        numEntries = file.TauCheck.GetEntries(select)
        return numEntries

    def create_plot(self, histograms, descriptions, outfile, optimizeTicks=True):
        sorted = self.sort_by_target_names(histograms)
        print sorted

        pl.simple_plot(sorted, canvas="linear", signal=[],
                       descriptions=descriptions, outfile=outfile, optimizeTicks=optimizeTicks)

    def create_normalized_plot(self, histos, descriptions, outfile):
        frac_histos = self.normalize(histos)
#         if descriptions.get("yaxis", ""):
#             descriptions["yaxis"] = "Normalized " + descriptions.get("yaxis", "")
        self.create_plot(frac_histos, descriptions, outfile, False)

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
        dummy_frac_histos = histograms.itervalues().next()
        keys = dummy_frac_histos.keys()

        fraction_histo_dict = {}
        for key in keys:
            fraction_histo_dict[key] = R.TH1F("", "", *(var.bins("def")))

        # iterate over source files
        for name, histos in histograms.items():
            print "looking at " + name
            if "QCD" in name:
                weight = 1
                #weight = 0.571225332448
            else:
                weight = 1
            print "using weight " + str(weight)
            # iterate over fractions
            integral_per_sample = 0
            
            for key in histos:
                frac_histo = histos[key]
                frac_histo.Scale(float(weight))
                
                integral = frac_histo.Integral()
                integral_per_sample += integral
                print "integral for {0}, {1}: ".format(name, key) + str(integral)
                fraction_histo_dict[key].Add(frac_histo)
                
            print "integral for {0}: ".format(name) + str(integral_per_sample)

        return fraction_histo_dict

    def get_target_name_list(self):
        return [kvp.value() for kvp in self.target_names]

    def sort_by_yields(self, histograms):

        print "histograms:"
        print histograms

        yields = [(h.Integral(), (name, h)) for name, h in histograms.items()]
        yields.sort()
        sorted = [copy.deepcopy(y[1]) for y in yields]

        return sorted

    def sort_by_target_names(self, histograms):

        print "histograms:"
        print histograms

        names = [(name, (name, h)) for name, h in histograms.items()]
        names.sort(key=get_index_for_fraction_name)
        sorted = [copy.deepcopy(n[1]) for n in names]

        return sorted

    def convert_to_list(self, histograms):
        list = [copy.deepcopy((k, v)) for k, v in histograms.items()]
        return list

def get_index_for_fraction_name(listitem):
    name = listitem[0]

    if name == "tt":
        print "name is tt"
        return 0
    elif name == "w":
        print "name is w"
        return 1
    elif name == "qcd":
        print "name is qcd"
        return 2
    elif name == "real":
        print "name is real"
        return 3
    else:
        print "name is something else:"
        print name
        return 4
