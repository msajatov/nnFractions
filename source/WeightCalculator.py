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
import os, errno
import logging


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    era = 2016
    embedding = True
    channels = ["tt", "et", "mt"]

    bin_var = "m_vis"

    new_file = True

    for channel in channels:
        if embedding:
            emb_suffix = "_emb"
            config = "conf/emb_frac_config_{0}_{1}.json".format(channel, era)
        else:
            emb_suffix = ""
            config = "conf/frac_config_{0}_{1}.json".format(channel, era)
        settings = Settings(channel, era)
        parser = ConfigParser(channel, era, config)
        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]

        if era == 2017:
            sample_root_path = "/afs/hephy.at/data/higgs01/v10/"
        elif era == 2016:
            sample_root_path = "/afs/hephy.at/data/higgs01/data_2016/ntuples_v6/{0}/ntuples_SVFIT_merged/".format(channel)

        calculator = WeightCalculator(settings, parser, sample_root_path, sample_sets)

        outdirpath = "debug/qcd_rw/4cat{2}/{1}/{0}".format(era, bin_var, emb_suffix)
        try:
            if not os.path.exists(outdirpath):
                os.makedirs(outdirpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        calculator.generate_histos(sample_sets, bin_var)
        calculator.generate_control_plot(sample_sets, bin_var, "", outdirpath)

        incl = calculator.get_copied_histos()
        int_w = calculator.calc_qcd_weight_with_integrals(incl)

        logging.info("int weight: " + str(int_w))

        reweighted = calculator.reweight_qcd(incl, int_w)

        prefix = "reweighted_qcd"

        var = Var(bin_var, channel)
        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": channel, "CoM": "13",
                        "lumi": "35.87", "title": "Fractions"}
        outfileprefix = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, channel, prefix, "inclusive", bin_var)

        calculator.create_plot(reweighted, descriptions, "{0}.png".format(outfileprefix))

        outfilepath = os.path.join(outdirpath, "qcd_weight_log_{0}.txt".format(bin_var))
        if new_file:
            mode = "w"
        else:
            mode = "a"
        f = open(outfilepath, mode)
        f.write("Channel: {0}\nBin_var: {1}\nQCD weight = ".format(channel, bin_var) + str(int_w) + "\n")
        f.close()
        new_file = False


class WeightCalculator:

    def __init__(self, settings, parser, sample_root_path, sample_sets=0):
        self.settings = settings
        self.parser = parser
        self.sample_root_path = sample_root_path
        self.sample_sets = sample_sets
        self.histos = None
        pass

    def calc_qcd_weight_with_integrals(self, histograms):
        histos = copy.deepcopy(histograms)

        mc_sum = 0
        data = 0
        qcd = 0

        for key in histos:
            # print key
            histo = histos[key]
            content = histo.Integral()
            # print bin_content
            if "data" in key:
                data = content
            elif "QCD" in key:
                qcd = content
            else:
                mc_sum += content

        diff = abs(data - mc_sum)
        weight = diff / qcd

        return weight


    def reweight_qcd(self, histos, weight):
        histos = copy.deepcopy(histos)

        for key in histos:
            if "QCD" in key:
                qcd_histo = histos[key]
                qcd_histo.Scale(weight)

        return histos

    def generate_histos(self, sample_sets, bin_var):
        logging.debug("Generating histos...")
        var = Var(bin_var, self.settings.channel)
        self.histos = self.read_histo_dict(sample_sets, var)

    def get_copied_histos(self):
        return copy.deepcopy(self.histos)

    def generate_control_plot(self, sample_sets, bin_var, prefix, outdirpath):
        logging.debug("Generating inclusive control plot...")

        var = Var(bin_var, self.settings.channel)

        histo_dict = self.get_copied_histos()

        for key in histo_dict:
            descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                            "lumi": "35.87", "title": "Fractions"}
            outfile = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, self.settings.channel, prefix, key, bin_var)

            # if "data" not in sample_set.name:
                # self.create_plot(frac_histos, descriptions, "{0}.png".format(outfile))

        descriptions = {"plottype": "ProjectWork", "xaxis": var.tex, "channel": self.settings.channel, "CoM": "13",
                        "lumi": "35.87", "title": "Fractions"}
        outfileprefix = "{0}/{1}_{2}_test_{3}_{4}".format(outdirpath, self.settings.channel, prefix, "inclusive", bin_var)

        inclusive_histos = self.get_copied_histos()
        self.create_plot(inclusive_histos, descriptions, "{0}.png".format(outfileprefix))

    def read_histo_dict(self, sample_sets, var):
        histograms = {}
        bin_var = var.name
        for sample_set in sample_sets:

            if "EMB" in sample_set.name:
                branches = [bin_var] + ["*weight*"] + ["*gen_match*"]
            else:
                branches = [bin_var] + self.parser.weights

            logging.debug("weights:")
            logging.debug(self.parser.weights)

            logging.debug("branch")

            events = self.get_events_for_sample_set(sample_set, branches)

            hist = self.fill_histo(events, "", sample_set, var)
            name = sample_set.name
            if name == "data_AR":
                name = "data"
            histograms[name] = hist

        return histograms

    def fill_histo(self, events, template, sample_set, var):
        tmpHist = R.TH1F(template, template, *(var.bins("def")))

        if "QCD" in sample_set.name:
            weight = 1.0
        else:
            weight = sample_set.weight

        tmpHist.Sumw2(True)
        events.eval("event_weight=" + str(weight), inplace=True)

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

        logging.debug("sample_path: " + sample_path)

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

    def create_plot(self, histograms, descriptions, outfile):
        pl.plot(histograms, canvas="linear", signal=[],
                       descriptions=descriptions, outfile=outfile)


if __name__ == '__main__':
    main()
