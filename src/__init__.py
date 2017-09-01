# the utility package
from os import path as pt
print("Initialize xtong utility package.")


def spn(fnm, **kwd):
    """ split name into prefix, middle name, and surfix. """
    if kwd.get('abs', False):
        fnm = pt.abspath(fnm)

    # normalization
    fnm = pt.normpath(fnm)

    # normal cases
    pfx = pt.dirname(fnm)
    mid = pt.basename(fnm)

    # no file surfix?
    if '.' in mid:
        mdn, sfx = mid.split('.', 1)
    else:
        mdn, sfx = mid, ''
    return pfx, mdn, sfx


def spz(fo, s):
    """ save python object to gziped pickle """
    import gzip
    import pickle

    if not fo.endswith(".pgz"):
        fo = "{}.pgz".format(fo)
    with gzip.open(fo, 'wb') as gz:
        pickle.dump(s, gz, -1)


def lpz(fi):
    """ load python object from gziped pickle, or from
    gzipped numpy file (*.npz). """
    import gzip
    import pickle
    import os
    import numpy as np

    if os.path.exists("{}.pgz".format(fi)):
        fi = "{}.pgz".format(fi)

    if os.path.exists("{}.npz".format(fi)):
        fi = "{}.npz".format(fi)

    if fi.endswith('.npz'):
        return dict((k, v) for k, v in np.load(fi).items())
    else:
        with gzip.open(fi, 'rb') as gz:
            return pickle.load(gz)


def xpt(whr, **kwd):
    """ export the progress in texture format. """
    import os
    import numpy as np

    # output directory
    odr = pt.join(pt.dirname(whr), pt.basename(whr).split('.')[0])

    # try to create it.
    try:
        os.mkdir(odr)
    except FileExistsError as e:
        pass

    # reject items
    rej = kwd.pop('rej', [])

    inf = []
    for k, v in kwd.items():
        if k in rej:
            continue
        if type(v) in [int, float, str]:
            inf.append('{}={}\n'.format(k, v))
        elif isinstance(v, np.number):
            inf.append('{}={}\n'.format(k, v))
        elif isinstance(v, np.ndarray) and v.size < 2:
            inf.append('{}={}\n'.format(k, v))
        elif isinstance(v, np.ndarray) and v.ndim < 3:
            np.savetxt(pt.join(odr, k), v, '%s', '\t')
        else:
            print(k, type(v), 'not exported')

    with open(pt.join(odr, 'inf'), 'w') as f:
        f.writelines(inf)
    return kwd


def match_sfx(bsn):
    """ match full filename with basename plus a list of
    candidate surfix, which is ['pgz', 'npz', 'npy', 'txt'].

    bsn: the basename
    """

    # try candidate surfix
    sfx = ['pgz', 'npz', 'npy', 'txt']
    for e in sfx:
        if pt.exists(bsn + '.' + e):
            return bsn + '.' + e

    # also try the filename without surfix
    if pt.exists(bsn):
        return bsn

    # give up
    return None


def fpg(fnm, sav='.', **kwd):
    """ find suggested input, and progress save. """
    # verbosity level.
    vbs = kwd.pop('vbs', 1)

    # directory, middle name, and surfix
    pfx, mid, sfx = spn(fnm)

    # suggest location for input
    if not pt.exists(fnm):
        fnm = match_sfx(pt.join(pfx, mid))

    # suggest location for save
    if pt.isdir(sav):
        sav = pt.normpath(pt.join(sav, mid))

    # try usual sufix
    dst = match_sfx(sav)

    # try input surfix
    if dst is None and sfx != '':
        if pt.exists(sav + '.' + sfx):
            dst = sav + '.' + sfx

    # return progress status and suggested location
    if dst is None:
        if vbs > 0:
            print('XU: progress is new:', dst)
    else:
        if vbs > 0:
            print('XU: progress exists:', dst)
        sav = dst
    return fnm, sav


def lpg(fnm, **kwd):
    """ load progress.
    -- fnm: input filename.
    ******** keywords ********
    ** sav: previously saved progress.
    ** new: allow new progress if both fnm and sav were not file?
    default is false, rasing {FileNotFoundError}.

    ** prg: progress settings
    0: start over if not already in progress, {sav} must not exist.
    1: continue on saved progress, start over if necessary (def).
    2: start over forceably, overwrite existing progress.

    ** rej: items to be rejected, even if they are not in {kwd}
    but found in fnm or sav

    ** kpr: key preference
    -- 0: {kwd} take precedence
    -- 1: {sav} or {fnm} take precedence

    ** but: keys to be excepted when considering precedence


    """
    # verbosity level.
    vbs = kwd.pop('vbs', 1)

    # suggest location for raw input and saved progress
    fnm, sav = fpg(fnm, kwd.get('sav', '.'))
    kwd['fnm'] = fnm
    kwd['sav'] = sav

    # progress settings
    prg = kwd.pop('prg', 1)

    # only start if no progress already exists
    if prg == 0 and pt.exists(sav):
        if vbs > 0:
            print("XT: Skip,", sav, "exists.", sep="")
        return (0, kwd)

    # continue on saved progress
    elif prg == 1 and pt.exists(sav):
        dat = lpz(sav)
        if vbs > 0:
            print("XT: Continue,", sav, "loaded.")

    # start over
    elif pt.exists(fnm):
        dat = lpz(fnm)
        if vbs > 0:
            print("XT: Restart,", fnm, "loaded.")
        prg = 2

    # missing both
    else:
        new = kwd.pop('new', False)
        # raise issue if empty start is not allowed
        if not new:
            raise FileNotFoundError(fnm + ' & ' + sav)

        # otherwise, return empty progress
        if vbs > 0:
            print("XT: Empty,", fnm, "&", sav, "are not files.")
        return (3, kwd)

    # rejection
    rej = kwd.pop('rej', [])
    for k in rej:
        dat.pop(k, None)

    # preference settings
    # 0: kwd take precedence
    # 1: dat take precedence
    kpr = kwd.pop('kpr', 0)
    if kpr == 0:
        cpy = dat
        org = kwd
    else:
        cpy = kwd.copy()
        org = dat

    but = kwd.pop('but', [])
    for k, v in org.items():
        if k in but and k in cpy:
            continue
        cpy[k] = v

    return (prg, cpy)


def spg(save_as=None, **kwd):
    """ save progress.

    fnm: the new location to save as.
    ********** keywords **********
    ** sav: original save loacation. if {fnm} is none, save to this
    location by default.

    ** rej: keys items not to be saved even if they exist in {kwd}.
    """
    # verbosity level
    vbs = kwd.pop('vbs', 1)

    # check new and previously save location
    # save as
    if save_as is not None:
        sav = save_as
        if vbs > 0:
            print('XU: save as:', sav)
    # try previous save
    else:
        sav = kwd.get('sav', None)
    if sav is not None:
        if vbs > 0:
            print('XU: save to:', sav)
    # suggest local save
    else:
        fnm = kwd.get('fnm', None)
        if fnm is not None:
            fnm, sav = fpg(fnm, '.')
            if vbs > 0:  # verbosity
                print("save as:", sav, '(suggest)')
        else:
            raise ValueError('fail to infer save location.')

    # make a shallow copy
    cpy = kwd.copy()

    # reject some items
    rej = cpy.pop('rej', [])
    for k in rej:
        kwd.pop(k, None)

    # save the dictionary
    kwd['sav'] = sav
    spz(sav, kwd)
    return kwd
