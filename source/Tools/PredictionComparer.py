import root_numpy as rn
import ROOT as R
from ROOT import TFile
import root_pandas as rp
from pandas import DataFrame, concat
import copy
import os


def main():

    basepath1 = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/predictions/4cat_vars8/2017"
    basepath2 = "/afs/hephy.at/work/m/msajatovic/CMSSW_9_4_0/src/dev/nnFractions/output/predictions/4cat_vars8/inverted/2017"

    filenames1 = ["mt-NOMINAL_ntuple_TT.root"]
    filenames2 = ["mt-NOMINAL_ntuple_TT.root"]
    
    for i, file in enumerate(filenames1):
        fullfilename1 = os.path.join(basepath1, filenames1[i])
        fullfilename2 = os.path.join(basepath2, filenames2[i])
        
        tfile1 = R.TFile(fullfilename1, "read")
        #tfile2 = R.TFile(fullfilename2, "read")
        
        tree1 = tfile1.TauCheck
        tree1.AddFriend("TauCheck2=TauCheck", fullfilename2)
        cv0 = R.TCanvas()
        tree1.Draw("predicted_frac_prob_0:TauCheck2.predicted_frac_prob_0")
        cv1 = R.TCanvas()
        tree1.Draw("predicted_frac_prob_1:TauCheck2.predicted_frac_prob_1")
        cv2 = R.TCanvas()
        tree1.Draw("predicted_frac_prob_2:TauCheck2.predicted_frac_prob_2")
        cv3 = R.TCanvas()
        tree1.Draw("predicted_frac_prob_3:TauCheck2.predicted_frac_prob_3")
        
        x = raw_input("raw input")
        

#         branches = ["predicted_frac_class", "predicted_frac_prob", "predicted_frac_prob_0", 
#                     "predicted_frac_prob_1", "predicted_frac_prob_2", "predicted_frac_prob_3"]
# 
#         tfile1.TauCheck.Print()   
    
        #file.TauCheck.GetEntries(cut)
        
        
#         root > TFile f1("file1.root");
# root > TTree *T = (TTree*)f1.Get("T");
# root > T->AddFriend("T2=T","file2.root");
# root > T->Draw("x:T2.x")
            
            
if __name__ == '__main__':
    main()