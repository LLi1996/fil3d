"""

Cube 0th, 1st, 2nd moments, Column densities

LL2018
"""

import numpy as np

from cube_fil_finder.galfa import galfa_const
from cube_fil_finder.galfa import galfa_util


def mask_map_2d(map_2d, mask_2d):
    """ masks a 2d map with a 2d mask of same shape
    Arguments:
        map_2d {2d np.array} -- data
        mask_2d {2d np.array} -- mask
    Returns:
        2d np.array -- data with the 0 values on the masks zeroed out
    """
    map_2d = np.asarray(map_2d)
    mask_2d = np.asarray(mask_2d)
    if np.shape(map_2d) == np.shape(mask_2d):
        map_2d[np.where(mask_2d == False)] = np.NaN
    else:
        print('ERROR: data and mask don\'t have the same shape, returning data...')
    return map_2d


def moment_0_from_cube(data_cube, mask=None):
    """ calculate a 0th moment map from data cube
    Arguments:
        data_cube {3d np.array} -- v,y,x in that order
    Keyword Arguments:
        mask {2d np.array} -- mask (default: {None})
    Returns:
        2d np.array -- 0th moment map
    """
    moment_0_map = np.zeros_like(data_cube[0])
    for s in data_cube:
        if mask is None:
            moment_0_map = np.add(moment_0_map, s)
        else:
            moment_0_map = np.add(moment_0_map, mask_map_2d(s, mask))

    moment_0_map = moment_0_map * galfa_const.GALFA_W_SLICE_SEPARATION

    return moment_0_map


def moment_1_from_cube(data_cube, starting_v_index, v_length, mask=None):
    """ calculate a 1st moment map from data cube
    Arguments:
        data_cube {3d np.array} -- v,y,x
        starting_v_index {int} -- galfa velocity index of starting slice
        v_length {int} -- length in velocity
    Keyword Arguments:
        mask {2d np.array} -- mask (default: {None})
    Returns:
        2d np.array -- 1st moment map
    """
    moment_0_map = moment_0_from_cube(data_cube, mask=mask)
    moment_1_map = np.zeros_like(data_cube[0])
    for i in range(v_length):
        v_index = starting_v_index + i
        s = data_cube[i] * galfa_util.galfa_v_lookup_from_index(v_index)
        if mask is None:
            moment_1_map = np.add(moment_1_map, s)
        else:
            moment_1_map = np.add(moment_1_map, mask_map_2d(s, mask))

    moment_1_map = moment_1_map * galfa_const.GALFA_W_SLICE_SEPARATION / moment_0_map

    return moment_1_map


def moment_2_from_cube(data_cube, starting_v_index, v_length, mask=None):
    """ calculate a 2nd moment map from data cube
    Arguments:
        data_cube {3d np.array} -- v,y,x
        starting_v_index {int} -- galfa velocity index of starting slice
        v_length {int} -- length in velocity
    Keyword Arguments:
        mask {2d np.array} -- mask (default: {None})
    Returns:
        2d np.array -- 2nd moment map
    """
    moment_2_map = np.zeros_like(data_cube[0])
    moment_1_map = moment_1_from_cube(data_cube, starting_v_index, v_length, mask=mask)
    moment_0_map = moment_0_from_cube(data_cube, mask=mask)
    for i in range(v_length):
        v_index = starting_v_index + i
        s = data_cube[i] * (galfa_util.galfa_v_lookup_from_index(v_index) - moment_1_map)**2
        if mask is None:
            moment_2_map = np.add(moment_2_map, s)
        else:
            moment_2_map = np.add(moment_2_map, mask_map_2d(s, mask))

    moment_2_map = (moment_2_map * galfa_const.GALFA_W_SLICE_SEPARATION / moment_0_map)**(.5)

    return moment_2_map


def column_density_from_moment_0_map(moment_0_map):
    return (1.823 * 10**18) * moment_0_map


def column_density_from_cube(data_cube, mask=None):
    """ calculate column density from a data cube
    Arguments:
        data_cube {3d np.array} -- v,y,x
    Keyword Arguments:
        mask {2d np.array} -- mask (default: {None})
    Returns:
        2d np.array -- column density
    """
    moment_0_map = moment_0_from_cube(data_cube, mask=mask)
    return column_density_from_moment_0_map(moment_0_map)
