class Cut:

    def __init__(self, alias, full_cut_string):
        self.alias = alias
        self.full_cut_string = full_cut_string

    def __str__(self):
        return "[Cut: " + self.alias + ";" + self.full_cut_string + "]"
