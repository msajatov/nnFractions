from Reader import Reader
import copy
import pandas
import os
from glob import glob
import argparse
import cPickle
import keras
from FileManager import FileManager, ModelFileManager, PredictionFileManager, FractionPlotFileManager
from DataController import DataController
from DataReader import DataReader
from ConfigParser import ConfigParser
from TrainingDataHandler import TrainingDataHandler
from PredictionDataHandler import PredictionDataHandler
from Settings import Settings
from FractionPlotter import FractionPlotter
from Logger import TrainingLogger, PredictionLogger, FractionPlotLogger
from Prediction import Prediction
from Training import Training

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
    parser.add_argument('-m', dest='model',   help='ML model to use', choices=['keras', 'xgb'],  default='keras')
    parser.add_argument('-t', dest='train',   help='Train new model', action='store_true')
    parser.add_argument('-s', dest='shapes',   help='Predict shapes', action='store_true')
    parser.add_argument('-p', dest='predict', help='Make prediction', action='store_true')
    parser.add_argument('-f', dest='fractions', help='Plot Fractions', action='store_true')
    parser.add_argument('-d', dest='datacard', help='Datacard', action='store_true')
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

    run(channel=args.channel,
        era=args.era,
        use=args.model,
        train=args.train,
        shapes=args.shapes,
        predict=args.predict,
        fractions=args.fractions,
        datacard=args.datacard,
        add_nominal=args.add_nom
        )


def run(channel, era, use, train=False, shapes=False, predict=False, fractions=False, datacard=False, add_nominal=False):

    file_manager = FileManager("conf/path_config.json")

    config = file_manager.get_sample_config_path().format(channel, era)
    settings = Settings(use, channel, era)

    if train:

        model_file_manager = ModelFileManager("conf/path_config.json")
        set_up_model_file_manager(model_file_manager, settings)

        parser = ConfigParser(channel, era, config)
        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        sample_sets = [sset for sset in sample_sets if (not "AR" in sset.name)]
        print "Filtered sample sets for training: \n"
        for ss in sample_sets:
            print ss

        logger = TrainingLogger(settings, model_file_manager, sample_sets, parser)
        print "attempt logging"
        logger.log()

        training = Training(settings, model_file_manager, parser, sample_sets)
        training.train()

    if predict:

        prediction_file_manager = PredictionFileManager("conf/path_config.json")
        set_up_prediction_file_manager(prediction_file_manager, settings)

        parser = ConfigParser(channel, era, config)
        sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
        print "Filtered sample sets for prediction: \n"
        for ss in sample_sets:
            print ss

        logger = PredictionLogger(settings, prediction_file_manager, sample_sets, parser)
        print "attempt logging"
        logger.log()

        prediction = Prediction(settings, prediction_file_manager, parser, sample_sets)
        prediction.predict()

    if fractions:

        frac_plot_file_manager = FractionPlotFileManager("conf/path_config.json")
        set_up_fraction_plot_file_manager(frac_plot_file_manager, settings)

        bin_var = "m_vis"

        parser = ConfigParser(channel, era, config)
        plotter = FractionPlotter(settings, frac_plot_file_manager, parser)

        train_sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        train_sample_sets = [sset for sset in train_sample_sets if (not "AR" in sset.name)]

        ar_sample_sets = [sset for sset in parser.sample_sets if "data_AR" in sset.name]

        complete_sample_sets = []
        complete_sample_sets += train_sample_sets
        complete_sample_sets += ar_sample_sets

        print "Filtered sample sets for AR frac plots: \n"
        for ss in complete_sample_sets:
            print ss
            print "count: "
            print plotter.get_event_count_for_sample_set(ss)

        outdirpath = frac_plot_file_manager.get_dir_path("fracplot_output_dir")

        logger = FractionPlotLogger(settings, frac_plot_file_manager, complete_sample_sets, parser)

        # tn = {0:"tt", 1:"w", 2:"qcd"}
        # plotter.set_target_names(tn)
        # logger.set_target_names(tn)

        print "attempt logging"
        logger.log()

        plotter.make_fraction_plots(ar_sample_sets, bin_var, "AR", outdirpath)
        plotter.make_fraction_plots(train_sample_sets, bin_var, "train", outdirpath)

    if datacard and "hephy.at" in os.environ["HOME"]:
        from Tools.Datacard.produce import Datacard, makePlot
        from Tools.CutObject.CutObject import Cut
        from Tools.FakeFactor.FakeFactor import FakeFactor

        Datacard.use_config = era + "/datacard_conf"
        D = Datacard(channel=channel,
                     variable="predicted_prob",
                     era=era,
                     real_est="mc",
                     add_systematics = shapes,
                     debug=True,
                     use_cutfile = "conf/cuts_{0}.json".format(era))

        FakeFactor.fractions = "{0}/datacard_conf/fractions/htt_ff_fractions_{0}.root".format(era)

        D.create(era+"/"+use)
        makePlot(channel, "ML", era+"/"+use, era, era+"/plots")


def set_up_model_file_manager(model_file_manager, settings):
    era = settings.era
    use = settings.ml_type
    channel = settings.channel

    model_dir = model_file_manager.get_dir_name("model_output_dir")
    model_dir = model_dir + "/" + era
    model_name = "{0}.{1}".format(channel, use)

    model_file_manager.set_dir_name("model_output_dir", model_dir)
    model_file_manager.set_dir_name("scaler_output_dir", model_dir)
    model_file_manager.set_model_filename(model_name)

    model_file_manager.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))


def set_up_prediction_file_manager(prediction_file_manager, settings):
    era = settings.era
    use = settings.ml_type
    channel = settings.channel

    model_dir = prediction_file_manager.get_dir_name("model_input_dir")
    model_dir = model_dir + "/" + era
    model_name = "{0}.{1}".format(channel, use)

    prediction_file_manager.set_dir_name("model_input_dir", model_dir)
    prediction_file_manager.set_dir_name("scaler_input_dir", model_dir)
    prediction_file_manager.set_model_filename(model_name)

    prediction_dir = prediction_file_manager.get_dir_name("prediction_output_dir")
    prediction_dir = prediction_dir + "/" + era
    prediction_file_manager.set_dir_name("prediction_output_dir", prediction_dir)

    prediction_file_manager.set_scaler_filename("StandardScaler.{0}.pkl".format(channel))


def set_up_fraction_plot_file_manager(frac_plot_file_manager, settings):
    era = settings.era
    use = settings.ml_type
    channel = settings.channel

    prediction_dir = frac_plot_file_manager.get_dir_name("prediction_input_dir")
    prediction_dir = prediction_dir + "/" + era
    frac_plot_file_manager.set_dir_name("prediction_input_dir", prediction_dir)

    plot_dir = frac_plot_file_manager.get_dir_name("fracplot_output_dir")
    plot_dir = "{0}/{1}".format(plot_dir, era)
    frac_plot_file_manager.set_dir_name("fracplot_output_dir", plot_dir)


if __name__ == '__main__':
    main()
