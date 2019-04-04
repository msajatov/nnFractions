import json
import pandas
import root_pandas as rp
import os
import sys
from DataHandler import DataHandler
from ConfigParser import ConfigParser
from SampleSet import SampleSet
from DataReader import DataReader
import time


def main():
    pass
    #DR = DataReader("mt", "conf/global_config_2016.json", 2)


class DataController:

    def __init__(self, root_path, folds, config_parser, settings, sample_sets):
        self.root_path = root_path
        self.folds = folds
        self.config_parser = config_parser
        self.settings = settings
        self.sample_sets = sample_sets
        self.sample_info_dicts = []

    def set_root_path(self, root_path):
        self.root_path = root_path

    def set_sample_sets(self, sample_sets):
        self.sample_sets = sample_sets

    def read_for_training(self, sample_info_dicts=[]):
        #self.read_and_process(self, sample_sets, split_in_folds=True, use_chunks=False)

        start = time.time()
        # check if chunking is needed / requested

        print "info dicts: "
        print len(self.sample_info_dicts)

        training_samples = []
        for_prediction = False

        self.sample_info_dicts.sort()

        for sample_info in sample_info_dicts:
            # this may be one fold or two folds -> use parameter properly
            loaded_data_frame = self.loadForMe(sample_info, for_prediction)
            training_samples.append(loaded_data_frame)

        print "Combining for fraction training"
        training_folds = self.combineFolds(training_samples)

        end = time.time()

        time_diff = end - start

        print "Time Diff: "
        print time_diff

        #self.data_handler.handle(training_folds, "")
        return training_folds

    def read_for_prediction(self, sample_info):
        #self.read_and_process(self, sample_sets, split_in_folds=True, use_chunks=True)

        # check if chunking is needed / requested

        for_prediction = True
        # this may be one fold or two folds -> use parameter properly
        data_frame_iterator = self.loadForMe(sample_info, for_prediction)
        print "predicting for " + sample_info["histname"]
        return data_frame_iterator


    #def read_and_process(self, sample_sets, split_in_folds=True, use_chunks=False):

        # self.prepare()
        # # check if chunking is needed / requested
        #
        # for_prediction = not use_chunks
        #
        # if (use_chunks):
        #
        #     # process chunks
        # else:
        #     for sample_info in self.sample_info_dicts:
        #         # this may be one fold or two folds -> use parameter properly
        #         loaded_data_frame = self.loadForMe(sample_info, for_prediction)
        #         self.data_handler.handle(loaded_data_frame)
        # return

    def prepare(self, sample_sets):
        sample_info_dicts = []
        for sset in sample_sets:
            info_dict = self._getCommonSettings(sset)
            sample_info_dicts.append(info_dict)

        return sample_info_dicts





       ##########################################################################################

    def _getFolds(self, df):
        if self.folds != 2:
            raise NotImplementedError("Only implemented two folds so far!!!")
        return [df.query("abs(evt % 2) != 0 ").reset_index(drop=True),
                df.query("abs(evt % 2) == 0 ").reset_index(drop=True)]

    def _getDF(self, sample_path, select, for_prediction):

        add = "addvar"
        if "Embedd" in sample_path:
            add = "addvar_Embedding"

        snowflakes = ["evt"]
        if "ggH" in sample_path:
            snowflakes.append("THU*")
            snowflakes.append("*NNLO*")

        branches = list(set(self.config_parser.variable_names + self.config_parser.weights + snowflakes + self.config_parser.additional_variable_names))
        #branches = list(set(self.config["variables"] + self.config["weights"] + snowflakes + self.addvar))
        if "EMB" in sample_path and "sf*" in branches:
            branches.remove("sf*")

        # Return iterator when predicting samples
        chunksize = None
        if for_prediction:
            chunksize = 100000

        tmp = rp.read_root(paths=sample_path,
                           where=select,
                           columns=branches,
                           chunksize=chunksize)

        # tmp.replace(-999.,-10, inplace = True)
        # tmp["evt"] = tmp["evt"].astype('int64')

        return tmp

    def combineFolds(self, samples):

        #print "samples: "
        #print samples

        folds = [ [fold] for fold in samples[0] ]
        for sample in samples[1:]:
            for i in xrange(len(folds)):
                folds[i].append( sample[i] )

        for i,fold in enumerate(folds):
            folds[i] = pandas.concat( fold, ignore_index=True).sample(frac=1., random_state = 41).reset_index(drop=True)

        return folds

    def modifyDF(self, DF, sample_info):

        DF["evt"] = DF["evt"].astype('int64')
        DF.eval( "event_weight = " + sample_info["event_weight"], inplace = True  )
        DF["target"] = sample_info["target"]
        #DF["train_weight"] = DF["event_weight"].abs() * self.config["class_weight"].get(sample_info["target_name"], 1.0 )

        class_weight = sample_info["class_weight"]

        DF["train_weight"] = DF["event_weight"].abs() * class_weight
        DF.replace(-999.,-10, inplace = True)

        for new, old in sample_info["rename"]:
            if new in DF.columns.values.tolist() and old in DF.columns.values.tolist():
                DF[old] = DF[new]
            # else:
            #     print "cant rename {0} to {1}".format(old, new)

        if self.settings.era == "2016":
            DF.replace({"jdeta":-10.},-1., inplace = True)
            DF.replace({"mjj":-10.},-11., inplace = True)
            DF.replace({"dijetpt":-10.},-11., inplace = True)

            DF.eval("jdeta =   (njets < 2) *-1  + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-11 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-11 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)


        if self.settings.era == "2017":
            DF.replace({"jdeta":-1.},-10., inplace = True)
            DF.replace({"mjj":-11.},-10., inplace = True)
            DF.replace({"dijetpt":-11.},-10., inplace = True)

            DF.eval("jdeta =   (njets < 2) *-10 + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-10 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-10 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)

    def _getCommonSettings(self, sample_set):
        # using SampleSet and TargetCategory
        settings = {}
        settings["event_weight"] = self._getEventWeight(sample_set)
        settings["target"] = sample_set.target.index
        settings["target_name"] = sample_set.target.name
        settings["select"] = sample_set.cut
        settings["path"] = "{0}/{1}".format(self.root_path, sample_set.source_file_name)
        settings["histname"] = sample_set.name
        settings["class_weight"] = sample_set.target.class_weight
        settings["rename"] = {}

        return settings

    def _getEventWeight(self, sample_set):
        if type(sample_set.event_weight) is list:
            return "*".join(sample_set.event_weight + [str(self.config_parser.lumi)])

        if type(sample_set.event_weight) is float:
            return str(sample_set.event_weight)

        if type(sample_set.event_weight) is unicode:
            return "*".join([sample_set.event_weight, str(self.config_parser.lumi)])

        else:
            return 1.0

    def loadForMe(self, sample_info, for_prediction):
        if not os.path.exists(sample_info["path"]):
            print "\033[1;31mWarning:\033[0m ", self.constStrLen(sample_info["histname"]), sample_info["path"].split("/")[-1]
            return []

        print "\033[1;32mLoading:\033[0m ", self.constStrLen(sample_info["histname"]), sample_info["path"].split("/")[-1]
        DF = self._getDF(sample_path=sample_info["path"],
                         select=sample_info["select"],
                         for_prediction=for_prediction)

        # A bit hacky. Return  iterator when predicting to reduce memory consumption
        # Otherweise split in folds

        if for_prediction:
            return DF

        num = len(DF.index)
        print "Entries in DF before modification: " + str(num)

        self.modifyDF(DF, sample_info)

        return self._getFolds(DF[self.config_parser.variable_names + ["target", "train_weight", "evt", "event_weight"]])

    def constStrLen(self, string):
        return string + " " * (40 - len(string))

    def get_training_folds(self, sample_sets):
        return []

    def split_in_folds(self, sample_data_frame):
        return []






