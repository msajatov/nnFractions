from PredictionDataHandler import PredictionDataHandler
from DataController import DataController
import os
import cPickle


class Prediction:

    def __init__(self, settings):
        self.settings = settings
        self.file_manager = settings.prediction_file_manager
        self.parser = settings.config_parser
        self.sample_sets = settings.filtered_samples
        self.scaler = 0
        self.model = 0
        self.ext_input = settings.ext_input
        self.setup()

    def setup(self):
        if self.settings.scaler == "standard":
            if os.path.exists(self.file_manager.get_scaler_filepath()):
                print "Loading Scaler"
                with open(self.file_manager.get_scaler_filepath(), "rb") as FSO:
                    tmp = cPickle.load(FSO)
                    self.scaler = [tmp, tmp]
            else:
                print "Fatal: Scaler file not found at {0}. Train model using -t first.".format(
                    self.file_manager.get_scaler_filepath())
                return

        print "Loading model and predicting."
        if self.settings.ml_type == "xgb":
            print "Using xgb..."
            from XGBModel import XGBObject as modelObject

        if self.settings.ml_type == "keras":
            import keras
            print "Using keras", keras.__version__
            from KerasModel import KerasObject as modelObject

        self.model = modelObject(filename=self.file_manager.get_model_filepath())

    def predict(self):
        print "scaler: ", self.scaler
        prediction_handler = PredictionDataHandler(self.settings, self.file_manager, self.parser, self.model, self.scaler)
        controller = DataController(self.parser.data_root_path, 2, self.parser, self.settings, self.ext_input, sample_sets=[])

        sample_info_dicts = controller.prepare(self.sample_sets)

        first = True
        for sample_info in sample_info_dicts:
            print "predicting for " + sample_info["histname"]
            if self.ext_input:
                sample_info["path"] = sample_info["path"].replace("WJets", "W")
            # this may be one fold or two folds -> use parameter properly
            iter = controller.read_for_prediction(sample_info)
            for df in iter:
                if not self.ext_input:
                    controller.modifyDF(df, sample_info)
                prediction_handler.handle(df, sample_info, first)
                first = False