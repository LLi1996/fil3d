"""
GALFA specific util functions

"""

from astropy.io import fits
import glob
from cube_fil_finder.galfa import galfa_const
from cube_fil_finder.galfa import galfa_v_lookup
from cube_fil_finder.util import cube_util
import numpy as np


DATA_SLICE_BASE_DIR = '/Volumes/LarryExternal1/Research_2017/GALFA_slices_backup/umask_gaussian_30/'


def get_galfa_slice_paths_from_tree(tree, data_dir=None):
    """gets the paths to galfa slices from a tree and data directory
    Arguments:
        tree {maskTree} -- of masks
    Keyword Arguments:
        data_dir {str} -- of galfa slices (default: {None})
    Return:
        slice_paths_list {list} -- of paths to slices (sorted)
    """
    slice_paths_list = []
    length = tree.length
    starting_slice_index = tree.root_v_slice

    slice_base_dir = galfa_const.GALFA_BACKUP_DATA_DIR if data_dir is None else data_dir

    if slice_base_dir[-1] != '/':
        slice_base_dir = slice_base_dir + '/'

    for i in range(length):
        slice_path = glob.glob(slice_base_dir + '*{0}*'.format(str(starting_slice_index + i)))[0]
        slice_paths_list.append(slice_path)

    slice_paths_list.sort()

    return slice_paths_list


def get_cut_cube_from_galfa_slice_paths(slice_paths_list, tree=None):
    """gets a cut data cube specifed by the dimention of the node and length of
    the slice_path_list
    Arguments:
        slice_paths_list {list} -- of full paths to galfa data slices
    Keyword Arguments:
        tree {maskTree} -- we use the corners to cut the slices (default: {None})
    """
    this_structure_cube = []
    for f in slice_paths_list:
        full_slice, hdr = fits.getdata(f, header=True)
        # probably should check some header info here
        if tree is None:
            this_structure_cube.append(full_slice)
        else:
            this_structure_cube.append(cut_galfa_slice_from_tree(full_slice, tree))

    return np.asarray(this_structure_cube)


def cut_galfa_slice_from_tree(data_slice, tree):
    """cut out from a data slice the data indicated inside the tree mask box
    Arguments:
        data_slice {2d np.array} -- of data, shape(m, n) "y-x"
        tree {maskTree} -- containing nodes with masks
    Returns:
        cut_data_slice {2d np.array}
    """
    return cut_galfa_slice_from_node(data_slice, tree.root_node)


def cut_galfa_slice_from_node(data_slice, node):
    """cut out from a data slice the data indicated inside the mask box
    Arguments:
        data_slice {2d np.array} -- of data, shape(m, n) "y-x"
        node {maskNode} -- containing a mask
    Returns:
        cut_data_slice {2d np.array}
    """
    return cut_galfa_slice_from_corners(data_slice, node.corners)


def cut_galfa_slice_from_corners(data_slice, corners):
    """cut out a data slice from the original slice and box corners
    Arguments:
        data_slice {2d np.array} -- of data shape(m, n) "y-x"
        corners {list of list} -- [[xmin, ymin], [xmax, ymax]]
    Return:
        cut_data_slice {2d np.array}
    """
    cut_data_slice = data_slice[corners[0][1]:corners[1][1], corners[0][0]:corners[1][0]]
    return cut_data_slice


def get_galfa_data_cube_from_tree(tree):
    """ cut out a data cube from galfa data from given tree spec
    Arguments:
        tree {maskTree} -- tree
    Returns:
        3d np.array -- v,y,x
    """
    data_slice_paths = get_galfa_slice_paths_from_tree(tree, data_dir=DATA_SLICE_BASE_DIR)
    data_cube = get_cut_cube_from_galfa_slice_paths(data_slice_paths, tree)
    return data_cube


def galfa_index_to_lb(xs, ys, verbose=False):
    """gets ls & bs assuming galfa standard indexing
    Arguments:
        xs {list/np.array} -- of indexes
        ys {list/np.array} -- of indexes
    Keyword Arguments:
        verbose {bool} -- (default: {False})
    Returns:
        ls, bs {np.array} -- of ls bs
    """
    hdr = galfa_const.MOCK_GALFA_HDR
    ras, decs = galfa_index_to_radecs(xs, ys, verbose=verbose)
    return cube_util.radecs_to_lb(ras, decs)


def lbs_to_galfa_index(ls, bs, remin=False, verbose=False):
    """gets galfa xs & ys from ls & bs asssuming galfa standard indexing
    Arguments:
        ls {list/np.array} -- of galactic longitude
        bs {list/np.array} -- of galactic latitude
    Keyword Arguments:
        verbose {bool} -- (default: {False})
    """
    hdr = galfa_const.MOCK_GALFA_HDR
    ras, decs = cube_util.lbs_to_radecs(ls, bs, remin=remin)
    return radec_to_galfa_index(ras, decs, verbose=verbose)


def galfa_index_to_radecs(xs, ys, verbose=True):
    """
    turns arrays of indecies to ra, dec based on header

    Arguments:
        xs {[type]} -- [description]
        ys {[type]} -- [description]
        hdr {[type]} -- [description]
    """
    hdr = galfa_const.MOCK_GALFA_HDR

    if type(xs) != np.ndarray:
        xs = np.array(xs)
    if type(ys) != np.ndarray:
        ys = np.array(ys)

    if xs.size != ys.size:
        if verbose:
            print "\t x & y array sizes different in conversion to RA-DEC"

    ras = (xs - hdr['CRPIX1']) * hdr['CDELT1'] + hdr['CRVAL1']
    decs = (ys - hdr['CRPIX2']) * hdr['CDELT2'] + hdr['CRVAL2']
    # ^redundant but the right way?
    return ras, decs


def radec_to_galfa_index(ras, decs, verbose=True):
    """
    turns arrays of ra, dec into indecies based on header

    Arguments:
        ras {[type]} -- [description]
        decs {[type]} -- [description]
        hdr {[type]} -- [description]
    """
    hdr = galfa_const.MOCK_GALFA_HDR

    if type(ras) != np.ndarray:
        ras = np.array(ras)
    if type(decs) != np.ndarray:
        decs = np.array(decs)

    assert ras.size == decs.size, "\t x & y array sizes different in conversion to RA-DEC"

    xs = (ras - hdr['CRVAL1']) / hdr['CDELT1'] + hdr['CRPIX1']
    ys = (decs - hdr['CRVAL2']) / hdr['CDELT2'] + hdr['CRPIX2']
    # ^redundant but the right way?
    return xs, ys


def galfa_v_lookup_from_index(index, wide=True):
    """ gets the velocity given channel index
    Arguments:
        index {float} -- channel
    Keyword Arguments:
        wide {bool} -- wide or narrow (default: {True})
    """
    if wide:
        galfa_v_lookup_list = galfa_v_lookup.GALFA_V_LOOKUP_W
    else:
        # for narrow v channels -- don't have them yet
        galfa_v_lookup_list = []
    return (galfa_v_lookup_list[int(np.floor(index))] + galfa_v_lookup_list[int(np.ceil(index))]) / 2.
