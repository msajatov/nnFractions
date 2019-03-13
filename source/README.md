## Setup for XGBoost and Keras 

### Option 1 
1) Source softwarestack from LCG (always needed)  

        source /cvmfs/sft.cern.ch/lcg/views/LCG_93c/x86_64-slc6-gcc62-opt/setup.sh 

2) Install xgboost and root_pands (only needed once) 

        pip install --user xgboost 
        pip install --user keras==2.1.1
        pip install --user root_pandas==0.6.1 

3) Add local python packages to PYTHONPATH ( best to add to ~/.profile ) 

        `export PYTHONPATH=$HOME/.local/lib/python2.7/site-packages:$PYTHONPATH`

### Option 2 
	
Set up a CMSSW environment (`>=9_4_0`). All needed packages are included in the softwarestack. 

However, `keras` and `root_pandas` need to be updated to version `2.1.1` and `0.6.1` respectively

## Quickguide 
	
Use **run_model.py** to train (`-t`) model (`-m [keras,xgb]`) on events for a given channel (`-c [mt,et,tt]`). Samples and input variables must be specified in `conf/global_config*.json`. To get proper training weights run **calc_train_weights.py** after variables and samples are specified. 

