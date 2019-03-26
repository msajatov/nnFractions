import json
import copy
import os
import argparse
import root_pandas as rp
import root_numpy as rn
import ROOT as R
import multiprocessing as mp
import Tools.Plotting.Plotting as pl
from array import array
import imp
from Tools.CutObject.CutObject import Cut
from Tools.VarObject.VarObject import Var
from Tools.FakeFactor.FakeFactor import FakeFactor
from Tools.Weights.Weights import Weight

R.gROOT.SetBatch(True)
R.gStyle.SetOptStat(0)

def main():
    

    parser = argparse.ArgumentParser()
    parser.add_argument('var', nargs="+", help='Variable')
    parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt','et','tt'], default = 'mt')
    parser.add_argument('-o', dest='out', help='Path to outdir', default="" )
    parser.add_argument('-e', dest='era', help='Era',required = True )
    parser.add_argument('--real_est', dest='real_est', help='define which method to use for real part subtractio', choices = ['mc','frac'], default="mc" )
    parser.add_argument('--syst', dest='syst', help='Add systematics and shape', action="store_true" )
    parser.add_argument('--debug', dest='debug', help='Debug Mode for FFs', action="store_true" )
    parser.add_argument('--plot_only', dest='plot_only', help='Plot datacard', action="store_true")


    args = parser.parse_args()
    Datacard.use_config = "conf" +  args.era

    for u in args.var:
        if not args.plot_only:
            makeDatacard(args.channel, u, args.out, args.era, args.real_est, args.syst, args.debug)

        makePlot(args.channel, u, args.out, args.era)

def makePlot(channel, variable, indir, era, outdir = ""):
    var = Var(variable)

    if "2016" in era: lumi = "35.9"
    if "2017" in era: lumi = "41.5"

    if indir:  root_datacard = "/".join([indir, "htt_{0}.inputs-sm-Run{1}-{2}.root".format(channel, era,var.name) ])
    else:
        root_datacard = "{0}/htt_{1}.inputs-sm-Run{2}-{3}.root".format("_".join([era, "datacards"]), channel, era, var.name)
    file = R.TFile(root_datacard)

    for category in file.GetListOfKeys():
        cat = category.GetName()
        interesting_ones = {}
        for h in ["W","VVT","VVL","VVJ","TTT","TTL","TTJ","ZTT","ZL","ZJ", "QCD",
                 "jetFakes","jetFakes_W","jetFakes_TT","jetFakes_QCD","EMB","data_obs"]:

            if h == "data_obs":
                interesting_ones["data"] = copy.deepcopy( file.Get("{0}/{1}".format(cat,h) ) )
            else:
                interesting_ones[h] = copy.deepcopy( file.Get("{0}/{1}".format(cat,h)  ) )
        

        plots = [ ("_def",["W","VVT","VVL","VVJ","TTT","TTL","TTJ","ZTT","ZL","ZJ","QCD","data"]),
                  ("_def_EMB",["W","VVL","VVJ","TTL","TTJ","EMB","ZL","ZJ","QCD","data"]),
                  ("_ff",["VVT","VVL","TTT","TTL","ZTT","ZL","jetFakes","data"]),
                  ("_ff_split",["VVT","VVL","TTT","TTL","ZTT","ZL","jetFakes_W","jetFakes_TT","jetFakes_QCD","data"]),
                  ("_ff_EMB_split",["VVL","TTL","ZL","EMB","jetFakes_W","jetFakes_TT","jetFakes_QCD","data"]),
                  ("_ff_EMB",["VVL","TTL","EMB","ZL","jetFakes","data"])
        ]
        for p in plots:
            histos = {}
            plot = True
            for h in p[1]:
                if type(interesting_ones[h]) == R.TObject: plot = False
                histos[h] = interesting_ones[h]
            if not outdir:
                outdir = "_".join([era, "plots/"])

            if plot: pl.plot(histos, canvas="semi", signal = [], descriptions = {"plottype": "ProjectWork", "xaxis":var.tex, "channel":channel,"CoM": "13", "lumi":lumi  }, outfile = outdir +"/"+ cat+"_"+var.name + p[0] +".png" )
    file.Close()            

def makeDatacard(channel, variable, outdir,era,real_est, add_systematics, debug):

    print "Producing datacard for:"
    print "channel: ", channel
    print "Var: ", variable
    print "Era: ", era

    D = Datacard(channel, variable, era,real_est, add_systematics, debug)
    D.create(outdir)

class Datacard:

    use_config = real_path = "/".join( os.path.realpath(__file__).split("/")[:-1] + ["conf"] ) 
    def __init__(self, channel, variable, era, real_est, add_systematics=False, debug=False, use_cutfile = ""):

        assert os.path.exists( self.use_config )
        print "path to use_config is: " + self.use_config

        if not use_cutfile:
            Cut.cutfile = "{0}/cuts.json".format(self.use_config)
        else:
            Cut.cutfile = use_cutfile

        FakeFactor.fraction_path = "{0}/fractions".format(self.use_config)
        FakeFactor.fractions = "{0}/fractions/htt_ff_fractions_{1}.root".format(self.use_config, era)
        FakeFactor.ff_config = "{0}/ff_config.json".format(self.use_config)

        self.channel = channel
        self.var = Var(variable, channel)
        self.datacard = {}
        self.add_systematics = add_systematics
        self.debug = debug
        self.queue = mp.Queue()
        self.era = era
        self.real_est = real_est
         
        with open("{0}/samples.json".format(self.use_config),"r") as FSO:
            self.sample_config = json.load(FSO)

        with open("{0}/subprocess.json".format(self.use_config),"r") as FSO:
            self.subprocess_config = json.load(FSO)

        file, pathname, description = imp.find_module("{0}/categories".format(self.use_config))
        categories = imp.load_module("categories", file, pathname, description)
        self.category_config = categories.config

        file, pathname, description = imp.find_module("{0}/weights".format(self.use_config))
        weight = imp.load_module("weights", file, pathname, description)
        self.weight_config = weight.config

        self.template_tree = {}
        self.createTemplateTree()

    def assertChannel(self, entry):
        if not entry: return {}
        if type(entry) == dict:
            return entry[self.channel]
        else:
            return entry

    def createTemplateTree(self):

        for sample in self.sample_config["samples"]:
            self.template_tree[sample] = {}
            self.template_tree[sample]["path"] = "/".join([self.sample_config["path_to_files"], self.sample_config["samples"][sample]["nominal"].format(channel = self.channel) ])
            if self.sample_config["samples"][sample]["type"] == "mc":
                nominal_weight = self.weight_config["template_weight"][self.channel][sample]

                self.template_tree[sample]["categories"] = self.addCategories(sample = sample,
                                                                              nominal_weight = nominal_weight,
                                                                              add_systematics = self.add_systematics  )

            else:
                nominal_weight = Weight("1.0",[])
                self.template_tree[sample]["categories"] = self.addCategories(sample = sample,
                                                                              nominal_weight = nominal_weight, 
                                                                              add_systematics = False)

            if self.add_systematics:
                for shift in ["Up","Down"]:
                    shapes = self.sample_config["samples"][sample]["shape_from_file"]
                    shapes.update( self.assertChannel(self.sample_config["samples"][sample]["channel_shapes"]) )

                    for shape_name, shape in shapes.items():
                        self.template_tree[sample+shape_name+shift] = {}
                        self.template_tree[sample+shape_name+shift]["path"] = self.template_tree[sample]["path"].replace("NOMINAL",shape+shift)
                        self.template_tree[sample+shape_name+shift]["categories"] = self.addCategories(sample = sample,
                                                                                                 nominal_weight = nominal_weight,
                                                                                                 shape_name=shape_name+shift,
                                                                                                 add_systematics = False)

                    for shape_name, shape in self.sample_config["samples"][sample]["shape_from_tree"].items():
                        self.template_tree[sample+shape_name+shift] = {}
                        self.template_tree[sample+shape_name+shift]["path"] = self.template_tree[sample]["path"]
                        self.template_tree[sample+shape_name+shift]["categories"] = self.addCategories(sample = sample,
                                                                                                 nominal_weight = nominal_weight,   # For now.. Make sure that weights do not depend on jets
                                                                                                 shape_name=shape_name+shift,
                                                                                                 shape = shape+shift,
                                                                                                 add_systematics = False)                      


    def addCategories(self, sample, nominal_weight, add_systematics=False, shape_name="", shape = ""):

        categories = {}
        for category in self.category_config["categories"][self.channel]:
            regions = self.category_config["categories"][self.channel][category]
            for region in regions:

                category_name = category + region

                categories[category_name] = {}
                categories[category_name]["category_selection"] =  Cut(cutstring=regions[region],channel=self.channel, jec_shift=shape)
                categories[category_name]["templates"] = { sample: {} }
                categories[category_name]["templates"][sample]["weight"] = [ (sample+shape_name, nominal_weight) ]
                categories[category_name]["templates"][sample]["additional_selection"] = Weight("",[])

                if self.subprocess_config.get(sample, None) != None:
                    for template_name, selection in self.subprocess_config[sample].items():
                        categories[category_name]["templates"][template_name+shape_name] = {}

                        # additional selection used as weight
                        additional_selection = Weight( Cut(cutstring=selection, channel=self.channel, jec_shift=shape).get(), self.subprocess_config["needed"] )
                        categories[category_name]["templates"][template_name+shape_name]["weight"] = [ (template_name+shape_name, nominal_weight + additional_selection) ]



                if add_systematics:

                    for template in categories[category_name]["templates"]:
                        template_weight =  categories[category_name]["templates"][template]["weight"][0][1]
                        for rw in self.weight_config["reweighting"]:

                            if template in self.weight_config["reweighting"][rw]["apply_to"] or "all" in self.weight_config["reweighting"][rw]["apply_to"]:

                                for weight in self.weight_config["reweighting"][rw]["weights"]:
                                    reweight = self.assertChannel(self.weight_config["reweighting"][rw]["weights"][weight])
                                    categories[category_name]["templates"][template]["weight"].append( ("_".join([ template, weight ]), template_weight + reweight ) )

        return categories



    def readSamples(self):
        samples = self.template_tree.keys()
        samples.sort()
        for sample in samples:
            path = self.template_tree[sample]["path"]
            if not os.path.exists(path):
                print "\033[1;31mWARNING:\033[0m ", path
                continue
            print "\033[1;32mLOADING:\033[0m ", path

            categories = self.template_tree[sample]["categories"]
            for category in categories:
                if self.datacard.get(category,None) == None: self.datacard[category] = {}


                selection = categories[category]["category_selection"]
                templates = categories[category]["templates"]

                # preselecting needed branches based on weight
                branches = Weight("",[])
                for template in templates:
                    for template_name, weight in templates[template]["weight"]:
                        branches+=weight

                events = rp.read_root( paths = path, where = selection.get(), columns = branches.need + self.var.getBranches(for_df=True) )

                for template in templates:
                    for template_name, weight in templates[template]["weight"]:
                        self.datacard[category][template_name] = copy.deepcopy( self.fillHisto( events=events,
                                                                                                template=template_name, 
                                                                                                weight=weight,
                                                                                                category=category,
                                                                                                jec_shift=selection.jec_shift ) )

    def fillHisto(self, events, template, weight, category="def", jec_shift=""):
        if self.var.is2D():
            tmpHist = R.TH2D(template+"2D",template+"2D",*( self.var.bins(category) ))
        else:
            tmpHist = R.TH1F(template,template,*( self.var.bins(category) ))

        tmpHist.Sumw2(True)
        events.eval("event_weight="+weight.use, inplace=True)

        fill_with = self.var.getBranches(jec_shift=jec_shift)
        if not fill_with in events.columns.values.tolist():
            fill_with = self.var.getBranches(jec_shift="")

        rn.fill_hist( tmpHist, array = events[ fill_with ].values,
                               weights = events["event_weight"].values )

        return self.unroll2D(tmpHist)

    def unroll2D(self, th):
        if type(th) is R.TH1F: return th

        bins = th.GetNbinsX()*th.GetNbinsY()
        name = th.GetName().replace("2D","")
        unrolled = R.TH1D(name,name, *(bins,0,bins) )
        unrolled.Sumw2(True)

        for i,y in  enumerate( xrange(1,th.GetNbinsY()+1) ):
            for x in xrange(1,th.GetNbinsX()+1):
                offset = i*th.GetNbinsX()

                unrolled.SetBinContent( x+offset, th.GetBinContent(x,y) )
                unrolled.SetBinError( x+offset, th.GetBinError(x,y) )

        return unrolled

    def estimateQCDfromSS(self):

        for category in self.category_config["categories"][self.channel]:
            if not category+"_ss" in self.datacard:
                print "Warning: Not able to estimate QCD from SS in {0}".format(category)
                continue

            self.datacard[ category+"_ss" ]["QCD"] = copy.deepcopy( self.datacard[ category+"_ss" ]["data_obs"] )
            self.datacard[ category+"_ss" ]["QCD"].SetName("QCD")
            self.datacard[ category+"_ss" ]["QCD"].SetTitle("QCD")
            for h in ["Z","W","TT","VV"]:
                self.datacard[ category+"_ss" ]["QCD"].Add( self.datacard[ category+"_ss" ][h], -1 )

            self.datacard[category] ["QCD"] = copy.deepcopy( self.datacard[ category+"_ss" ]["QCD"] )

            if self.era == "2016":
                if self.channel == "mt":
                    self.datacard[category] ["QCD"].Scale(1.14)
                if self.channel == "et":
                    self.datacard[category] ["QCD"].Scale(1.15)

            if self.era == "2017":
                if self.channel == "mt":
                    self.datacard[category] ["QCD"].Scale(1.1)
                if self.channel == "et":
                    self.datacard[category] ["QCD"].Scale(1.09)    


    def estimateQCDWithABCD(self):
        for category in self.category_config["categories"][self.channel]:#
            if not category+"_ss" in self.datacard:
                print "Warning: Not able to estimate QCD with ABCD in {0}".format(category)
                continue

            abcd_parts = {}
            for c in [ category+"_ss" ,"{category}_antiiso".format(category=category) ,"{category}_antiiso_ss".format(category=category) ]:
                abcd_parts[c] = copy.deepcopy( self.datacard[c]["data_obs"] )
                for h in ["Z","W","TT","VV"]:
                    abcd_parts[c].Add( self.datacard[c][h], -1 )

            self.datacard[category]["QCD"] = abcd_parts["{category}_antiiso".format(category=category) ]
            self.datacard[category]["QCD"].SetName("QCD")
            self.datacard[category]["QCD"].SetTitle("QCD")
            self.datacard[category]["QCD"].Scale( abcd_parts[ category+"_ss" ].Integral() / abcd_parts["{category}_antiiso_ss".format(category=category) ].Integral() )        

    def estimateJetFakes(self):

        real_nominal = {}
        real_shifted = {"CMS_scale_t_1prong_Run{0}Up".format(self.era):{},
                        "CMS_scale_t_1prong_Run{0}Down".format(self.era):{},
                        "CMS_scale_t_1prong1pizero_Run{0}Up".format(self.era):{},
                        "CMS_scale_t_1prong1pizero_Run{0}Down".format(self.era):{},
                        "CMS_scale_t_3prong_Run{0}Up".format(self.era):{},
                        "CMS_scale_t_3prong_Run{0}Down".format(self.era):{}
                       }
        if not self.add_systematics: real_shifted = {}

        real_samples = []
        if self.real_est == "mc": real_samples = ["EMB","Z","VV","TT"]

        for sample in real_samples:
            real_nominal[sample] = {"path":  self.template_tree[sample]["path"] }
            real_nominal[sample]["weight"] = self.weight_config["template_weight"][self.channel][sample]

            for shift in real_shifted.keys():
                if not sample in real_shifted[shift]: real_shifted[shift][sample] = {}

                real_shifted[shift][sample] = {"path":  self.template_tree[ "_".join([sample,shift]) ]["path"] }
                real_shifted[shift][sample]["weight"] = self.weight_config["template_weight"][self.channel][sample]

        ff_templates = {}
        FF = FakeFactor( channel=self.channel,
                         variable = self.var,
                         data_file=self.template_tree["data_obs"]["path"],
                         era = self.era,
                         real_nominal = real_nominal,
                         real_shifted = real_shifted,
                         add_systematics=(self.add_systematics or self.debug),
                         debug = self.debug
                        )        
        for category in self.category_config["categories"][self.channel]:

            selection = self.template_tree["data_obs"]["categories"][category]["category_selection"]
            ff_templates[category] = FF.calc( cut = selection,  category=category )


        self.queue.put( ff_templates )


    def embeddingUncertainties(self):
         for category in self.category_config["categories"][self.channel]:
            if "EMB" in self.datacard[category]:

                for unTmp in ["EMB_CMS_htt_emb_ttbarUp", "EMB_CMS_htt_emb_ttbarDown"]:
                    self.datacard[category][unTmp] = copyTemplate( self.datacard[category]["EMB"], unTmp )

                tmpTTT = copy.deepcopy( self.datacard[category]["TTT"] )
                tmpTTT.Scale(0.1)

                self.datacard[category]["EMB_CMS_htt_emb_ttbarUp"].Add(tmpTTT)
                self.datacard[category]["EMB_CMS_htt_emb_ttbarDown"].Add(tmpTTT, -1)

                self.datacard[category]["EMB_CMS_htt_emb_ttbar_Run{0}Up".format(self.era)] = copyTemplate( self.datacard[category]["EMB_CMS_htt_emb_ttbarUp"], "EMB_CMS_htt_emb_ttbar_Run{0}Up".format(self.era) )
                self.datacard[category]["EMB_CMS_htt_emb_ttbar_Run{0}Down".format(self.era)] = copyTemplate( self.datacard[category]["EMB_CMS_htt_emb_ttbarDown"], "EMB_CMS_htt_emb_ttbar_Run{0}Down".format(self.era) )

    def splitTESuncertainties(self):
        for category in self.category_config["categories"][self.channel]:
            for name, templ in self.datacard[category].items():

                l = ""
                if "scale_t" in name: l = "t"
                if "scale_e" in name: l = "e"

                if l:
                    mcsplit      = name.replace("scale_" + l,"scale_mc_" + l)
                    embsplit     = name.replace("scale_" + l,"scale_emb_" + l)
                    correlate    = name.replace("_Run{0}".format(self.era),"" )
                    corrmcsplit  = mcsplit.replace("_Run{0}".format(self.era),"" )
                    corrembsplit = embsplit.replace("_Run{0}".format(self.era),"" )

                    self.datacard[category][correlate] = copyTemplate(templ, correlate)

                    if "EMB" in name:
                        self.datacard[category][embsplit] = copyTemplate(templ, embsplit)
                        self.datacard[category][corrembsplit] = copyTemplate(templ, corrembsplit)
                    elif "jetFakes" in name:
                        self.datacard[category][embsplit] = copyTemplate(templ, embsplit)
                        self.datacard[category][corrembsplit] = copyTemplate(templ, corrembsplit)
                        self.datacard[category][mcsplit] = copyTemplate(templ, mcsplit)
                        self.datacard[category][corrmcsplit] = copyTemplate(templ, corrmcsplit)                        
                    else:
                        self.datacard[category][mcsplit] = copyTemplate(templ, mcsplit)
                        self.datacard[category][corrmcsplit] = copyTemplate(templ, corrmcsplit)


                    
                   
                    

    def splitJECuncertainties(self):
        for category in self.category_config["categories"][self.channel]:
            for name, templ in self.datacard[category].items():
                if "scale_j" in name:

                    correlate = name.replace("_Run{0}".format(self.era),"" )
                    self.datacard[category][correlate] = copyTemplate(templ, correlate)
     



    def mergeSTXS1Cats(self):

        if self.channel == "tt":
            stage1cats = {"ggh":["0J","1J_PTH_0_60","1J_PTH_60_120","1J_PTH_120_200","1J_PTH_GT200",
                                 "GE2J_PTH_0_60","GE2J_PTH_60_120","GE2J_PTH_120_200","GE2J_PTH_GT200"],
                          "qqh":["VBFTOPO_JET3VETO","VBFTOPO_JET3","VH2JET","REST","PTJET1_GT200"]
            }
        else:
            stage1cats = {"ggh":["0J","1J_PTH_0_60","1J_PTH_60_120","1J_PTH_120_200",
                                 "GE2J_PTH_0_60","GE2J_PTH_60_120","GE2J_PTH_120_200"],
                          "qqh":["VBFTOPO_JET3VETO","VBFTOPO_JET3","VH2JET","REST","PTJET1_GT200"]
            }
             

        if not self.unrollable(stage1cats):
            print "Can not unroll"
            return

        for mode, cats in stage1cats.items():

            self.datacard[ "_".join([ mode, "unrolled" ]) ] = {}
            for name in self.datacard[mode].keys():
                tmp_unrolled =  self.getSTXS1UnrolledHist(name=name, mode=mode, cats=cats)
                tmp_unrolled.Sumw2(True)

                index = 1
                for cat in cats:

                    if name in self.datacard[ "_".join([ mode, cat ]) ]:
                        tmp = copy.deepcopy(self.datacard[ "_".join([ mode, cat ]) ][name] )
                    else:
                        tmp = copy.deepcopy( R.TH1D(name,name, *self.var.bins( "_".join([mode,cat]) ) ) )

                    for i in xrange(1, tmp.GetNbinsX() + 1) :
                        tmp_unrolled.SetBinContent(index, tmp.GetBinContent(i) )
                        tmp_unrolled.SetBinError(index, tmp.GetBinError(i) )
                        index += 1


                self.datacard[ "_".join([ mode, "unrolled" ]) ][name] = copy.deepcopy(tmp_unrolled)

                    
    def unrollable(self, stage1cats):
        for mode, cats in stage1cats.items():
            for cat in cats:
                if not "_".join([ mode, cat ]) in self.datacard:
                    return
        return True

    def getSTXS1UnrolledHist(self, name, mode, cats):
        binning = []
        for i,c in enumerate(cats):
            bins = self.var.bins( "_".join([mode,c]) )[1]
            if i == 0:
                first = bins[0]
                binning.append(first)
                interval = bins[-1] - first

            for j,b in enumerate(bins):
                if j > 0:
                    binning.append(b + i*interval)

        if self.channel != "tt":
            binning.append(6.275)

        binning = list(set(binning))
        binning.sort()

        unrolled = ( len(binning)-1, array("d", binning) )

        return R.TH1D(name,name,*unrolled )  

    def create(self, outdir = ""):

        print "Estimating jetFakes"
        p = mp.Process(target=self.estimateJetFakes)
        p.start()

        self.readSamples()
        # print "Estimating QCD"
        # if self.channel == "tt":
        #     self.estimateQCDWithABCD()
        # else:
        #     self.estimateQCDfromSS()

        if self.add_systematics:
            self.embeddingUncertainties()


        print "Waiting for jetFakes"
        jetFakes = self.queue.get(block = True)
        for category in jetFakes:
            if self.datacard.get(category,None) != None:
                self.datacard[category].update( jetFakes.get(category,{}) )
            else:
                self.datacard[category] = jetFakes.get(category,{}) 

        # Split in correlated an uncorrelated part
        self.splitTESuncertainties()
        self.splitJECuncertainties()

        if self.var.name == "predicted_prob":
            self.mergeSTXS1Cats()

        elif "ggh" in self.datacard and "qqh" in self.datacard:
            self.datacard["ggh_unrolled"] = copy.deepcopy( self.datacard["ggh"] )
            self.datacard["qqh_unrolled"] = copy.deepcopy( self.datacard["qqh"] )

        self.writeToFile( outdir )

    def writeToFile(self, outdir=""):
        if outdir:
            if self.var.name == "predicted_prob":
                outpath = "/".join([outdir, "htt_{0}.inputs-sm-Run{1}-ML.root".format(self.channel, self.era) ])
            else:
                outpath = "/".join([outdir, "htt_{0}.inputs-sm-Run{1}-{2}.root".format(self.channel, self.era, self.var.name) ])
        else:
            outdir = "_".join([self.era,"datacards"])

            if self.var.name == "predicted_prob":
                outpath = "{0}/htt_{1}.inputs-sm-Run{2}-ML.root".format(outdir,self.channel, self.era)
            else:
                outpath = "{0}/htt_{1}.inputs-sm-Run{2}-{3}.root".format(outdir,self.channel, self.era, self.var.name)

        if not os.path.exists( outdir ):
            os.mkdir(outdir)

        root_datacard = R.TFile(outpath , "RECREATE" )
        for category in self.datacard:
            tdir = "{0}_{1}".format( self.channel, category )
            root_datacard.mkdir(tdir)
            root_datacard.cd(tdir)
            for template,hist in self.datacard[category].items():
                hist.Write()
        root_datacard.Close()
        print "Written to:", outpath
    

def copyTemplate(template, name):

    newtemplate = copy.deepcopy(template)
    newtemplate.SetName(name)
    newtemplate.SetTitle(name)

    return newtemplate


if __name__ == '__main__':
    main()
