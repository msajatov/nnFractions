class SampleSet:

    def __init__(self, name, source_file_name, cut, target, event_weight):
        self.name = name
        self.source_file_name = source_file_name
        self.cut = cut
        self.target = target
        self.event_weight = event_weight

    def get_name(self):
        return self.name

    def __str__(self):
        result = ""
        result += "[SampleSet: " + "\n"
        result += "Name: " + self.name + "\n"
        result += "Source: " + self.source_file_name + "\n"
        result += "Source Path: " + self.source_file_name + "\n"
        result += "Cut: " + self.cut + "\n"
        result += "Target: " + str(self.target) + "\n"
        result += "Event Weight: " + str(self.event_weight) + "]" + "\n"
        return result
