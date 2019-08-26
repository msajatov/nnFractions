from DataController import DataController
from Tools.NNCore.PredictionWrapper import PredictionWrapper

import os
import cPickle


class PredictionHelper:

    def __init__(self, settings):
        self.settings = settings
        self.file_manager = settings.prediction_file_manager
        self.parser = settings.config_parser
        self.sample_sets = settings.filtered_samples
        self.scaler = 0
        self.model = 0
        self.ext_input = settings.ext_input
        self.prediction = None
        self.setup_prediction()

    def setup_prediction(self):
        pred = PredictionWrapper(self.settings)

        scaler_path = self.file_manager.get_scaler_filepath()
        model_path = self.file_manager.get_model_filepath()

        pred.setup(model_path, scaler_path)
        self.prediction = pred

    def predict(self):

        print "scaler: ", self.scaler
        controller = DataController(self.parser.data_root_path, 2, self.parser, self.settings, self.ext_input,
                                    sample_sets=[])

        sample_info_dicts = controller.prepare(self.sample_sets)

        first = True
        for sample_info in sample_info_dicts:
            print "predicting for " + sample_info["histname"]
            if self.ext_input:
                sample_info["path"] = sample_info["path"].replace("WJets", "W")

            filename = "NOMINAL_ntuple_" + sample_info["histname"].split("_")[0]
            filename = filename.replace("data", "Data")
            dirpath = self.file_manager.get_dir_path("prediction_output_dir")
            outpath = "{0}/{1}-{2}.root".format(dirpath, self.settings.channel, filename)

            invert = False

            iter = controller.read_for_prediction(sample_info)
            for data_frame in iter:
                # if not self.ext_input:
                #     controller.modifyDF(data_frame, sample_info)
                prediction_folds = self.prediction.get_prediction_folds(data_frame, "evt", invert=invert)
                self.addPredictionToOutput(prediction_folds, data_frame, outpath, first, invert=invert)
                first = False

    def addPredictionToOutput(self, prediction, df, outpath, new=True, invert=False):

        reordered = []

        if invert:
            reordered.append(prediction[1])
            reordered.append(prediction[0])
        else:
            reordered = prediction

        folds = PredictionWrapper.splitInFolds(df)
        df.drop(df.index, inplace=True)

        for i in xrange(len(folds)):
            for c in reordered[i].columns.values.tolist():
                folds[i][c] = reordered[i][c]

            if i == 0 and new:
                mode = "w"
            else:
                mode = "a"
            folds[i].to_root(outpath, key="TauCheck", mode=mode)
            prediction[i].drop(prediction[i].index, inplace=True)
            folds[i].drop(folds[i].index, inplace=True)