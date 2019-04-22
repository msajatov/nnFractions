import os
import sys


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
        else:
            with open(filepath, 'w') as f:
                print >> f, "Training for ", self.settings.channel, self.settings.era, self.settings.ml_type
                print >> f, "Config used is ", self.file_manager.get_sample_config_path().format(self.settings.channel, self.settings.era)
                print >> f, "Samples: \n"

                for sset in self.sample_sets:
                    print >> f, sset


    def copy_configs(self, dir):
        pass

    def write_to_file(self, file):
        pass

