import os
import sys
import argparse
from FileManager import FileManager, ModelFileManager, PredictionFileManager, FractionPlotFileManager
from ConfigParser import ConfigParser
from Settings import Settings
from Logger import TrainingLogger, PredictionLogger, FractionPlotLogger
import tempfile
import json
import shutil
import time

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
    parser.add_argument('-m', dest='model',   help='ML model to use', choices=['keras', 'xgb'],  default='keras')
    parser.add_argument('-t', dest='train',   help='Train new model', action='store_true')
    parser.add_argument('-s', dest='scaler',   help='Global data scaler', choices=['none', 'standard'], default='none')
    parser.add_argument('-p', dest='predict', help='Make prediction', action='store_true')
    parser.add_argument('-f', dest='fractions', help='Plot Fractions', action='store_true')
    parser.add_argument('-tf', dest='trainingFracplots', help='Plot Fractions for training samples', action='store_true')
    parser.add_argument('-cf', dest='classificationFracplots', help='Plot Fractions after classification', action='store_true')
    parser.add_argument('-ctf', dest='classificationTrainingFracplots', help='Plot training Fractions after classification', action='store_true')
    parser.add_argument('-d', dest='datacard', help='Datacard', action='store_true')
    parser.add_argument('-e', dest='era',  help='Era', choices=["2016", "2017"], required = True)
    parser.add_argument('bin_vars', nargs="*", help='Bin variable for fraction plots or datacard', default=[])
    parser.add_argument('-name', dest='name',   help='Global data scaler', default='none')
    parser.add_argument('-varset', dest='varset',   help='Global data scaler', default='none')
    parser.add_argument('-emb', dest='emb',   help='Global data scaler', action='store_true')
    args = parser.parse_args()
    
    # parser.add_argument('var', nargs="+", help='Variable')

    print "---------------------------"
    print "Era: ", args.era
    print "Running over {0} samples".format(args.channel)
    print "---------------------------"
    
    print args.bin_vars
    
    if not args.bin_vars:
        args.bin_vars = ["pt_1", "pt_2", "jpt_1", "jpt_2", "bpt_1", "bpt_2", "njets", "nbtag",  "m_sv", "mt_1",
                        "mt_2", "pt_vis", "pt_tt", "mjj", "jdeta", "m_vis", "dijetpt", "met", "eta_1", "eta_2"]
        
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
    classificationFracplots = args.classificationFracplots
    classificationTrainingFracplots = args.classificationTrainingFracplots
    datacard = args.datacard
    bin_vars = args.bin_vars

    if args.emb:
        embstr = "_emb"
    else:
        embstr = ""

    path_config_path = "conf/path_config.json"
    temp_path = "conf/path_config_{0}_{1}{2}_{3}".format(args.name, args.varset, embstr, str(int(time.time())))

    try:
        shutil.copyfile(path_config_path,temp_path)
        print 'temp file:',temp_path
    except ValueError as e:
        print e
        sys.exit(-1)
    
    #file_manager = FileManager("conf/path_config.json")
    file_manager = FileManager(temp_path) 
    
    settings = Settings(channel, era, model, scaler)    

    settings.varset = args.varset
    settings.emb = args.emb
    settings.name = args.name

    config = file_manager.get_sample_config_path().format(channel, era, settings.varset, settings.get_emb_prefix())

    print "Sample config path: " + config

    parser = ConfigParser(channel, era, config)

    settings.config_parser = parser

    if train:

        from Training import Training

        model_file_manager = ModelFileManager(temp_path, settings)
        settings.model_file_manager = model_file_manager

        sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        sample_sets = [sset for sset in sample_sets if (not "AR" in sset.name)]
        print "Filtered sample sets for training: \n"
        for ss in sample_sets:
            print ss

        settings.filtered_samples = sample_sets

        # logger = TrainingLogger(settings)
        # print "attempt logging"
        # logger.log()

        training = Training(settings)
        training.train()

    if predict:

        from Prediction import Prediction
        from PredictionHelper import PredictionHelper

        prediction_file_manager = PredictionFileManager(temp_path, settings)
        settings.prediction_file_manager = prediction_file_manager

        sample_sets = [sset for sset in parser.sample_sets if "_full" in sset.name]
        print "Filtered sample sets for prediction: \n"
        for ss in sample_sets:
            print ss

        settings.filtered_samples = sample_sets

        # logger = PredictionLogger(settings)
        # print "attempt logging"
        # logger.log()

        # prediction = Prediction(settings)
        # prediction.predict()

        prediction_helper = PredictionHelper(settings)
        prediction_helper.predict()

    if fractions or trainingFracplots or classificationFracplots or classificationTrainingFracplots:

        from FractionPlotter import FractionPlotter

        frac_plot_file_manager = FractionPlotFileManager(temp_path, settings)
        settings.fraction_plot_file_manager = frac_plot_file_manager

        plotter = FractionPlotter(settings)

        train_sample_sets = [sset for sset in parser.sample_sets if (not "_full" in sset.name)]
        train_sample_sets = [sset for sset in train_sample_sets if (not "AR" in sset.name)]

        if trainingFracplots or classificationTrainingFracplots:
            train_sample_sets = [sset for sset in train_sample_sets if (not "EMB" in sset.name)]

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

        if fractions:
            for variable in bin_vars:
                plotter.make_fraction_plots(ar_sample_sets, variable, "AR", outdirpath)

        if trainingFracplots:
            trainOutpath = outdirpath.replace("AR", "train")
            FileManager.create_dir(trainOutpath)
                        
            for variable in bin_vars:
                plotter.make_fraction_plots(train_sample_sets, variable, "train", trainOutpath, True)

        if classificationFracplots:
            trainOutpath = outdirpath.replace("AR", "AR_classification")
            FileManager.create_dir(trainOutpath)
            
            for variable in bin_vars:
                plotter.make_classification_plots(ar_sample_sets, variable, "AR_class", trainOutpath)

        if classificationTrainingFracplots:
            trainOutpath = outdirpath.replace("AR", "train_classification")
            FileManager.create_dir(trainOutpath)
            
            for variable in bin_vars:
                plotter.make_classification_plots(train_sample_sets, variable, "train_class", trainOutpath, True)


if __name__ == '__main__':
    main()
