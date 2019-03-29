from DataHandler import DataHandler
import os
import copy


class PredictionDataHandler(DataHandler):

    def __init__(self, settings, file_manager, config_parser, model, scaler):
        self.settings = settings
        self.file_manager = file_manager
        self.config_parser = config_parser
        self.model = model
        self.scaler = scaler

    def handle(self):
        print "Handling data for prediction..."
        self._handle_prediction_data()

    def _handle_prediction_data(self):
        #do something here (similar to what sandbox in run_model does)
        pass

    def sandbox(self, channel, model, scaler, sample, variables, outname, outpath, config=None, modify=None):
        # needed because of memory management
        # iterate over chunks of sample and do splitting on the fly
        first = True
        for part in sample:
            # This is awful. Try to figure out a better way to add stuff to generator.
            if modify:
                modify(part, config)

            part["THU"] = 1  # Add dummy
            # Carefull!! Check if splitting is done the same for training. This is the KIT splitting
            folds = [part.query("abs(evt % 2) != 0 ").reset_index(drop=True),
                     part.query("abs(evt % 2) == 0 ").reset_index(drop=True)]
            self.addPrediction(channel, model.predict(self.applyScaler(scaler, folds, variables)), folds, outname, outpath,
                          new=first)

            folds[0].drop(folds[0].index, inplace=True)
            folds[1].drop(folds[1].index, inplace=True)
            part.drop(part.index, inplace=True)

            first = False
        del sample

    def addPrediction(self, channel, prediction, df, sample, outpath, new=True):

        if not os.path.exists(outpath):
            os.mkdir(outpath)

        for i in xrange(len(df)):
            for c in prediction[i].columns.values.tolist():
                df[i][c] = prediction[i][c]

            if i == 0 and new:
                mode = "w"
            else:
                mode = "a"
            # df[i].to_root("{0}/{1}-{2}.root".format("predictions",channel, sample), key="TauCheck", mode = mode)
            df[i].to_root("{0}/{1}-{2}.root".format(outpath, channel, sample), key="TauCheck", mode=mode)
            prediction[i].drop(prediction[i].index, inplace=True)

    def applyScaler(self, scaler, folds, variables):
        if not scaler: return folds
        newFolds = copy.deepcopy(folds)
        for i, fold in enumerate(newFolds):
            fold[variables] = scaler[i].transform(fold[variables])
        return newFolds


