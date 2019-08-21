import root_pandas as rp
import ROOT as R
import root_numpy as rn
import copy
import os
from ROOT import TFile
import json

def main():

    controlRootPath = "/afs/hephy.at/work/m/msajatovic/data/storage/fraction_plots/control/2017"
#     fracRootPath = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/fracplots/4cat_vars1/real/2017"
    fracpath = "/afs/hephy.at/work/m/msajatovic/data/storage/nn/fracplots/{0}/AR/2017"

    channels = ["et", "mt", "tt"]
#     channels = ["et"]
    variables = ["pt_1","pt_2","jpt_1","jpt_2","bpt_1","bpt_2","njets","nbtag","m_sv","mt_1",
                "mt_2","pt_vis","pt_tt","mjj","jdeta","m_vis","dijetpt","met","eta_1","eta_2"]
#     variables = ["pt_1","pt_2","jpt_1","jpt_2","bpt_1","bpt_2","njets","nbtag","m_sv","mt_1",
#                 "mt_2","pt_vis","pt_tt","mjj","jdeta","m_vis""dijetpt","met","eta_1","eta_2","iso_1","iso_2"]
#     variables = ["pt_1","pt_2","m_vis"]
    
    metricsCollection = {}
    
    models = ["nn2", "nn3", "nn4", "nn6", "nn7", "nn8", "nn9", "nn11", "nn12", "nn13", "nn14", "nn15", "nn16"]
    for model in models:
        fracRootPath = fracpath.format(model)
        fc = FractionComparer(channels, variables, controlRootPath, fracRootPath)
        modelmetrics = fc.run(model)
        metricsCollection[model] = modelmetrics
    

    print "xy"
    filename = "complete_metrics.json"
    with open(filename, 'wb') as FSO:
        json.dump(metricsCollection, FSO)  
        
        
        

#     for channel in channels:
#         print channel
#         controlPath = "{0}/1_m_vis_{1}_fractions.root".format(controlRootPath, channel)
#         fracPath = "{0}/{1}_AR_frac_data_AR_m_vis_norm.root".format(fracRootPath, channel)
#         
#         controlPlot = loadControlPlotCanvas(controlPath)
#         controlPlotHists = getControlPlotHists(controlPlot)
# 
#         fracPlot = loadFracPlotCanvas(fracPath)
#         fracPlotHists = getFracPlotHists(fracPlot)
#         
#         pm = PlotManipulator(channel)
#         
#         ratios = pm.getRatios(fracPlotHists, controlPlotHists)
#         pm.printBinwise(ratios)
#         
#         diffs = pm.getDifferences(fracPlotHists, controlPlotHists)
#         pm.printBinwise(diffs)
#         
#         fracMetrics = {}
#         
#         for diff in diffs:
#             name = diff.GetName()
#             sum = pm.getSquareErrorSum(diff)
#             fracMetrics[name] = sum
#             
#         print fracMetrics


class FractionComparer:
    def __init__(self, channels, variables, controlRootPath, fracRootPath):
        self.channels = channels
        self.variables = variables
        self.controlRootPath = controlRootPath
        self.fracRootPath = fracRootPath
        
    def run(self, model):
        completeMetrics = {}
        for channel in self.channels:
            completeMetrics[channel] = self.compareChannel(channel)   
            
        print completeMetrics   
        filename = "{0}_metrics.json".format(model)    
        with open(filename, 'wb') as FSO:
            json.dump(completeMetrics, FSO)  
            
        return completeMetrics
            
    def compareChannel(self, channel):
        print channel
        channelMetrics = {}
        for var in self.variables:
            channelMetrics[var] = self.compareVariable(channel, var)
        return channelMetrics
        
    def compareVariable(self, channel, var):
        print var
        controlPath = "{0}/1_{1}_{2}_fractions.root".format(self.controlRootPath, var, channel)
        fracPath = "{0}/{1}_AR_frac_data_AR_{2}_norm.root".format(self.fracRootPath, channel, var)
        
        controlPlot = self.loadControlPlotCanvas(controlPath)
        controlPlotHists = self.getControlPlotHists(controlPlot)

        fracPlot = self.loadFracPlotCanvas(fracPath)
        fracPlotHists = self.getFracPlotHists(fracPlot)
        
        #ratios = self.getRatios(fracPlotHists, controlPlotHists)
        #self.printBinwise(ratios)
        
        diffs = self.getDifferences(fracPlotHists, controlPlotHists)
        #self.printBinwise(diffs)
        
        fracMetrics = {}
        
        for diff in diffs:
            name = diff.GetName()
            sum = self.getSquareErrorSum(diff)
            fracMetrics[name] = sum
            
        print fracMetrics
        return fracMetrics

    def getRatios(self, histos1, histos2):
        if len(histos1) != len(histos2):
            print "Histo lists must have the same length!"
            return
        ratios = []
        
        for i, h1 in enumerate(histos1):
            h1copy =  copy.deepcopy(histos1[i])
            result = h1copy.Divide(histos2[i])
            h1copy.SetName(histos2[i].GetName())
            ratios.append(h1copy)
            
        return ratios
            
    def printBinwise(self, ratios):
        for ratio in ratios:
            print ratio.GetName()
            nbins = ratio.GetNbinsX()
            for ibin in xrange(nbins+1):
                print "Bin {0}:".format(ibin)
                print ratio.GetBinContent(ibin)
                
    def getDifferences(self, histos1, histos2):
        if len(histos1) != len(histos2):
            print "Histo lists must have the same length!"
            return
        diffs = []
        
        for i, h1 in enumerate(histos1):
            h1copy =  copy.deepcopy(histos1[i])
            result = h1copy.Add(histos2[i], -1)
            h1copy.SetName(histos2[i].GetName())
            diffs.append(h1copy)
            
        return diffs
    
    def getSquareErrorSum(self, diffHisto):
        sum = 0
        nbins = diffHisto.GetNbinsX()
        for ibin in xrange(nbins+1):
            content = diffHisto.GetBinContent(ibin)
            sum += content*content
        return sum

    def loadFracPlotCanvas(self, path):
        print "loading frac plot..."
        file = R.TFile(path, "read")
        path = path.replace("4cat_bias/real/2017", "4cat_bias/2017")
    
        cvname = os.path.basename(path)
        cvname = cvname.replace(".root", "")
    
        print "cv name: " + cvname
        cv = file.Get(cvname)
        #cv.Draw()
    
        # cv.cd()
    
        content = cv.ls()
    
        print content
    
        # pad = cv.GetPrimitive("cv_1")
        # stack = pad.GetPrimitive("stack")
        #
        # hists = list(stack.GetHists())
        #
        # for h in hists: print h
    
        return copy.deepcopy(cv)

    def loadControlPlotCanvas(self, path):
        print "loading control plot..."
        file = R.TFile(path, "read")
        cv = file.Get("1cv")
        #cv.Draw()
    
        #cv.cd()
        content = cv.ls()
    
        print content
    
        # stack = cv.GetPrimitive("stack")
        #
        # hists = list(stack.GetHists())
        #
        return copy.deepcopy(cv)

    def getControlPlotHists(self, canvas):
        stack = canvas.GetPrimitive("stack")
        hists = list(stack.GetHists())
        return hists
    
    def getFracPlotHists(self, canvas):
        pad = canvas.GetPrimitive("cv_1")
        stack = pad.GetPrimitive("stack")
        hists = list(stack.GetHists())
        return hists

if __name__ == '__main__':
    main()