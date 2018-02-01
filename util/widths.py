"""
for widths
"""

import numpy as np
import filfind_class as filfind


def get_width_fit_filfind(moment_0_map, tree, hdr):
    """ get width fit from filfind with moment 0 map, tree param & header
    Arguments:
        moment_0_map {2d np.array} -- of data
        tree {maskTree} -- tree
        hdr {fits header} -- sample header
    Returns:
        list -- Amplitude, Width, Background, FWHM
    """
    fils = filfind.fil_finder_2D(moment_0_map, header=hdr, beamwidth=10.0, glob_thresh=20,
                                 distance=100, flatten_thresh=95, standard_width=0.5,
                                 size_thresh=600, mask=tree.root_node.mask)
    fils.medskel()
    fils.analyze_skeletons(skel_thresh=1000.0, branch_thresh=50)
    fils.exec_rht()
    fils.find_widths(verbose=False, try_nonparam=False, auto_cut=False, max_distance=0.6)

    if fils.number_of_filaments == 1:
        width_fit = fils.width_fits['Parameters'][0, :]
        width_fit_err = fils.width_fits['Errors'][0, :]
    else:
        main_filament_index = np.argmax(fils.lengths)
        width_fit = fils.width_fits['Parameters'][main_filament_index, :]
        width_fit_err = fils.width_fits['Errors'][main_filament_index, :]

    return width_fit, width_fit_err
