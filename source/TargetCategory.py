

class TargetCategory:

    def __init__(self, name, class_weight):
        self.name = name
        self.sample_sets = []
        self.class_weight = class_weight
        self.index = ""

    def get_name(self):
        return self.name

    def __str__(self):
        result = ""
        result += "[TargetCategory: " + self.name + ";" + str(self.index) + ";" + str(self.class_weight) + "]"
        return result
