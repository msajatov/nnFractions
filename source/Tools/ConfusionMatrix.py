import os
import ROOT as R
import numpy as np
import matplotlib.pyplot as plt
import argparse

import root_numpy as rn
import root_pandas as rp
from FileManager import FileManager
from Settings import Settings
from ConfigParser import ConfigParser
from TargetCategory import TargetCategory
from SampleSet import SampleSet
from pandas import DataFrame, concat
from PathObject import makeDir
import copy

def main(): 

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--model',   help='ML model to use' ,choices = ['keras','xgb'],  default = 'keras')
    parser.add_argument('-c', '--channel', help='Decay channel' ,choices = ['mt','et','tt'], default = 'mt')
    args = parser.parse_args()

    channel = args.channel
    model = args.model

    # create confusion

    confusion = get_confusion()


    
    print "Writing confusion matrices to plots/confusion"
    plot_confusion(confusion,classes,"plots/confusion/{0}_{1}_confusion.png".format(model,channel), "std")

    conf_eff1, conf_eff2 = get_efficiency_representations(confusion)
    plot_confusion(conf_eff1, classes, "plots/confusion/{0}_{1}_confusion_eff1.png".format(model,channel))
    plot_confusion(conf_eff2, classes, "plots/confusion/{0}_{1}_confusion_eff2.png".format(model,channel), "eff")

    conf_pur1, conf_pur2 = get_purity_representations(confusion)
    plot_confusion(conf_pur1, classes, "plots/confusion/{0}_{1}_confusion_pur1.png".format(model,channel))
    plot_confusion(conf_pur2, classes, "plots/confusion/{0}_{1}_confusion_pur2.png".format(model,channel), "pur")


def make_confusion_plots(settings, sample_sets):
    confusion = get_confusion(settings)


    
    print "Writing confusion matrices to plots/confusion"
    plot_confusion(confusion,classes,"plots/confusion/{0}_{1}_confusion.png".format(model,channel), "std")

    conf_eff1, conf_eff2 = get_efficiency_representations(confusion)
    plot_confusion(conf_eff1, classes, "plots/confusion/{0}_{1}_confusion_eff1.png".format(model,channel))
    plot_confusion(conf_eff2, classes, "plots/confusion/{0}_{1}_confusion_eff2.png".format(model,channel), "eff")

    conf_pur1, conf_pur2 = get_purity_representations(confusion)
    plot_confusion(conf_pur1, classes, "plots/confusion/{0}_{1}_confusion_pur1.png".format(model,channel))
    plot_confusion(conf_pur2, classes, "plots/confusion/{0}_{1}_confusion_pur2.png".format(model,channel), "pur")

def get_confusion(settings, sample_sets):

    confusion =  np.zeros( (len(classes),len(classes)) )

    file_manager = settings.fraction_plot_file_manager

    dict = {}

    # TODO implement this

    for sample_set in sample_sets:
        events = get_events_for_sample_set(file_manager, sample_set, branches)

def get_events_for_sample_set(file_manager, sample_set, branches):
        root_path = file_manager.get_dir_path("prediction_input_dir")
        sample_path = "{0}/{1}".format(root_path, sample_set.source_file_name)
        sample_path = sample_path.replace("WJets", "W")
        select = sample_set.cut

        events = rp.read_root(paths=sample_path, where=select,
                              columns=branches)
        return events

def plot_confusion(confusion, classes, filename, form="arb", markup='{:.2f}'):
    plt.figure(figsize=(1.5 * confusion.shape[0], 1.0 * confusion.shape[1]))
    axis = plt.gca()
    for i in range(confusion.shape[0]):
        for j in range(confusion.shape[1]):
            axis.text(
                i + 0.5,
                j + 0.5,
                markup.format(confusion[-1 - j, i]),
                ha='center',
                va='center')
    q = plt.pcolormesh(confusion[::-1], cmap='Wistia')
    cbar = plt.colorbar(q)
    if form == "std":
        cbar.set_label("Sum of event weights", rotation=270, labelpad=50)
    elif form == "eff":
        cbar.set_label("Efficiency", rotation=270, labelpad=50)
    elif form == "pur":
        cbar.set_label("Purity", rotation=270, labelpad=50)
    else:
        cbar.set_label("Arbitrary units", rotation=270, labelpad=50)
    plt.xticks(
        np.array(range(len(classes))) + 0.5, classes, rotation='vertical')
    plt.yticks(
        np.array(range(len(classes))) + 0.5,
        classes[::-1],
        rotation='horizontal')
    plt.xlim(0, len(classes))
    plt.ylim(0, len(classes))
    plt.ylabel('True class')
    plt.xlabel('Predicted class')
    plt.savefig(filename, bbox_inches='tight')


def get_efficiency_representations(m):
    ma = np.zeros(m.shape)
    mb = np.zeros(m.shape)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ma[i, j] = m[i, j] / m[i, i]
            mb[i, j] = m[i, j] / np.sum(m[i, :])
    return ma, mb


def get_purity_representations(m):
    ma = np.zeros(m.shape)
    mb = np.zeros(m.shape)
    for i in range(m.shape[0]):
        for j in range(m.shape[1]):
            ma[i, j] = m[i, j] / m[j, j]
            mb[i, j] = m[i, j] / np.sum(m[:, j])
    return ma, mb


if __name__ == '__main__':
    main()