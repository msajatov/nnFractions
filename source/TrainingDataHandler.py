from DataHandler import DataHandler
from FileManager import FileManager
from ConfigParser import ConfigParser
import copy
import cPickle
import pandas
import keras
import os


class TrainingDataHandler(DataHandler):

    def __init__(self, settings, file_manager, config_parser, model, scaler):
        self.settings = settings
        self.file_manager = file_manager
        self.config_parser = config_parser
        #model and scaler are references that will be written to -> usable later on the outside if needed
        self.model = model
        self.scaler = scaler

    def handle(self, data_frame):
        print "Handling data for prediction..."
        self._handle_training_data(data_frame)

    def _handle_training_data(self, data_frame):
        #do something here (similar to what training in run_model does)

        if self.settings.ml_type == "xgb":
            from XGBModel import XGBObject as modelObject
            parameters = "conf/parameters_xgb.json"

        if self.settings.ml_type == "keras":
            print "Using keras..."
            from KerasModel import KerasObject as modelObject
            parameters = "conf/parameters_keras.json"

        print "Training new model"
        print "Loading Training set"
        trainSet = data_frame

        print "Fit Scaler to training set...",
        scaler = self.trainScaler(trainSet, self.config_parser.variables)

        print " done. Dumping for later."

        with open(self.file_manager.get_scaler_filepath(), 'wb') as FSO:
            cPickle.dump(scaler, FSO, 2)
        scaler = [scaler, scaler]  # Hotfix since KIT uses 2 scalers

        trainSet = self.applyScaler(scaler, trainSet, self.config_parser.variables)

        model = modelObject(parameter_file=parameters,
                            variables=self.config_parser.variables,
                            target_names=self.config_parser.get_target_names)
        model.train(trainSet)
        model.save(self.file_manager.get_model_filepath())

    def trainScaler(self, folds, variables):
        from sklearn.preprocessing import StandardScaler

        total = pandas.concat(folds, ignore_index=True).reset_index(drop=True)
        scaler = StandardScaler()
        scaler.fit(total[variables])

        return scaler

    def applyScaler(self, scaler, folds, variables):
        if not scaler:
            return folds
        new_folds = copy.deepcopy(folds)
        for i, fold in enumerate(new_folds):
            fold[variables] = scaler[i].transform(fold[variables])
        return new_folds
