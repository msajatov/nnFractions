import Cut
import json


class ComplexCut:

    def __init__(self, cut_config_path=""):
        self.cuts = []
        self.cut_dict = {}
        self.cut_config_path = cut_config_path

    def add_cut(self, cut):
        self.cuts.append(cut)

    def add_cut_by_alias(self, alias, cut_config_path):
        if not self.cut_dict:
            self.read_cut_mapping(cut_config_path)
        cut_string = self.cut_dict[alias]
        cut = Cut(alias, cut_string)
        self.cuts.append(cut)

    def add_cut_by_alias(self, alias):
        self.add_cut_by_alias(alias, self.cut_config_path)

    def read_cut_mapping(self, cut_config_path):
        with open(cut_config_path, "r") as FSO:
            self.cut_dict = json.load(FSO)

    def __str__(self):
        result = ""
        for item in self.cuts:
            result += str(item) + "\n"
        return result
