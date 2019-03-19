import os

class FileManager():

    def __init__(self, outputpath = ""):
        self.outputpath = outputpath
        self.model_dir = "{0}/models/default/".format(outputpath)
        self.model_name = "empty"
        self.scaler_name = "empty"

    def set_model_name(self, name):
        self.model_name = name

    def set_scaler_name(self, name):
        self.scaler_name = name

    def set_model_dir(self, dirname):
        self.model_dir = "{0}/models/{1}/".format(self.outputpath, dirname)

    def get_model_dir(self):
        return self.model_dir

    def get_model_path(self):
        return "{0}/{1}".format(self.model_dir, self.model_name)

    def get_scaler_path(self):
        return "{0}/{1}".format(self.model_dir, self.scaler_name)

