from ConfigParser import ConfigParser
from SampleSet import SampleSet
from Settings import Settings
from utils import Plotting as pl
import root_pandas as rp
from utils.VarObject import Var
from pandas import DataFrame, concat
import copy
import ROOT as R
from ROOT import TFile
import root_numpy as rn


def main():

    channel = "et"
    era = 2017
    use = "keras"
    config = "conf/frac_config_{0}_{1}.json".format(channel, era)
    settings = Settings(use, channel, era)
    parser = ConfigParser(channel, era, config)
    sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]

    sample_root_path = "/afs/hephy.at/data/higgs01/v10/"

    calculator = WeightCalculator(settings, parser, sample_root_path, sample_sets)
    #calculator.generate_control_plot(sample_sets, "m_vis", "", "debug")

    incl = calculator.generate_histos(sample_sets, "m_vis", "", "debug")
    w = calculator.calc_qcd_weight(incl)

    print "avg_weight: " + str(w)

    reweighted = calculator.reweight_qcd(incl, w)

    outdirpath = "debug"
    prefix = "reweighted_qcd"

    var = Var("m_vis", channel)
    descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": channel, "CoM": "13",
                    "lumi": "35.87", "title": "Fractions"}
    outfileprefix = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, channel, prefix, "inclusive", "m_vis")

    calculator.create_plot(reweighted, descriptions, "{0}.png".format(outfileprefix))

    pass


class WeightCalculator:

    def __init__(self, settings, parser, sample_root_path, sample_sets=0):
        self.settings = settings
        self.parser = parser
        self.sample_root_path = sample_root_path
        self.sample_sets = sample_sets
        pass

    def calc_qcd_weight(self, histos):
        bin_totals = []
        frac_histos = copy.deepcopy(histos)

        # get arbitrary entry from dict (number of bins must be the same for all histos)
        dummy_histo = frac_histos.itervalues().next()
        nbinsx = dummy_histo.GetXaxis().GetNbins()

        weight_sum = 0
        avg_weight = 0

        print "nbinsx: " + str(nbinsx)

        n_weights = 0

        # iterate over bins
        for i in range(0, nbinsx + 1):
            print "i: " + str(i)
            bin_totals.append(0)

            mc_sum = 0
            data = 0
            qcd = 0
            # iterate over fractions to sum up all contributions
            for key in frac_histos:
                #print key
                frac_histo = frac_histos[key]
                bin_content = frac_histo.GetBinContent(i)
                #print bin_content
                if "data" in key:
                    data = bin_content
                elif "QCD" in key:
                    qcd = bin_content
                else:
                    mc_sum += bin_content

            if qcd == 0:
                continue

            n_weights += 1
            diff = abs(data - mc_sum)
            weight = diff / qcd
            print "weight: " + str(weight)
            weight_sum += weight

        print "n_weights:" + str(n_weights)
        avg_weight = weight_sum / n_weights
        return avg_weight


    def reweight_qcd(self, histos, weight):
        histos = copy.deepcopy(histos)

        for key in histos:
            if "QCD" in key:
                qcd_histo = histos[key]
                qcd_histo.Scale(weight)

        return histos

    def calc_qcd_weight_for_single_bin(self):
        pass

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

    def generate_histos(self, sample_sets, bin_var, prefix, outdirpath):
        fraction_histo_summary = []

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos(sample_set, var)
            fraction_histo_summary.append(frac_histos)

        inclusive_histos = self.get_inclusive(var, fraction_histo_summary)
        return inclusive_histos

    def generate_control_plot(self, sample_sets, bin_var, prefix, outdirpath):
        fraction_histo_summary = []

        var = Var(bin_var, self.settings.channel)

        for sample_set in sample_sets:
            frac_histos = self.get_histos(sample_set, var)
            fraction_histo_summary.append(frac_histos)
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87", "title": "Fractions"}
            outfile = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, self.settings.channel, prefix, sample_set.name, bin_var)

            if "data" not in sample_set.name:
                self.create_plot(frac_histos, descriptions, "{0}.png".format(outfile))

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87", "title": "Fractions"}
        outfileprefix = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, self.settings.channel, prefix, "inclusive", bin_var)

        inclusive_histos = self.get_inclusive(var, fraction_histo_summary)
        self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    def get_histos(self, sample_set, var):
        histograms = {}
        bin_var = var.name
        branches = [bin_var] + self.parser.weights

        events = self.get_events_for_sample_set(sample_set, branches)

        hist = self.fill_histo(events, "", sample_set, var)
        name = sample_set.name
        if name == "data_AR":
            name = "data"
        histograms[name] = hist

        return histograms

    def fill_histo(self, events, template, sample_set, var):
        tmpHist = R.TH1F(template, template, *(var.bins("def")))

        tmpHist.Sumw2(True)
        events.eval("event_weight=" + sample_set.weight, inplace=True)

        fill_with = var.getBranches(jec_shift="")
        if not fill_with in events.columns.values.tolist():
            fill_with = var.getBranches(jec_shift="")

        rn.fill_hist(tmpHist, array=events[fill_with].values,
                     weights=events["event_weight"].values)

        return tmpHist

    def get_events_for_sample_set(self, sample_set, branches):
        root_path = self.sample_root_path
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        #sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

    def get_inclusive(self, var, input_histos):
        if not input_histos:
            print "Cannot create inclusive histograms: List of histograms is empty!"
            return

        histograms = copy.deepcopy(input_histos)

        print "in get_inclusive"

        fraction_histo_dict = {}

        # iterate over source files
        for histos in histograms:
            # iterate over fractions
            for key in histos:
                frac_histo = histos[key]
                fraction_histo_dict[key] = frac_histo

        return fraction_histo_dict

    def create_plot(self, histograms, descriptions, outfile):

        pl.plot(histograms, canvas="linear", signal=[],
                       descriptions=descriptions, outfile=outfile)


if __name__ == '__main__':
    main()