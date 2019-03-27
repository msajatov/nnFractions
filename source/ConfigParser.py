import json
import sys
from SampleSet import SampleSet
from TargetCategory import TargetCategory
from ComplexCut import ComplexCut
from Cut import Cut


def main():
    cp = ConfigParser("mt", 2017, "conf/frac_config_mt_2017.json")


class ConfigParser:

    def __init__(self, channel, era, file_path):
        self.channel = channel
        self.era = era
        self.file_path = file_path

        self.sample_sets = []
        self.target_categories = []
        self.variable_names = []

        self.cut_dict = {}

        self.cut_config_path = "conf/cuts_{0}.json".format(era)
        self.read_cut_mapping(self.cut_config_path)
        self.parse(self.file_path)

    def parse(self, path):
        # parse config and return boolean to indicate success
        try:
            with open(path,"r") as FSO:
                config = json.load(FSO)
        except ValueError as e:
            print e
            print "Check {0}. Probably a ',' ".format(path)
            sys.exit(0)

        self._parse_variable_names(config)
        self._parse_categories(config)
        self._parse_sample_sets(config)

        self._add_samples_to_categories()

        for cat in self.target_categories:
            for sset in cat.sample_sets:
                print sset
            print "\n"

    def read_cut_mapping(self, cut_config_path):
        with open(cut_config_path, "r") as FSO:
            cuts = json.load(FSO)
            for c in cuts:
                cuts[c] = self._assert_channel(cuts[c])
            self.cut_dict = cuts

# sample_sets are still missing
    def _parse_categories(self, config):
        print "Parsing categories..."
        cat = TargetCategory("none", 1)
        cat.probability_var_index = -1
        self.target_categories.append(cat)

        for key in config["class_weight"]:
            val = config["class_weight"][key]
            name = key
            class_weight = self._assert_channel(val)
            target_cat = TargetCategory(name, class_weight)
            print target_cat
            self.target_categories.append(target_cat)

        print self.target_categories

        for i, target_cat in enumerate(self.target_categories):
            for key in config["target_values"]:
                val = config["target_values"][key]
                #print target_cat
                if key == target_cat.get_name():
                    prob_index = self._assert_channel(val)
                    target_cat.probability_var_index = prob_index

    def _parse_sample_sets(self, config):
        print "Parsing sample sets..."
        for key in config["samples"]:
            val = config["samples"][key]
            # this is not the full file path yet! (training vs. prediction?)
            source = self._assert_channel(val["name"])
            source_name = "{0}-{1}.root".format(self.channel, source)
            target_name = self._assert_channel(val["target"])
            # make this return a list of Cut instances
            cuts = self._parse_cut(val["select"])
            event_weight = self._assert_channel(val["event_weight"])

            #print "Filtering categories..."

            categories = [c for c in self.target_categories if c.name == target_name]
            #print "Remaining:"
            #print categories

            if len(categories) != 1:
                raise ValueError("Target category not found or ambiguous!")

            category = categories[0]

            sample_set = SampleSet(key, source_name, cuts, category, event_weight)
            self.sample_sets.append(sample_set)

            print sample_set

            # check if target is one of the valid, defined ones
            # for training: check if target is not the default one (none)

    def _parse_variable_names(self, config):
        print "Parsing variable names..."
        self.variable_names = self._assert_channel(config["variables"])

    def _add_samples_to_categories(self):
        for cat in self.target_categories:
            sample_sets = [sample for sample in self.sample_sets if sample.target.name == cat.name]
            cat.sample_sets = sample_sets



    def dummy(self, config):

        targets = []
        config["channel"] = self.channel
        config["path"] = config["path"].format(**config)  # Can be dropped when configs are split per channel
        config["outpath"] = config["outpath"].format(**config)
        config["target_names"] = {}
        config["variables"] = self._assertChannel(config["variables"])
        config["version"] = self._assertChannel(config["version"])
        for cw in config["class_weight"]:
            config["class_weight"][cw] = self._assertChannel(config["class_weight"][cw])

        for sample in config["samples"]:

            snap = config["samples"][sample]
            self.processes.append(sample)

            sample_name = self._assertChannel(snap["name"])
            snap["target"] = self._assertChannel(snap["target"])
            targets.append(snap["target"])

            snap["name"] = "{path}/{channel}-{name}.root".format(name=sample_name, **config)

            snap["select"] = self._parseCut(snap["select"])

            snap["event_weight"] = self._assertChannel(snap["event_weight"])

            if sample != "data" and sample != "estimate" and "_full" in sample:
                snap["shapes"] = self._getShapePaths(snap["name"], sample,
                                                     config["shape_from_file"],
                                                     config["shape_from_tree"])
                if type(snap["event_weight"]) is list:
                    config["addvar"] = list(set(config["addvar"] + snap["event_weight"]))

            config["samples"][sample] = snap

        targets.sort()
        targets = [t for t in targets if t != "none"]
        target_map = {"none": -1}

        for i, t in enumerate(set(targets)):
            config["target_names"][i] = t
            target_map[t] = i

        for sample in config["samples"]:
            config["samples"][sample]["target_name"] = config["samples"][sample]["target"]

            if "target_values" in config:
                config["samples"][sample]["target"] = int(
                    config["target_values"].get(config["samples"][sample]["target"], -1))
            else:
                config["samples"][sample]["target"] = target_map.get(config["samples"][sample]["target"], -1)

            config["target_names"][config["samples"][sample]["target"]] = config["samples"][sample]["target_name"]

        return config

    def _assert_channel(self, entry):
        if type(entry) is dict:
            return entry[self.channel]
        else:
            return entry

    def _parse_cut(self, cutstring):
        cutstring = self._assert_channel(cutstring)
        for alias, cut in self.cut_dict.items():
            cutstring = cutstring.replace(alias, cut)
        return cutstring

    def _parse_cut_new(self, cutstring):
        complex_cut = ComplexCut(self.cut_config_path)
        cutstring = self._assert_channel(cutstring)

        aliases = cutstring.split("&&")
        #print aliases

        stripped_aliases = []
        for alias in aliases:
            stripped_aliases.append(alias.strip())

        for stripped_alias in stripped_aliases:
            full_cut_string = self.cut_dict[stripped_alias]
            complex_cut.add_cut(Cut(stripped_alias, full_cut_string))

        print str(complex_cut)
        return complex_cut


if __name__ == '__main__':
    main()
