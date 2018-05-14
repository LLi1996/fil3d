"""
for widths calculations from filfinder
"""

from astropy import units as u
import numpy as np
from fil_finder import FilFinder2D


def get_width_fit_filfind(moment_0_map, tree, hdr):
    """ get width fit from filfind with moment 0 map, tree param & header
    Arguments:
        moment_0_map {2d np.array} -- of data
        tree {maskTree} -- tree
        hdr {fits header} -- sample header
    Returns:
        list -- Amplitude, Width, Background, FWHM
    """
    hdr['BUNIT'] = 'k'  # as opposed to 'k (tb)' which isn't recognized by astropy.units
    mask = tree.root_node.mask

    fils = FilFinder2D(moment_0_map, header=hdr, distance=100. * u.pc, beamwidth=10. * u.arcmin,
                       mask=mask)
    fils.preprocess_image(flatten_percent=95)
    fils.create_mask(use_existing_mask=True)

    fils.medskel()
    fils.analyze_skeletons(skel_thresh=0.1 * 8 * u.pc)
    fils.exec_rht()
    fils.find_widths(try_nonparam=False, auto_cut=False, add_width_to_length=False,
                     xunit=u.pc, max_dist=0.6 * u.pc, deconvolve_width=False)

    main_filament_index = np.argmax(fils.lengths())
    if np.isnan(fils.filaments[main_filament_index]._fwhm):
        return np.nan, np.nan
    else:
        width_fit = fils.widths(unit=u.pc)[0][main_filament_index].value
        width_fit_err = fils.widths(unit=u.pc)[1][main_filament_index].value

        return width_fit, width_fit_err
