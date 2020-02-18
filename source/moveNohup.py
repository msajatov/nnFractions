import shutil
import argparse
import time
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-c', dest='channel', help='Decay channel' ,choices = ['mt', 'et', 'tt', 'em'], default='mt')
parser.add_argument('-e', dest='era',  help='Era', choices=["2016", "2017"], required = True)
parser.add_argument('-name', dest='name',   help='Global data scaler', default='none')
parser.add_argument('-varset', dest='varset',   help='Global data scaler', default='none')
parser.add_argument('-emb', dest='emb',   help='Global data scaler', action='store_true')
args = parser.parse_args()

abort = False
counter = 0
while not abort:
    if args.emb:
        emb = "emb"
    else:
        emb = ""

    try:
        destfolder = "/afs/cern.ch/work/m/msajatov/private/CMSSW_9_4_0/src/dev/nnFractions/output/models/{0}_{1}_{2}/{3}".format(args.name, args.varset, emb, args.era, args.channel)
        if args.emb:
            filename = "nohup_{0}_{1}_{2}_{3}_emb.out".format(args.name, args.varset, args.channel, args.era)
            shutil.move(filename, destfolder + "/" + filename)
        else:
            filename = "nohup_{0}_{1}_{2}_{3}.out".format(args.name, args.varset, args.channel, args.era)
            shutil.move(filename, destfolder + "/" + filename)
        print "Successfully copied nohup.out to " + destfolder + "/" + filename
        sys.exit(0)
    except Exception as e:
        print "Cannot copy nohup.out; " + str(e)
    time.sleep(10)
    counter += 1
    if counter > 20:
        abort = True

