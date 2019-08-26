import os
import argparse
from FileManager import FileManager, ModelFileManager, PredictionFileManager, FractionPlotFileManager
from ConfigParser import ConfigParser
from Settings import Settings
from Logger import TrainingLogger, PredictionLogger, FractionPlotLogger


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
    parser.add_argument('-m', dest='model',   help='ML model to use', choices=['keras', 'xgb'],  default='keras')
    parser.add_argument('-t', dest='train',   help='Train new model', action='store_true')
    parser.add_argument('-s', dest='scaler',   help='Global data scaler', choices=['none', 'standard'], default='none')
    parser.add_argument('-p', dest='predict', help='Make prediction', action='store_true')
    parser.add_argument('-f', dest='fractions', help='Plot Fractions', action='store_true')
    parser.add_argument('-tf', dest='trainingFracplots', help='Plot Fractions for training samples', action='store_true')
    parser.add_argument('-d', dest='datacard', help='Datacard', action='store_true')
    parser.add_argument('-e', dest='era',  help='Era', choices=["2016", "2017"], required = True)
    parser.add_argument('-ext', dest='ext_input', help='Use alternative sample input path for making predictions', action='store_true')
    parser.add_argument('bin_vars', nargs="*", help='Bin variable for fraction plots or datacard', default=[])
    args = parser.parse_args()
    
    # parser.add_argument('var', nargs="+", help='Variable')

    print "---------------------------"
    print "Era: ", args.era
    print "Running over {0} samples".format(args.channel)
    print "---------------------------"
    
    print args.bin_vars
    
    if not args.bin_vars:
        args.bin_vars = [
                        "pt_1",
                        "pt_2",
                        "jpt_1",
                        "jpt_2",
                        "bpt_1",
                        "bpt_2",
                        "njets",
                        "nbtag",
                        "m_sv",
                        "mt_1",
                        "mt_2",
                        "pt_vis",
                        "pt_tt",
                        "mjj",
                        "jdeta",
                        "m_vis",
                        "dijetpt",
                        "met",
                        "eta_1",
                        "eta_2"
                        ]
        
    print args.bin_vars

    run(args)


def run(args):

    channel = args.channel
    era = args.era
    model = args.model
    scaler = args.scaler
    train = args.train
    predict = args.predict
    fractions = args.fractions
    trainingFracplots = args.trainingFracplots
    datacard = args.datacard
    ext_input = args.ext_input
    bin_vars = args.bin_vars

    file_manager = FileManager("conf/path_config.json")

    config = file_manager.get_sample_config_path().format(channel, era)
    parser = ConfigParser(channel, era, config)
    settings = Settings(channel, era, model, scaler)
    settings.config_parser = parser

    if train:

        from Training import Training

        model_file_manager = ModelFileManager("conf/path_config.json", settings)
        settings.model_file_manager = model_file_manager

        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        sample_sets = [sset for sset in sample_sets if (not "AR" in sset.name)]
        print "Filtered sample sets for training: \n"
        for ss in sample_sets:
            print ss

        settings.filtered_samples = sample_sets

        logger = TrainingLogger(settings)
        print "attempt logging"
        logger.log()

        training = Training(settings)
        training.train()

    if predict:

        from Prediction import Prediction
        from PredictionHelper import PredictionHelper

        prediction_file_manager = PredictionFileManager("conf/path_config.json", settings)
        settings.prediction_file_manager = prediction_file_manager

        sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
        print "Filtered sample sets for prediction: \n"
        for ss in sample_sets:
            print ss

        settings.filtered_samples = sample_sets

        # use external predictions (category NN output) as input for frac NN prediction
        if ext_input:
            ext_prediction_input_path = prediction_file_manager.get_dir_path("sample_input_dir")
            parser.data_root_path = ext_prediction_input_path
            settings.ext_input = ext_input

        logger = PredictionLogger(settings)
        print "attempt logging"
        logger.log()

        # prediction = Prediction(settings)
        # prediction.predict()

        prediction_helper = PredictionHelper(settings)
        prediction_helper.predict()

    if fractions:

        from FractionPlotter import FractionPlotter

        frac_plot_file_manager = FractionPlotFileManager("conf/path_config.json", settings)
        settings.fraction_plot_file_manager = frac_plot_file_manager

        plotter = FractionPlotter(settings)

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

        settings.filtered_samples = complete_sample_sets

        outdirpath = frac_plot_file_manager.get_dir_path("fracplot_output_dir")

        #logger = FractionPlotLogger(settings)

        # tn = {0:"tt", 1:"w", 2:"qcd"}
        # plotter.set_target_names(tn)
        # logger.set_target_names(tn)

#         print "attempt logging"
#         logger.log()

        for variable in bin_vars:
            plotter.make_fraction_plots(ar_sample_sets, variable, "AR", outdirpath)
            #plotter.make_fraction_plots(train_sample_sets, variable, "train", outdirpath)
            plotter.make_classification_plots(train_sample_sets, variable, "train", outdirpath)
            
    if trainingFracplots:
        from FractionPlotter import FractionPlotter

        frac_plot_file_manager = FractionPlotFileManager("conf/path_config.json", settings)
        settings.fraction_plot_file_manager = frac_plot_file_manager

        plotter = FractionPlotter(settings)

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

        settings.filtered_samples = complete_sample_sets

        outdirpath = frac_plot_file_manager.get_dir_path("fracplot_output_dir")

        #logger = FractionPlotLogger(settings)

        # tn = {0:"tt", 1:"w", 2:"qcd"}
        # plotter.set_target_names(tn)
        # logger.set_target_names(tn)

#         print "attempt logging"
#         logger.log()

        trainOutpath = outdirpath.replace("AR", "train")
        try:
            if not os.path.exists(trainOutpath):
                os.makedirs(trainOutpath)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        
        for variable in bin_vars:
            plotter.make_fraction_plots(train_sample_sets, variable, "train", trainOutpath)

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

        D.create(era+"/"+model)
        makePlot(channel, "ML", era+"/"+model, era, era+"/plots")


if __name__ == '__main__':
    main()
