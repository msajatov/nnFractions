from Reader import Reader
import copy
import pandas
import os
from glob import glob
import argparse
import cPickle
import keras
from FileManager import FileManager
from DataController import DataController
from DataReader import DataReader
from ConfigParser import ConfigParser
from TrainingDataHandler import TrainingDataHandler
from PredictionDataHandler import PredictionDataHandler
from Settings import Settings
from PlotCreator import PlotCreator

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
    parser.add_argument('-m', dest='model',   help='ML model to use', choices=['keras', 'xgb'],  default='keras')
    parser.add_argument('-t', dest='train',   help='Train new model', action='store_true')
    parser.add_argument('-s', dest='shapes',   help='Predict shapes', action='store_true')
    parser.add_argument('-p', dest='predict', help='Make prediction', action='store_true')
    parser.add_argument('-d', dest='draw', help='Draw', action='store_true')
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
        draw=args.draw,
        add_nominal=args.add_nom
        )


def run(samples, channel, era, use, train=False, shapes=False, predict=False, draw=False, add_nominal=False):

    config = samples

    model_dir = "models_long/" + era
    model_name = "{0}.{1}".format(channel, use)

    file_manager = FileManager("/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output")

    file_manager.set_model_dirname(model_dir)
    file_manager.set_model_filename(model_name)

    prediction_dir = "predictions_fracplot_oldcode_" + era
    file_manager.set_prediction_dirname(prediction_dir)

    file_manager.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))

    print "debug:" + "\n"
    print file_manager.get_model_dirpath() + "\n"
    print file_manager.get_model_filepath() + "\n"
    print file_manager.get_model_dirname() + "\n"
    print file_manager.get_model_filename() + "\n"

    if train:
        parser = ConfigParser(channel, era, config)

        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]

        print "Filtered sample sets for training: "

        for ss in sample_sets:
            print ss

        settings = Settings(use, channel, era)
        training_handler = TrainingDataHandler(settings, file_manager, parser, 0, 0)
        controller = DataController(parser.data_root_path, 2, parser, settings, sample_sets=[])

        sample_info_dicts = controller.prepare(sample_sets)
        training_folds = controller.read_for_training(sample_info_dicts)

        training_handler.handle(training_folds)

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
        if use == "xgb":
            from XGBModel import XGBObject as modelObject

        if use == "keras":
            print "Using keras..."
            from KerasModel import KerasObject as modelObject

        model = modelObject(filename=file_manager.get_model_filepath())

    if predict:
        parser = ConfigParser(channel, era, config)
        sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]

        print "Filtered sample sets for prediction: "

        for ss in sample_sets:
            print ss

        settings = Settings(use, channel, era)
        prediction_handler = PredictionDataHandler(settings, file_manager, parser, model, scaler)
        controller = DataController(parser.data_root_path, 2, parser, settings, sample_sets=[])

        sample_info_dicts = controller.prepare(sample_sets)

        first = True
        for sample_info in sample_info_dicts:
            print "predicting for " + sample_info["histname"]
            # this may be one fold or two folds -> use parameter properly
            iter = controller.read_for_prediction(sample_info)
            for df in iter:
                controller.modifyDF(df, sample_info)
                prediction_handler.handle(df, sample_info, first)
                first = False

    if draw:
        settings = Settings(use, channel, era)
        parser = ConfigParser(channel, era, config)
        plot_creator = PlotCreator(settings, file_manager, parser)

        # sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
        #
        # print "Filtered sample sets for prediction frac plots: "
        #
        # for ss in sample_sets:
        #    print ss
        #
        # outdirpath = file_manager.get_output_root_path() + "/fracplottest/" + channel
        # plot_creator.make_fraction_plots(sample_sets, "m_vis", "full", outdirpath)

        # ---------------------------------------------------------------------------------

        sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]

        print "Filtered sample sets for prediction val plots: "

        for ss in sample_sets:
            print ss

        outdirpath = file_manager.get_output_root_path() + "/fracplottest/" + channel
        plot_creator.make_val_plots(sample_sets, "m_vis", "full", outdirpath)

        # ---------------------------------------------------------------------------------

        # sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        #
        # print "Filtered sample sets for training frac plots: "
        #
        # for ss in sample_sets:
        #    print ss
        #
        # outdirpath = file_manager.get_output_root_path() + "/fracplottest/" + channel
        # plot_creator.make_fraction_plots(sample_sets, "m_vis", "training", outdirpath)

        # ---------------------------------------------------------------------------------

        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]

        print "Filtered sample sets for training val plots: "

        for ss in sample_sets:
            print ss

        outdirpath = file_manager.get_output_root_path() + "/fracplottest/" + channel
        plot_creator.make_val_plots(sample_sets, "m_vis", "training", outdirpath)


if __name__ == '__main__':
    main()
