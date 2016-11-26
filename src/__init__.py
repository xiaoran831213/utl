# the utility package
print("initialize utility package.")


def spz(fo, s):
    """ save python object to gziped pickle """
    import gzip
    import pickle

    if not fo.endswith(".pgz"):
        fo = "{}.pgz".format(fo)
    with gzip.open(fo, 'wb') as gz:
        pickle.dump(s, gz, -1)


def lpz(fi):
    """ load python object from gziped pickle """
    import gzip
    import pickle
    import os
    if os.path.exists("{}.pgz".format(fi)):
        fi = "{}.pgz".format(fi)
    with gzip.open(fi, 'rb') as gz:
        return pickle.load(gz)
