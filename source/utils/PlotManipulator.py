import root_pandas as rp
import ROOT as R
import root_numpy as rn
import copy
import os
from ROOT import TFile
#from math import sqrt
#from array import array
#R.gROOT.SetBatch(True)
#R.gStyle.SetOptStat(0)
#R.TGaxis.SetExponentOffset(-0.05, 0.01, "y")


def main():

    norm = False
    overlay = True

    controlRootPath = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/HephyHiggs/Tools/FakeFactor/plots_mvis_v8/2017"
    fracRootPath = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/fracplots/4cat_bias/real/2017"

    channels = ("et", "mt", "tt")

    for channel in channels:
        controlPath = "{0}/1__{1}_fractions.root".format(controlRootPath, channel)
        fracPath = "{0}/{1}_AR_frac_data_AR_m_vis_norm.root".format(fracRootPath, channel)
        if norm:
            pm = PlotManipulator()
            controlPlot = loadControlPlot(controlPath)
            normalized = pm.normalize(controlPlot)
            # save

        if overlay:
            pm = PlotManipulator()
            if norm:
                controlPlot = loadControlPlot(controlPath)
                controlPlot = pm.normalize(controlPlot)
            else:
                controlPlot = loadControlPlot(controlPath)
            transparentControlPlot = pm.makeTransparent(controlPlot)

            fracPlot = loadFracPlot(fracPath)
            overlay = pm.createOverlay(fracPlot, transparentControlPlot)
            # save

            raw_input("Press Enter to continue...")


def loadControlPlot(path):
    print "loading control plot..."
    file = R.TFile(path, "read")
    cv = file.Get("1cv")
    cv.Draw()

def loadFracPlot(path):
    print "loading frac plot..."
    file = R.TFile(path, "read")
    path = path.replace("4cat_bias/real/2017", "4cat_bias/2017")
    print "cv name: " + path
    cv = file.Get(path)
    cv.Draw()

def loadPlot(path):
    pass


class PlotManipulator:

    def __init__(self):
        pass


    def createOverlay(self, bg_histos, fg_histos):
        pass

    def makeTransparent(self, histo):
        pass

    def changeFill(self, histo, color):
        pass

    def normalize(self, histos):
        pass


if __name__ == '__main__':
    main()