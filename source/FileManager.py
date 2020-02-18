import os
import json
from PathObject import DirPathObject, FilePathObject


class FileManager():

    def __init__(self, path_config_path, settings=None):

        self.paths = {}
        self.config = {}

        self.path_config_path = path_config_path
        self.outputpath = ""
        self.sample_config_path = ""
        self.settings = settings

        FileManager.parse_path_config(self, path_config_path)

    @staticmethod
    def create_dir(path):
        try:
            if not os.path.exists(path):
                os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

    def parse_path_config(self, path):
        # parse config and return boolean to indicate success
        try:
            with open(path, "r") as FSO:
                config = json.load(FSO)
        except ValueError as e:
            print e
            print "Check {0}. Probably a ',' ".format(path)
            #sys.exit(0)

        self.config = config
        self.outputpath = config["output"]["output_root_dir"]
        self.sample_config_path = config["samples"]["sample_config"]

    def get_sample_config_path(self):
        return self.sample_config_path

    def get_path_config_path(self):
        return self.path_config_path

    def get_dir_path(self, type):
        if type in self.paths:
            return self.paths[type].get_path()
        else:
            print type + " not found in registered paths!"

    def get_dir_name(self, type):
        if type in self.paths:
            return self.paths[type].get_name()
        else:
            print type + " not found in registered paths!"

    def set_dir_name(self, type, dir_name):
        if type in self.paths:
            return self.paths[type].set_name(dir_name)
        else:
            print type + " not found in registered paths!"


class ModelFileManager(FileManager):

    def __init__(self, path_config_path, settings):
        FileManager.__init__(self, path_config_path, settings)
        self.filepaths = {}
        if path_config_path:
            print "parsing path config..."
            self.parse_path_config(path_config_path)
        self.incorporate_era(settings)

    def parse_path_config(self, path):

        conf = self.config["model"]

        model_identifier = "{0}_{1}_{2}".format(self.settings.name, self.settings.varset, self.settings.get_emb_suffix())

        path = conf["model_output_dir"].format(model_identifier)
        type = "model_output_dir"
        self.paths["model_output_dir"] = DirPathObject(type, self.outputpath, path)

        # sic! use model_output_dir for scaler_output_dir
        path = conf["model_output_dir"].format(model_identifier)
        type = "scaler_output_dir"
        self.paths["scaler_output_dir"] = DirPathObject(type, self.outputpath, path)

    def incorporate_era(self, settings):
        era = settings.era
        model = settings.ml_type
        channel = settings.channel

        model_dir = self.get_dir_name("model_output_dir")
        model_dir = model_dir + "/" + era
        model_name = "{0}.{1}".format(channel, model)

        self.set_dir_name("model_output_dir", model_dir)
        self.set_dir_name("scaler_output_dir", model_dir)
        self.set_model_filename(model_name)

        self.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))

    def set_model_filename(self, name):
        model_dir_path = self.paths["model_output_dir"].get_path()
        self.filepaths["model_file"] = FilePathObject("model_file", model_dir_path, name)

    def set_scaler_filename(self, name):
        scaler_dir_path = self.paths["scaler_output_dir"].get_path()
        self.filepaths["scaler_file"] = FilePathObject("scaler_file", scaler_dir_path, name)

    def get_model_filename(self):
        type = "model_file"
        if type in self.filepaths:
            return self.filepaths[type].get_name()
        else:
            print type + " not found in registered filepaths!"

    def get_model_filepath(self):
        type = "model_file"
        if type in self.filepaths:
            return self.filepaths[type].get_path()
        else:
            print type + " not found in registered filepaths!"

    def get_scaler_filename(self):
        type = "scaler_file"
        if type in self.filepaths:
            return self.filepaths[type].get_name()
        else:
            print type + " not found in registered filepaths!"

    def get_scaler_filepath(self):
        type = "scaler_file"
        if type in self.filepaths:
            return self.filepaths[type].get_path()
        else:
            print type + " not found in registered filepaths!"


class PredictionFileManager(FileManager):

    def __init__(self, path_config_path, settings):
        FileManager.__init__(self, path_config_path, settings)
        self.filepaths = {}
        if path_config_path:
            print "parsing path config..."
            self.parse_path_config(path_config_path)
        self.incorporate_era(settings)

    def parse_path_config(self, path):

        conf = self.config["prediction"]

        model_identifier = "{0}_{1}_{2}".format(self.settings.name, self.settings.varset, self.settings.get_emb_suffix())

        path = conf["model_input_dir"].format(model_identifier)
        type = "model_input_dir"
        self.paths["model_input_dir"] = DirPathObject(type, self.outputpath, path)

        # sic! use model_input_dir for scaler_input_dir
        path = conf["model_input_dir"].format(model_identifier)
        type = "scaler_input_dir"
        self.paths["scaler_input_dir"] = DirPathObject(type, self.outputpath, path)

        path = conf["prediction_output_dir"].format(model_identifier)
        type = "prediction_output_dir"
        self.paths["prediction_output_dir"] = DirPathObject(type, self.outputpath, path)

    def incorporate_era(self, settings):
        era = settings.era
        model = settings.ml_type
        channel = settings.channel

        model_dir = self.get_dir_name("model_input_dir")
        model_dir = model_dir + "/" + era
        model_name = "{0}.{1}".format(channel, model)

        self.set_dir_name("model_input_dir", model_dir)
        self.set_dir_name("scaler_input_dir", model_dir)
        self.set_model_filename(model_name)

        prediction_dir = self.get_dir_name("prediction_output_dir")
        prediction_dir = prediction_dir + "/" + era
        self.set_dir_name("prediction_output_dir", prediction_dir)

        self.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))


    def set_model_filename(self, name):
        model_dir_path = self.paths["model_input_dir"].get_path()
        self.filepaths["model_file"] = FilePathObject("model_file", model_dir_path, name)

    def set_scaler_filename(self, name):
        scaler_dir_path = self.paths["scaler_input_dir"].get_path()
        self.filepaths["scaler_file"] = FilePathObject("scaler_file", scaler_dir_path, name)

    def get_model_filename(self):
        type = "model_file"
        if type in self.filepaths:
            return self.filepaths[type].get_name()
        else:
            print type + " not found in registered filepaths!"

    def get_model_filepath(self):
        type = "model_file"
        if type in self.filepaths:
            return self.filepaths[type].get_path()
        else:
            print type + " not found in registered filepaths!"

    def get_scaler_filename(self):
        type = "scaler_file"
        if type in self.filepaths:
            return self.filepaths[type].get_name()
        else:
            print type + " not found in registered filepaths!"

    def get_scaler_filepath(self):
        type = "scaler_file"
        if type in self.filepaths:
            return self.filepaths[type].get_path()
        else:
            print type + " not found in registered filepaths!"


class FractionPlotFileManager(FileManager):

    def __init__(self, path_config_path, settings):
        FileManager.__init__(self, path_config_path, settings)
        if path_config_path:
            print "parsing path config..."
            self.parse_path_config(path_config_path)
        self.incorporate_era(settings)

    def parse_path_config(self, path):

        conf = self.config["fracplots"]

        model_identifier = "{0}_{1}_{2}".format(self.settings.name, self.settings.varset, self.settings.get_emb_suffix())

        path = conf["prediction_input_dir"].format(model_identifier)
        type = "prediction_input_dir"
        self.paths["prediction_input_dir"] = DirPathObject(type, self.outputpath, path)

        path = conf["fracplot_output_dir"].format(model_identifier)
        type = "fracplot_output_dir"
        self.paths["fracplot_output_dir"] = DirPathObject(type, self.outputpath, path)

    def incorporate_era(self, settings):
        era = settings.era

        prediction_dir = self.get_dir_name("prediction_input_dir")
        prediction_dir = prediction_dir + "/" + era
        self.set_dir_name("prediction_input_dir", prediction_dir)

        plot_dir = self.get_dir_name("fracplot_output_dir")
        plot_dir = "{0}/{1}".format(plot_dir, era)
        self.set_dir_name("fracplot_output_dir", plot_dir)

