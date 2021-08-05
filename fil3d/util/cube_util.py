"""
utility functions related to cleaning data cubes

LL2017

"""
import logging
import math
import os

import numpy as np
import scipy.ndimage
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.wcs import WCS


def circ_kern(diameter):
    """
    Performs a circle-cut of given diameter on inkernel.
    Outkernel is 0 anywhere outside the window.
    taken from https://github.com/seclark/RHT/blob/master/rht.py

    for umask step
    """
    assert diameter % 2
    r = diameter // 2  # int(np.floor(diameter / 2))
    mnvals = np.indices((diameter, diameter)) - r
    rads = np.hypot(mnvals[0], mnvals[1])
    return np.less_equal(rads, r).astype(np.int)


def umask(data, radius=15, filter_opt='tophat', smr_mask=None, verbose=False):
    """
    unsharp masking of a data slice
    taken from https://github.com/seclark/RHT/blob/master/rht.py
    ^conversion to binary data step skipped

    radius is set to 15 by default for GALFA data: diameter of 30 arcmin
    """
    assert data.ndim == 2

    if filter_opt == 'tophat':
        logging.debug("doing tophat umask filter")
        kernel = circ_kern(2 * radius + 1)
        outdata = scipy.ndimage.filters.correlate(data, kernel)

        # Correlation is the same as convolution here because kernel is symmetric
        # Our convolution has scaled outdata by sum(kernel), so we will divide out these weights.
        kernweight = np.sum(kernel)
        fin_out_data = data - outdata / kernweight

    elif filter_opt == 'gaussian':
        logging.debug("doing gaussian umask filter")
        # we want the FWHM to = radius so we do the FWHM = 2(2ln2)^.5 sigma conversion
        sigma = float(radius) / (8 * math.log(2)) ** 0.5
        if verbose:
            print(sigma)
        fin_out_data = data - scipy.ndimage.filters.gaussian_filter(data, sigma)

    else:
        return 0

    fin_out_data[np.where(fin_out_data < 0.0)] = 0

    # print np.shape(fin_out_data)

    # set NaNs to 0??
    # subtr_data[np.where(subtr_data == np.NaN)] = 0

    if smr_mask is None:
        return fin_out_data
    else:
        return np.logical_and(smr_mask, fin_out_data)


def index_to_radec(xs, ys, hdr, verbose=True):
    """DEPRECATED -- use galfa_util.galfa_index_to_radecs instead
    """
    from fil3d.galfa import galfa_util
    print('DEPRECATED -- use galfa_util.galfa_index_to_radecs instead')
    return galfa_util.galfa_index_to_radecs(xs, ys, hdr, verbose=verbose)


def radecs_to_lb(ras, decs):
    """
    Transformation between lists of ras, decs, to ls, bs. Assumes ra, dec in degrees
    Conforms to astropy 0.4.3
    taken from https://github.com/seclark/FITSHandling/commit/f04a6e54c6624741e4f3077ba8ba96af620871ac

    for lb masks
    """
    obj = SkyCoord(ras, decs, unit="deg", frame="icrs")
    obj = obj.galactic

    ls = obj.l.degree
    bs = obj.b.degree

    return ls, bs


def lbs_to_radecs(ls, bs, remin=False):
    """
    Transformation between lists of ls, bs, to ras, decs. Assumes all in degrees
    Conforms to astropy 0.4.3
    taken from https://github.com/seclark/FITSHandling/commit/f04a6e54c6624741e4f3077ba8ba96af620871ac
    """
    assert len(ls) == len(bs)
    obj = SkyCoord(ls, bs, unit="deg", frame="galactic")
    obj = obj.icrs

    ras = obj.ra.degree
    decs = obj.dec.degree

    if remin:
        ra_min = np.argmin(ras)
        ras = np.hstack((ras[ra_min:], ras[:ra_min]))
        decs = np.hstack((decs[ra_min:], decs[:ra_min]))
        return ras, decs

    return ras, decs


def galfa_index_to_lb(xs, ys, verbose=False):
    """DEPRECATED -- use galfa_util.galfa_index_to_lb instead
    """
    import fil3d.galfa.galfa_util as galfa_util
    print('DEPRECATED -- use galfa_util.galfa_index_to_lb instead')
    return galfa_util.galfa_index_to_lb(xs, ys, verbose=verbose)


def mask_lb(data, hdr, b_cutoff=30, toNaN=False, l_cutoff=None):
    pass


def umask_and_save(data, hdr, save_dir, file_name, radius=None, umask_filter=None):
    """
    unsharp masking a data slice and saving it
    """
    save_path = os.path.join(save_dir, file_name.rsplit('.', 1)[0] + '_umask.fits')

    logging.info('applying un-sharp masking ...')
    umask_data = umask(data, radius, umask_filter)

    logging.info('saving un-sharp masked data to {0} ...'.format(save_path))
    fits.writeto(save_path, umask_data, header=hdr)

    return umask_data


def cube_transfer(data_cube,
                  hdr: fits.Header):
    """ Compute the coordinate transfer for the whole cube
    From Avery
    Returns to imshow extent coordinates
    """
    w = WCS(hdr)
    lenv, leny, lenx = data_cube.shape
    square = np.array([[0, 0, 0],
                       [0, leny, 0],
                       [lenx, 0, 0],
                       [lenx, leny, 0]])
    translated = w.wcs_pix2world(square, 1)[:, :2]
    ra_min, dec_min = translated[0]
    ra_max, dec_max = translated[-1]
    coord_list = np.array([ra_max, ra_min, dec_min, dec_max])
    return coord_list
