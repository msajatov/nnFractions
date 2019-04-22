import os
import sys
from shutil import copy


class Logger:

    def __init__(self, settings, file_manager, sample_sets):
        self.settings = settings
        self.file_manager = file_manager
        self.sample_sets = sample_sets


class TrainingLogger(Logger):
    def __init__(self, settings, file_manager, sample_sets):
        Logger.__init__(self, settings, file_manager, sample_sets)
        pass

    def log(self):
        dirpath = self.file_manager.get_dir_path("model_output_dir")
        filepath = dirpath + "/log_{0}_{1}_{2}.txt".format(self.settings.channel, self.settings.era, self.settings.ml_type)
        if os.path.exists(filepath):
            filepath += "_err"
            with open(filepath, 'w') as f:
                print >> f, "Log file already exists in this directory. Did not overwrite.\n"     # Python 2.x
            print "Stopped to prevent overwriting of existing files"
            sys.exit(-5)
        else:
            with open(filepath, 'w') as f:
                print >> f, "Training for", self.settings.channel, self.settings.era, self.settings.ml_type
                print >> f, "Config used is", self.file_manager.get_sample_config_path().format(self.settings.channel, self.settings.era)
                print >> f, "Model output dir is", self.file_manager.get_dir_path("model_output_dir")
                print >> f, "Samples: \n"

                for sset in self.sample_sets:
                    print >> f, sset
            self.copy_configs(dirpath)


    def copy_configs(self, dir):
        dest_dir = dir + "/conf_" + self.settings.channel
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        copy(self.file_manager.get_sample_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy(self.file_manager.get_path_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy("conf/parameters_keras.json", dest_dir)
        pass

    def write_to_file(self, file):
        pass


class PredictionLogger(Logger):
    def __init__(self, settings, file_manager, sample_sets):
        Logger.__init__(self, settings, file_manager, sample_sets)
        pass

    def log(self):
        dirpath = self.file_manager.get_dir_path("prediction_output_dir")
        filepath = dirpath + "/log_{0}_{1}_{2}.txt".format(self.settings.channel, self.settings.era,
                                                           self.settings.ml_type)
        if os.path.exists(filepath):
            filepath += "_err"
            with open(filepath, 'w') as f:
                print >> f, "Log file already exists in this directory. Did not overwrite.\n"  # Python 2.x
            print "Stopped to prevent overwriting of existing files"
            sys.exit(-5)
        else:
            with open(filepath, 'w') as f:
                print >> f, "Predicting for", self.settings.channel, self.settings.era, self.settings.ml_type
                print >> f, "Config used is", self.file_manager.get_sample_config_path().format(
                    self.settings.channel, self.settings.era)
                print >> f, "Model input dir is", self.file_manager.get_dir_path("model_input_dir")
                print >> f, "Prediction output dir is", self.file_manager.get_dir_path("prediction_output_dir")
                print >> f, "Samples: \n"

                for sset in self.sample_sets:
                    print >> f, sset
            self.copy_configs(dirpath)

    def copy_configs(self, dir):
        dest_dir = dir + "/conf_" + self.settings.channel
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        copy(self.file_manager.get_sample_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy(self.file_manager.get_path_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy("conf/parameters_keras.json", dest_dir)
        pass

    def write_to_file(self, file):
        pass


class FractionPlotLogger(Logger):
    def __init__(self, settings, file_manager, sample_sets):
        Logger.__init__(self, settings, file_manager, sample_sets)
        pass

    def log(self):
        dirpath = self.file_manager.get_dir_path("fracplot_output_dir")
        filepath = dirpath + "/log_{0}_{1}_{2}.txt".format(self.settings.channel, self.settings.era,
                                                           self.settings.ml_type)
        if os.path.exists(filepath):
            filepath += "_err"
            with open(filepath, 'w') as f:
                print >> f, "Log file already exists in this directory. Did not overwrite.\n"  # Python 2.x
            print "Stopped to prevent overwriting of existing files"
            sys.exit(-5)
        else:
            with open(filepath, 'w') as f:
                print >> f, "Plotting fractions for", self.settings.channel, self.settings.era, self.settings.ml_type
                print >> f, "Config used is", self.file_manager.get_sample_config_path().format(
                    self.settings.channel, self.settings.era)
                print >> f, "Prediction input dir is", self.file_manager.get_dir_path("prediction_input_dir")
                print >> f, "Fraction plot output dir is", self.file_manager.get_dir_path("fracplot_output_dir")
                print >> f, "Samples: \n"

                for sset in self.sample_sets:
                    print >> f, sset
            self.copy_configs(dirpath)

    def copy_configs(self, dir):
        dest_dir = dir + "/conf_" + self.settings.channel
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        copy(self.file_manager.get_sample_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy(self.file_manager.get_path_config_path().format(self.settings.channel, self.settings.era), dest_dir)
        copy("conf/parameters_keras.json", dest_dir)
        pass

    def write_to_file(self, file):
        pass

