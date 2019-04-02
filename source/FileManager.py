import os

class FileManager():

    def __init__(self, outputpath=""):
        self.outputpath = outputpath
        self.model_dirname = "models/default"
        self.model_dirpath = "{0}/{1}".format(self.outputpath, self.model_dirname)
        self.model_filename = "empty"
        self.model_filepath = "empty"
        self.scaler_dirname = "models/default"
        self.scaler_dirpath = "{0}/{1}".format(self.outputpath, self.model_dirname)
        self.scaler_filename = "empty"
        self.scaler_filepath = "empty"
        self.prediction_dirname = "predictions/default"
        self.prediction_dirpath = "{0}/{1}/".format(self.outputpath, self.prediction_dirname)
        self.datacard_config_dirname = "datacard/conf/default"
        self.datacard_config_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_config_dirname)
        self.datacard_dirname = "datacard/default"
        self.datacard_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_dirname)
        self.datacard_plot_dirname = "datacard/plot/default"
        self.datacard_plot_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_plot_dirname)

        self.plot_dirname = "plots/default"
        self.plot_dirpath = "{0}/{1}".format(self.outputpath, self.plot_dirname)

        self.fractions_filepath = ""

    def get_output_root_path(self):
        return self.outputpath

    def set_model_filename(self, name):
        self.model_filename = name
        self.model_filepath = "{0}/{1}".format(self.model_dirpath, self.model_filename)

    def set_scaler_filename(self, name):
        self.scaler_filename = name
        self.scaler_filepath = "{0}/{1}".format(self.scaler_dirpath, self.scaler_filename)

    def set_model_dirname(self, model_dir):
        # used as root dir for both model and scaler
        self.model_dirname = model_dir
        self.model_dirpath = "{0}/{1}".format(self.outputpath, self.model_dirname)

        self.scaler_dirname = model_dir
        self.scaler_dirpath = "{0}/{1}".format(self.outputpath, self.model_dirname)

        if not os.path.exists(self.model_dirpath):
            os.makedirs(self.model_dirpath)

    def get_model_dirname(self):
        return self.model_dirname

    def get_model_dirpath(self):
        return self.model_dirpath

    def get_model_filename(self):
        return self.model_filename

    def get_model_filepath(self):
        return self.model_filepath

    def get_scaler_filename(self):
        return self.scaler_filename

    def get_scaler_filepath(self):
        return self.scaler_filepath

    def set_prediction_dirname(self, prediction_dir):
        self.prediction_dirname = prediction_dir
        self.prediction_dirpath = "{0}/{1}".format(self.outputpath, self.prediction_dirname)
        if not os.path.exists(self.prediction_dirpath):
            os.makedirs(self.prediction_dirpath)

    def get_prediction_dirpath(self):
        return self.prediction_dirpath

    def set_datacard_config_dirname(self, datacard_config_dir):
        self.datacard_config_dirname = datacard_config_dir
        self.datacard_config_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_config_dirname)
        if not os.path.exists(self.datacard_config_dirpath):
            print "Warning: Datacard config dir does not exist ({0})".format(self.datacard_config_dirpath)

    def get_datacard_config_dirpath(self):
        return self.datacard_config_dirpath

    def get_datacard_config_dirname(self):
        return self.datacard_config_dirname

    def set_datacard_output_dirname(self, datacard_dir):
        self.datacard_dirname = datacard_dir
        self.datacard_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_dirname)
        if not os.path.exists(self.datacard_dirpath):
            print "Warning: Datacard config dir does not exist ({0})".format(self.datacard_dirpath)

    def get_datacard_output_dirpath(self):
        return self.datacard_dirpath

    def get_datacard_output_dirname(self):
        return self.datacard_dirname

    def set_datacard_plot_dirname(self, datacard_dir):
        self.datacard_plot_dirname = datacard_dir
        self.datacard_plot_dirpath = "{0}/{1}".format(self.outputpath, self.datacard_plot_dirname)
        if not os.path.exists(self.datacard_plot_dirpath):
            print "Warning: Datacard config dir does not exist ({0})".format(self.datacard_plot_dirpath)

    def get_datacard_plot_dirpath(self):
        return self.datacard_plot_dirpath

    def get_datacard_plot_dirname(self):
        return self.datacard_plot_dirname

    def set_fractions_filepath(self, path):
        self.fractions_filepath = path

    def get_fractions_filepath(self):
        return self.get_fractions_filepath()

    def set_plot_dirname(self, dirname):
        self.plot_dirname = dirname
        self.plot_dirpath = "{0}/{1}".format(self.outputpath, self.plot_dirname)
        if not os.path.exists(self.plot_dirpath):
            os.makedirs(self.plot_dirpath)

    def get_plot_dirpath(self):
        return self.plot_dirpath


