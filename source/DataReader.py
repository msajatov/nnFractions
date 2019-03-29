import pandas
import root_pandas as rp

class DataReader:

    def __init__(self):
        pass

    def get_data_frame(self, path, where, columns):
        tmp = rp.read_root(paths=path,
                           where=where,
                           columns=columns,
                           chunksize=None)

        return tmp

    def get_iterator(self, path, where, columns, chunksize):
        tmp = rp.read_root(paths=path,
                           where=where,
                           columns=columns,
                           chunksize=chunksize)

        return tmp

