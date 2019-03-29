import pandas
import root_pandas as rp


sample_path = "/afs/hephy.at/data/higgs01/v10/mt-NOMINAL_ntuple_TT.root"
select = "mt_1 < 50"
branches = ["pt_2",
            "jpt_1",
            "jpt_2",
            "mt_1"]

chunksize = 100

tmp = rp.read_root( paths = sample_path,
                    where = select,
                    columns = branches,
                    chunksize = chunksize)
