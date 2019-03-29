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

    def handle(self, data_frame, sample_info, first):
        print "Handling data for prediction..."
        self._handle_prediction_data(data_frame, sample_info, first)

    def _handle_prediction_data(self, data_frame, sample_info, first):
        #do something here (similar to what sandbox in run_model does)

        path = "NOMINAL_ntuple_" + sample_info["histname"].split("_")[0]
        self.sandbox(self.settings.channel, self.model, self.scaler, data_frame, self.config_parser.variable_names, path, self.file_manager.get_prediction_dirpath(), first, sample_info )
        pass

    def sandbox(self, channel, model, scaler, data_frame, variables, outname, outpath, first, config=None ):
        # needed because of memory management
        # iterate over chunks of sample and do splitting on the fly

            #self.modifyDF(data_frame, config)

            data_frame["THU"] = 1  # Add dummy
            # Carefull!! Check if splitting is done the same for training. This is the KIT splitting
            folds = [data_frame.query("abs(evt % 2) != 0 ").reset_index(drop=True),
                     data_frame.query("abs(evt % 2) == 0 ").reset_index(drop=True)]
            self.addPrediction(channel, model.predict(self.applyScaler(scaler, folds, variables)), folds, outname, outpath,
                          new=first)

            folds[0].drop(folds[0].index, inplace=True)
            folds[1].drop(folds[1].index, inplace=True)
            data_frame.drop(data_frame.index, inplace=True)

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

    def modifyDF(self, DF, sample_info):

        DF["evt"] = DF["evt"].astype('int64')
        DF.eval( "event_weight = " + sample_info["event_weight"], inplace = True  )
        DF["target"] = sample_info["target"]
        #DF["train_weight"] = DF["event_weight"].abs() * self.config["class_weight"].get(sample_info["target_name"], 1.0 )

        class_weight = sample_info["class_weight"]

        DF["train_weight"] = DF["event_weight"].abs() * class_weight
        DF.replace(-999.,-10, inplace = True)

        for new, old in sample_info["rename"]:
            if new in DF.columns.values.tolist() and old in DF.columns.values.tolist():
                DF[old] = DF[new]
            # else:
            #     print "cant rename {0} to {1}".format(old, new)

        if self.settings.era == "2016":
            DF.replace({"jdeta":-10.},-1., inplace = True)
            DF.replace({"mjj":-10.},-11., inplace = True)
            DF.replace({"dijetpt":-10.},-11., inplace = True)

            DF.eval("jdeta =   (njets < 2) *-1  + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-11 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-11 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)


        if self.settings.era == "2017":
            DF.replace({"jdeta":-1.},-10., inplace = True)
            DF.replace({"mjj":-11.},-10., inplace = True)
            DF.replace({"dijetpt":-11.},-10., inplace = True)

            DF.eval("jdeta =   (njets < 2) *-10 + (njets > 1 )*jdeta ", inplace=True)
            DF.eval("mjj =     (njets < 2) *-10 + (njets > 1 )*mjj ", inplace=True)
            DF.eval("dijetpt = (njets < 2) *-10 + (njets > 1 )*dijetpt ", inplace=True)
            DF.eval("jpt_1 =   (njets == 0)*-10 + (njets > 0 )*jpt_1 ", inplace=True)
            DF.eval("jpt_2 =   (njets < 2 )*-10 + (njets > 1 )*jpt_2 ", inplace=True)


