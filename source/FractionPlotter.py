from ROOT import *
import json
import FileManager
import os

def main():

    channel = "tt"

    with open("conf/cuts_2017.json", "r") as FSO:
        cuts = json.load(FSO)
        for c in cuts:
            cuts[c] = _assertChannel(cuts[c], channel)
        cut_dict = cuts

    basepath = "/afs/hephy.at/data/higgs01/v10/"

    path = "conf/frac_config_{0}_2017.json".format(channel)
    config = _flattenConfig(path)

    filteredsamples = {}

    cut_strings = []
    for sample in config["samples"]:
        print sample
        snap = config["samples"][sample]
        samplename = sample
        cut_strings.append(snap["select"])
        if "_full" in samplename:
            filteredsamples[samplename] = snap


    plotter = FractionPlotter(channel, filteredsamples, cut_dict)
    plotter.plot_probabilities()

    # lines = []
    # for key in filteredsamples:
    #
    #     value = filteredsamples[key]
    #     cut_alias = value["select"]
    #     cut = _parseCut(cut_alias, cut_dict, channel)
    #     full_file_path = basepath + channel + "-" + value["name"] + ".root"
    #     file = TFile(full_file_path)
    #
    #     print(key)
    #     #print(full_file_path)
    #     #print(cut_alias)
    #     #print(cut)
    #     numEntries = file.TauCheck.GetEntries(cut)
    #
    #     #print str(numEntries)
    #
    #     lines.append(key + ";" + str(numEntries) + "\n")
    #
    # file = open("{0}-2017-nums.csv".format(channel), "w")
    #
    # file.writelines(lines)

    # for key in filteredsamples:
    #     print key
    #     print filteredsamples[key]["name"]
    #     print filteredsamples[key]["select"]



    # for value in filteredsamples.values():
    #     print value["name"]
    #     print value["select"]

    # for n in filenames:
    #     print "Filename: " + n
    #
    # for s in samplenames:
    #     print "Samplename: " + s
    #
    # for c in cut_strings:
    #     print "Cutstrings: " + c



    #gROOT.ProcessLine('TFile *my = new TFile("/afs/hephy.at/work/m/msajatovic/data/mlFramework/pred/predictions_2017/tt-NOMINAL_ntuple_TT.root")');
    #file = TFile("/afs/hephy.at/work/m/msajatovic/data/mlFramework/pred/predictions_2017/tt-NOMINAL_ntuple_TT.root")

    #file = TFile("/afs/hephy.at/data/higgs01/v10/mt-NOMINAL_ntuple_VV.root")

    #selection = "mt_1 < 50"
    #selected =

    #selection = "mt_1 < 50"

    #selection = ""
    #numEntries = file.TauCheck.GetEntries(selection)
    #print "Number of entries: " + str(numEntries)



class FractionPlotter:

    def __init__(self, channel, filteredSamples, cut_dictionary):

        self.channel = channel
        self.read_paths = []
        self.samples = filteredSamples
        self.cut_dict = cut_dictionary


        output_root_path = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/predictions_test_2017"
        #read_paths.append(output_root_path + "/{0}-NOMINAL_ntuple_TT.root".format(channel))
        #read_paths.append(output_root_path + "/{0}-NOMINAL_ntuple_W.root".format(channel))
        #read_paths.append(output_root_path + "/{0}-NOMINAL_ntuple_Data.root".format(channel))
        #read_paths.append(output_root_path + "/{0}-NOMINAL_ntuple_VV.root".format(channel))
        #read_paths.append(output_root_path + "/{0}-NOMINAL_ntuple_DY.root".format(channel))

        self.basepath = output_root_path

        self.plot_dirpath = output_root_path + "/probability_plots_tt_new"


        if not os.path.exists(self.plot_dirpath):
            os.makedirs(self.plot_dirpath)

        # if not self.loadFile():
        #     print self.filename, "not found!!"
        #     return None

        self.prob_index_dict = {}
        self.prob_index_dict["0"] = "tt_jet"
        self.prob_index_dict["1"] = "w_jet"
        self.prob_index_dict["2"] = "qcd_jet"
        self.prob_index_dict["3"] = "other"


    def plot_probabilities(self):
        lines = []
        for key in self.samples:
            value = self.samples[key]
            cut_alias = value["select"]
            cut = _parseCut(cut_alias, self.cut_dict, self.channel)
            full_file_path = self.basepath + self.channel + "-" + value["name"] + ".root"
            if "WJets" in full_file_path:
                full_file_path = full_file_path.replace("WJets", "W")
            file = TFile(full_file_path)

            print "Key: " + key
            print "Full file path: " + full_file_path
            print "Cut alias:" + cut_alias

            numEntries = file.TauCheck.GetEntries(cut)

            outdir = self.plot_dirpath

            canvas = TCanvas()

            for index in self.prob_index_dict:
                value = self.prob_index_dict[index]
                file.TauCheck.Draw("predicted_prob_{0}".format(index))

                title = "{0}-predicted_prob_{1}_{2}".format(self.channel, value, key)
                outname = "{0}-predicted_prob_{1}_{2}.png".format(self.channel, value, key)
                outpath = "{0}/{1}".format(outdir, outname)

                primitives = canvas.GetListOfPrimitives()
                hist = primitives[0]

                hist.SetTitle(title)

                print "saving to " + outpath
                canvas.SaveAs(outpath)









            # print str(numEntries)

            lines.append(key + ";" + str(numEntries) + "\n")

        # file = open("{0}-2017-nums.csv".format(channel), "w")
        #
        # file.writelines(lines)


def plot_probability(self, path):


        return



def _assertChannel(entry, channel):

    if type( entry ) is dict:
        return entry[ channel ]
    else:
        return entry

def _parseCut(cutstring, cut_dict, channel):
    #cutstring = self._assertChannel( cutstring )
    for alias,cut in cut_dict.items():
        cutstring = _flattenCut(cutstring, channel)
        cutstring = cutstring.replace( alias, cut )
    return cutstring


def _flattenCut(cutentry, channel):
    if type( cutentry ) is dict:
        return cutentry[ channel ]
    else:
        return cutentry

def _flattenConfig(path):
    '''
    Read dataset configuration file and flatten the return object to the current use case.
    '''
    try:
        with open(path, "r") as FSO:
            config = json.load(FSO)
    except ValueError as e:
        print e
        print "Check {0}. Probably a ',' ".format(self.config_file)
        sys.exit(0)

    return config

if __name__ == '__main__':
    main()