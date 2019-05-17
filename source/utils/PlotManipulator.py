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

    channels = ["et", "mt", "tt"]

    for channel in channels:
        print channel
        controlPath = "{0}/1__{1}_fractions.root".format(controlRootPath, channel)
        fracPath = "{0}/{1}_AR_frac_data_AR_m_vis_norm.root".format(fracRootPath, channel)
        if norm:
            pm = PlotManipulator(channel)
            controlPlot = loadControlPlotCanvas(controlPath)
            normalized = pm.normalize(controlPlot)
            # save

        if overlay:
            pm = PlotManipulator(channel)
            if norm:
                controlPlot = loadControlPlotCanvas(controlPath)
                controlPlot = pm.normalize(controlPlot)
            else:
                controlPlot = loadControlPlotCanvas(controlPath)

            controlPlotHists = getControlPlotHists(controlPlot)
            transparentControlPlotHists = pm.makeTransparent(controlPlotHists)


            fracPlot = loadFracPlotCanvas(fracPath)
            fracPlotHists = getFracPlotHists(fracPlot)
            pm.createOverlay(fracPlotHists, transparentControlPlotHists, fracPlot, controlPlot)


def loadControlPlotCanvas(path):
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

def getControlPlotHists(canvas):
    stack = canvas.GetPrimitive("stack")
    hists = list(stack.GetHists())
    return hists

def getFracPlotHists(canvas):
    pad = canvas.GetPrimitive("cv_1")
    stack = pad.GetPrimitive("stack")
    hists = list(stack.GetHists())
    return hists

def loadFracPlotCanvas(path):
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

def loadPlot(path):
    pass


class PlotManipulator:

    def __init__(self, channel):
        self.channel = channel
        pass

    def cpHist(self, h, name,title="", reset = True):
        newHist = copy.deepcopy(h)
        if reset: newHist.Reset()
        newHist.SetName(name)
        if title:
            newHist.SetTitle(title)
        else:
            newHist.SetTitle(name)

        return newHist

    def createOverlay(self, histos1, histos2, canvas1, canvas2):
        # pad = canvas1.GetPrimitive("cv_1")
        # stack = pad.GetPrimitive("stack")

        fracstack = R.THStack("fracstack", "")

        for histo in histos1:
            print "frac plot histos:"
            print histo
            histo.SetFillColorAlpha(0, 0)
            #histo.SetFillStyle(4000)
            histo.SetLineColor(R.kBlack)
            #applyHistStyle(histo, histo.GetName())
            fracstack.Add(histo)

        # controlstack = R.THStack("controlstack", "")
        #
        # for histo in histos2:
        #     print "transparent control plot histos:"
        #     print histo
        #     #histo.SetFillColorAlpha(0, 0)
        #     #histo.SetFillStyle(4000)
        #     #histo.SetLineColor(R.kBlack)
        #     histo.ResetAttFill()
        #     histo.SetLineColor(R.kRed)
        #     controlstack.Add(copy.deepcopy(histo))

        individual_control_hists = []

        for histo in histos2:
            applySignalHistStyle(histo, histo.GetName(), 3)
            individual_control_hists.append(copy.deepcopy(histo))



        #canvas1.Draw()
        #canvas1.cd()
        cv = R.TCanvas("cv", "cv", 10, 10, 700, 600)
        cv.cd()

        pad1 = R.TPad("pad1", "", 0, 0, 1, 1)
        pad1.SetFillStyle(4000)
        pad2 = R.TPad("pad2", "", 0, 0, 1, 1)
        pad2.SetFillStyle(4000)

        pad1.Draw()
        pad1.cd()

        # fracstack.Draw()
        # controlstack.Draw()
        #fracstack.Draw()

        cv.Update()

        #pad2.Draw()
        #pad2.cd()

        #controlstack.Draw()
        # fracstack.Draw()
        # controlstack.Draw()

        controlstack2 = R.THStack("controlstack2", "")

        for hist in individual_control_hists:
            controlstack2.Add(hist)
            #hist.Draw("same")

        controlstack2.Draw()
        #controlstack2.Draw("same hist")
        #stack.Draw("same")
        fracstack.Draw("same")


        cv.Update()

        #canvas1.Draw()
        #
        # #newcanvas = R.TCanvas()
        #
        # #newcanvas.cd()
        # #newcanvas.Draw()
        # #controlstack.Draw("SAME")
        #

        raw_input("Press Enter to continue...")
        cv.SaveAs("{0}-fractions_test.ps".format(self.channel))
        cv.SaveAs("{0}-fractions_test.png".format(self.channel))

    def createSimpleCanvas(self, name):

        cv = R.TCanvas(name, name, 10, 10, 800, 600)
        cv.Divide(1, 1, 0.0, 0.0)

        # Set Pad sizes
        cv.GetPad(1).SetPad(0.0, 0.0, 1.0, 1.0)
        cv.GetPad(1).SetFillStyle(4000)

        # Set pad margins 1
        cv.cd(1)
        R.gPad.SetTopMargin(0.08)
        R.gPad.SetBottomMargin(0.08)
        R.gPad.SetLeftMargin(0.08)
        R.gPad.SetRightMargin(0.2)
        return cv


    def makeTransparent(self, hists):
        for hist in hists:
            hist.SetFillColor(0)
        return hists


    def changeFill(self, histo, color):
        pass

    def normalize(self, histos):
        pass


def applyHistStyle(hist, name):
    # print "Applying hist style:"
    hist.GetXaxis().SetLabelFont(63)
    hist.GetXaxis().SetLabelSize(14)
    hist.GetYaxis().SetLabelFont(63)
    hist.GetYaxis().SetLabelSize(14)
    hist.SetFillColor( getColor( name ) )
    hist.SetLineColor( R.kBlack )

def applySignalHistStyle(hist, name, width = 1):
    # print "Applying signal hist style:"
    hist.GetXaxis().SetLabelFont(63)
    hist.GetXaxis().SetLabelSize(14)
    hist.GetYaxis().SetLabelFont(63)
    hist.GetYaxis().SetLabelSize(14)
    hist.SetFillColor( 0 )
    hist.SetLineWidth( width )
    hist.SetLineColor( getColor( name ) )


def getFancyName(name):
    if name == "ZL":                return r"Z (l#rightarrow#tau)"
    if name == "ZJ":                return r"Z (jet#rightarrow#tau)"
    if name == "ZTT":               return r"Z #rightarrow #tau#tau"
    if name == "TTT":               return r"t#bar{t} (#tau#rightarrow#tau)"
    if name == "TTJ":               return r"t#bar{t} (jet#rightarrow#tau)"
    if name == "VVT":               return r"VV (#tau#rightarrow#tau)"
    if name == "VVJ":               return r"VV (jet#rightarrow#tau)"
    if name == "W":                 return r"W + jet"
    if name == "QCD":               return r"MultiJet"
    if name == "jetFakes":          return r"jet #rightarrow #tau_{h}"
    if name == "jetFakes_W":        return r"W + jet ( F_{F} )"
    if name == "jetFakes_TT":       return r"t#bar{t} ( F_{F} )"
    if name == "jetFakes_QCD":      return r"MultiJet ( F_{F} )"
    if name == "EWKZ":              return r"EWKZ"
    if name in ["qqH","qqH125"]:    return "VBF"
    if name in ["ggH","ggH125"]:    return "ggF"

    return name



def getColor(name):
    print "Name in getColor is:"
    print name
    if name in ["TT","TTT","TTJ","jetFakes_TT", "tt", "TTT_anti", "TTJ_anti", "TTL_anti", "ttx"]:    return R.TColor.GetColor(155,152,204)
    if name in ["sig"]:                             return R.kRed
    if name in ["bkg"]:                             return R.kBlue
    if name in ["qqH","qqH125"]:                    return R.TColor.GetColor(0,100,0)
    if name in ["ggH","ggH125"]:                    return R.TColor.GetColor(0,0,100)
    if name in ["W","jetFakes_W", "w", "W_anti", "wx"]:                  return R.TColor.GetColor(222,90,106)
    if name in ["VV","VVJ","VVT", "VVJ_anti", "VVT_anti", "VVL_anti"]:                  return R.TColor.GetColor(175,35,80)
    if name in ["ZL","ZJ","ZLJ", "ZL_anti", "ZJ_anti"]:                   return R.TColor.GetColor(100,192,232)
    if name in ["EWKZ"]:                            return R.TColor.GetColor(8,247,183)
    if name in ["QCD","WSS","jetFakes_QCD", "qcd", "QCD_estimate", "qcdx"]:        return R.TColor.GetColor(250,202,255)
    if name in ["ZTT","DY","real", "ZTT_anti", "EMB_anti", "realx"]:                 return R.TColor.GetColor(248,206,104)
    if name in ["jetFakes"]:                        return R.TColor.GetColor(192,232,100)
    if name in ["data"]:                            return R.TColor.GetColor(0,0,0)
    else: return R.kYellow

if __name__ == '__main__':
    main()