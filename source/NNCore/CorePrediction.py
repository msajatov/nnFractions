import os
import copy
from pandas import DataFrame, concat

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class CorePrediction():

    def __init__(self, settings):
        self.settings = settings
        self.model = None
        self.scaler = None

    def setup(self, settings, model, scaler=None):
        self.settings = settings
        self.model = model
        self.scaler = scaler

    def get_prediction_folds_for_data_frame(self, data_frame, keep=[]):
        self.modifyDFForPrediction(data_frame)

        # this is a copy
        folds = self.splitInFolds(data_frame)

        prediction = self.get_prediction_folds_for_folds(folds, keep=keep)
        return prediction

    def get_prediction_folds_for_folds(self, folds, keep=[]):
        if self.scaler == 0 or self.scaler == None:
            logger.debug("Scaler is zero")
            unscaled = copy.deepcopy(folds)
            prediction = self.model.predict(unscaled)
            logger.debug("got prediction from model")
            unscaled[0].drop(unscaled[0].index, inplace=True)
            unscaled[1].drop(unscaled[1].index, inplace=True)
        else:
            logger.debug("Scaler is not zero")
            scaled = self.applyScaler(self.scaler, folds, self.model.variables)
            # TODO check if columns in keep exist in dataframe, if not -> ignore
            logger.debug("scaled:")
            logger.debug(scaled)
            
            prediction = self.model.predict(scaled)
            logger.debug("got prediction from model")
            scaled[0].drop(scaled[0].index, inplace=True)
            scaled[1].drop(scaled[1].index, inplace=True)
            
        if keep:
            logger.debug("keep specified")
            for i, prediction_fold in enumerate(prediction):
                # append "keep" columns from original data_frame to prediction if they exist
                try:
                    logger.debug("loc")
                    original_df_columns = folds[i].loc[:, keep]
                    logger.debug("keep columns: " + str(original_df_columns))
                    logger.debug("join")
                    prediction_fold = prediction_fold.join(original_df_columns)
                    prediction[i] = prediction_fold
                    logger.debug(prediction_fold)
                except KeyError:
                    logger.debug("Specified column labels not found in data frame")
                    raise KeyError
        else:
            logger.debug("keep not specified")

        logger.debug("Prediction before dropping: " + str(prediction))

        # dropping these does not affect the original data frame
        folds[0].drop(folds[0].index, inplace=True)
        folds[1].drop(folds[1].index, inplace=True)

        return prediction

    @staticmethod
    def splitInFolds(data_frame):
        data_frame["THU"] = 1  # Add dummy
        folds = [data_frame.query("abs(evt % 2) != 0 ").reset_index(drop=True),
                 data_frame.query("abs(evt % 2) == 0 ").reset_index(drop=True)]
        return folds

    def applyScaler(self, scaler, folds, variables):
        if not scaler or scaler == 0 or scaler == None:
            return copy.deepcopy(folds)
        newFolds = copy.deepcopy(folds)
        for i, fold in enumerate(newFolds):
            logger.debug("Length of folds: " + str(len(fold[variables])))
            if len(fold[variables]) > 0:
                fold[variables] = scaler[i].transform(fold[variables])
        return newFolds


    def modifyDFForPrediction(self, DF):
        DF["evt"] = DF["evt"].astype('int64')
        # DF.eval("event_weight = " + sample_info["event_weight"], inplace=True)
        # DF["target"] = sample_info["target"]
        # DF["train_weight"] = DF["event_weight"].abs() * self.config["class_weight"].get(sample_info["target_name"], 1.0 )

        # class_weight = sample_info["class_weight"]

        # DF["train_weight"] = DF["event_weight"].abs() * class_weight
        # DF["train_weight"] = DF["event_weight"].abs()
        # DF.replace(-999., -10, inplace=True)

        # for new, old in sample_info["rename"]:
        #     if new in DF.columns.values.tolist() and old in DF.columns.values.tolist():
        #         DF[old] = DF[new]
            # else:
            #     print "cant rename {0} to {1}".format(old, new)

        if self.settings.era == "2016":
            DF.replace({"jdeta": -10.}, -1., inplace=True)
            DF.replace({"mjj": -10.}, -11., inplace=True)
            DF.replace({"dijetpt": -10.}, -11., inplace=True)

            DF.eval("jdeta =   (njets < 2) *-1  + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-11 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-11 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)

        if self.settings.era == "2017":
            DF.replace({"jdeta": -1.}, -10., inplace=True)
            DF.replace({"mjj": -11.}, -10., inplace=True)
            DF.replace({"dijetpt": -11.}, -10., inplace=True)

            DF.eval("jdeta =   (njets < 2) *-10 + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-10 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-10 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)



