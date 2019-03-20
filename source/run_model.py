from Reader import Reader
import copy
import pandas
import os
from glob import glob
import argparse
import cPickle
import keras
from FileManager import FileManager

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
    parser.add_argument('-m', dest='model',   help='ML model to use', choices=['keras', 'xgb'],  default='keras')
    parser.add_argument('-t', dest='train',   help='Train new model', action='store_true')
    parser.add_argument('-s', dest='shapes',   help='Predict shapes', action='store_true')
    parser.add_argument('-p', dest='predict', help='Make prediction', action='store_true')
    parser.add_argument('-e', dest='era',  help='Era', choices=["2016", "2017"], required = True)
    parser.add_argument('--add_nominal', dest='add_nom', help='Add nominal samples to prediction', action='store_true')
    args = parser.parse_args()

    print "---------------------------"
    print "Era: ", args.era
    print "Running over {0} samples".format(args.channel)
    print "Using {0}".format(args.model), keras.__version__
    if args.train:
        print "Training new model"
    if not args.shapes:
        print "Not predicting shape templates."
    print "---------------------------"
        
    run(samples = "conf/frac_config_{0}_{1}.json".format(args.channel, args.era),
        channel=args.channel,
        era=args.era,
        use=args.model,
        train=args.train,
        shapes=args.shapes,
        predict=args.predict,
        add_nominal=args.add_nom
        )


def run(samples, channel, era, use, train=False, shapes=False, predict=False, add_nominal=False):

    if use == "xgb":
        from XGBModel import XGBObject as modelObject
        parameters = "conf/parameters_xgb.json"

    if use == "keras":
        from KerasModel import KerasObject as modelObject
        parameters = "conf/parameters_keras.json"

    read = Reader(channel = channel,
                  config_file = samples,
                  folds=2,
                  era = era)

    target_names = read.config["target_names"]
    variables = read.config["variables"]

    model_dir = "models_test/" + era
    model_name = "{0}.{1}".format(channel, use)

    file_manager = FileManager("/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output")

    file_manager.set_model_dirname(model_dir)
    file_manager.set_model_filename(model_name)

    scaler = None

    file_manager.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))

    print "debug:" + "\n"
    print file_manager.get_model_dirpath() + "\n"
    print file_manager.get_model_filepath() + "\n"
    print file_manager.get_model_dirname() + "\n"
    print file_manager.get_model_filename() + "\n"

    if train:
        print "Training new model"
        print "Loading Training set"
        trainSet = read.getSamplesForTraining()

        print "Fit Scaler to training set...",
        scaler = trainScaler(trainSet, variables)

        print " done. Dumping for later."

        with open(file_manager.get_scaler_filepath(), 'wb') as FSO:
            cPickle.dump(scaler, FSO , 2)
        scaler = [scaler, scaler] # Hotfix since KIT uses 2 scalers

        trainSet = applyScaler(scaler, trainSet, variables)

        model = modelObject( parameter_file=parameters,
                             variables=variables,
                             target_names=target_names)
        model.train(trainSet)
        model.save(file_manager.get_model_filepath())

    elif predict:
        if os.path.exists(file_manager.get_scaler_filepath()):
            print "Loading Scaler"
            with open(file_manager.get_scaler_filepath(), "rb") as FSO:
                tmp = cPickle.load(FSO)
                scaler = [tmp, tmp]
        else:
            print "Fatal: Scaler file not found at {0}. Train model using -t first.".format(file_manager.get_scaler_filepath())
            return

        print "Loading model and predicting."
        model = modelObject(filename=file_manager.get_model_filepath())
        read.variables = model.variables
        variables = model.variables

    if predict:
        prediction_dir = "predictions_" + era
        file_manager.set_prediction_dirname(prediction_dir)
        outpath = file_manager.get_prediction_dirpath()

        print "Predicting samples"
        if add_nominal:
            print "Predicting Nominal"
            for sample, sampleConfig in read.get(what = "nominal", for_prediction = True):
                sandbox(channel, model, scaler, sample, variables, "nom_" + sampleConfig["histname"], outpath ,sampleConfig, read.modifyDF )


        for sample, sampleConfig in read.get(what = "full", add_jec = shapes, for_prediction = True):
            if "data" in sampleConfig["histname"]:
                sandbox(channel, model, scaler, sample, variables, "NOMINAL_ntuple_Data", outpath, sampleConfig, read.modifyDF)
            elif "full" in sampleConfig["histname"]:
                print "predicting for " + sampleConfig["histname"]
                sandbox(channel, model, scaler, sample, variables,  "NOMINAL_ntuple_" + sampleConfig["histname"].split("_")[0], outpath, sampleConfig, read.modifyDF )
            # else:
            #     splName = sampleConfig["histname"].split("_")
            #     sandbox(channel, model, scaler, sample, variables,  "_".join(splName[1:])+"_ntuple_" + sampleConfig["histname"].split("_")[0], outpath, sampleConfig, read.modifyDF )

        # if shapes:
        #     print "Predicting shapes"
        #     for sample, sampleConfig in read.get(what = "tes", for_prediction = True):
        #         sandbox(channel, model, scaler, sample, variables, sampleConfig["histname"], outpath ,sampleConfig, read.modifyDF )



    # if "hephy.at" in os.environ["HOME"]:
    #     from Tools.Datacard.produce import Datacard, makePlot
    #     from Tools.CutObject.CutObject import Cut
    #     from Tools.FakeFactor.FakeFactor import FakeFactor
    #
    #     datacard_configpath = era + "/datacard_conf"
    #     datacard_outpath = era+"/"+use
    #     datacard_plotpath = era+"/plots"
    #
    #     #file_manager.set_datacard_config_dirname(era + "/datacard_conf")
    #
    #     Datacard.use_config = datacard_configpath
    #
    #     #Datacard.use_config = file_manager.get_datacard_config_dirpath()
    #     #Datacard.use_config = file_manager.get_datacard_config_dirname()
    #     D = Datacard(channel=channel,
    #                  variable="predicted_prob",
    #                  era=era,
    #                  real_est="mc",
    #                  add_systematics = shapes,
    #                  debug=True,
    #                  use_cutfile = "conf/cuts_{0}.json".format(era))
    #
    #     ffpath = "{0}/datacard_conf/fractions/htt_ff_fractions_{0}.root".format(era)
    #     #file_manager.set_fractions_filepath("../output/" + ffpath)
    #
    #     FakeFactor.fractions = ffpath
    #
    #     D.create(file_manager.get_datacard_output_dirname())
    #
    #     datacard_plotpath
    #
    #     makePlot(channel, "ML", datacard_outpath, era, datacard_plotpath)

def sandbox(channel, model, scaler, sample, variables, outname, outpath, config = None, modify = None):
    # needed because of memory management
    # iterate over chunks of sample and do splitting on the fly
    first = True
    for part in sample:
        # This is awful. Try to figure out a better way to add stuff to generator.
        if modify:
            modify(part, config)

        part["THU"] = 1 # Add dummy
        # Carefull!! Check if splitting is done the same for training. This is the KIT splitting
        folds = [part.query( "abs(evt % 2) != 0 " ).reset_index(drop=True), part.query( "abs(evt % 2) == 0 " ).reset_index(drop=True) ]
        addPrediction(channel, model.predict( applyScaler(scaler, folds, variables) ), folds, outname, outpath, new = first )
        
        folds[0].drop(folds[0].index, inplace=True)
        folds[1].drop(folds[1].index, inplace=True)
        part.drop(part.index, inplace=True)

        first = False
    del sample

def addPrediction(channel,prediction, df, sample, outpath, new = True):

    if not os.path.exists(outpath):
        os.mkdir(outpath)

    for i in xrange( len(df) ):
        for c in prediction[i].columns.values.tolist():
            df[i][c] =  prediction[i][c]
            
        if i == 0 and new: mode = "w"
        else: mode = "a"
        # df[i].to_root("{0}/{1}-{2}.root".format("predictions",channel, sample), key="TauCheck", mode = mode)
        df[i].to_root("{0}/{1}-{2}.root".format(outpath,channel, sample), key="TauCheck", mode = mode)
        prediction[i].drop(prediction[i].index, inplace = True)

def trainScaler(folds, variables):
    from sklearn.preprocessing import StandardScaler

    total = pandas.concat( folds, ignore_index = True ).reset_index(drop=True)
    Scaler = StandardScaler()
    Scaler.fit( total[ variables ] )


    return Scaler

def applyScaler(scaler, folds, variables):
    if not scaler: return folds
    newFolds = copy.deepcopy(folds)
    for i,fold in enumerate(newFolds):
        fold[variables] = scaler[i].transform( fold[variables] )
    return newFolds


if __name__ == '__main__':
    main()
