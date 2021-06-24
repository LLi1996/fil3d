"""
Utility functinos related to nodes and trees

simple hash functions for the names of nodes and trees
sorting function based on the hashed names

LL2017
"""

import logging
import pickle
import warnings

import numpy as np

from fil3d.structs import MaskObjNode
from fil3d.util import cube_util


def node_key_hash(original_key):
    warnings.warn('use MaskObjNode.add_node_to_dict instead.', DeprecationWarning)
    return MaskObjNode.node_key_hash(original_key=original_key)


def node_key_unhash(key):
    """Unhash them node keys
    Arguments:
        key {str} -- hashed node key
    Returns:
        int, int -- masked_area_size, number
    """
    key_decomp = key.rsplit('_')

    masked_area_size = int(key_decomp[0])
    number = key_decomp[1]

    return masked_area_size, number


def add_node_to_dict(node, dictionary):
    warnings.warn('use MaskObjNode.add_node_to_dict instead.', DeprecationWarning)
    MaskObjNode.add_node_to_dict(node=node, dictionary=dictionary)


def node_key_hashable(key):
    try:
        _ = node_key_unhash(key)
        return True
    except Exception as e:
        return False


def tree_key_hash(original_key):
    """Hash them tree keys
    in format: masked_area_size + '_' + starting_v + '_' + some number
    Arguments:
        original_key {str} -- unhashed tree key
    """
    key_base = original_key.rsplit('_', 1)[0]
    key_num = int(original_key.rsplit('_', 1)[1])

    key_num += 1

    new_key = key_base + '_' + str(key_num)
    return new_key


def tree_key_unhash(key):
    """Unhash them tree keys
    Arguments:
        key {str} -- hashed tree key
    Returns:
        int, int, int -- masked_area_size, starting_v, number
    """
    key_decomp = key.rsplit('_')

    masked_area_size = int(key_decomp[0])
    starting_v = int(key_decomp[1])
    number = key_decomp[2]

    return masked_area_size, starting_v, number


def add_tree_to_dict(tree, dictionary):
    """Adds a tree to the dictionary
    prevents key overlaps by hasing
    Arguments:
        tree {MaskObjNodeTree} -- tree to be added
        dictionary {dict} -- of trees
    """
    key = str(tree.getTreeMaskedArea2D())
    key += '_' + str(tree.getTreeStartingVelocity()) + '_0'

    while key in dictionary:
        key = tree_key_hash(key)

    dictionary[key] = tree
    return key


def pop_tree_from_dict(tree_key, dictionary):
    """
    pop a tree from the dictionary

    :param tree_key:

    :param dictionary:

    :return:
    """
    if tree_key in dictionary:
        logging.debug('removing tree {0} from the dictionary of trees'.format(tree_key))
        return dictionary.pop(tree_key)
    else:
        raise KeyError('{0} not a valid tree key'.format(tree_key))


def sorted_struct_dict_keys_by_area(dict_keys, key_type, descending=True):
    """Sort struct dict keys by masked area size
    Arguments:
        dict_keys {list} -- of hashed struct keys
        key_type {str} -- either 'node' or 'tree'
    Keyword Arguments:
        descending {bool} -- if reverse sort (default {True})
    Return
        {list} -- of keys sorted
    """
    # map keys into (key, size of mask)s
    if key_type.lower() == 'node':
        mapped_keys = [(k, node_key_unhash(k)[0]) for k in dict_keys]
    elif key_type.lower() == 'tree':
        mapped_keys = [(k, tree_key_unhash(k)[0]) for k in dict_keys]
    else:
        return []
    # sort (key, size of mask)s by size of mask
    sorted_mapped_keys = sorted(mapped_keys, key=lambda x: x[1], reverse=descending)
    # map (key, size of mask) back to keys
    return [k_size[0] for k_size in sorted_mapped_keys]


class PreV001Unpickler(pickle.Unpickler):
    """ Child class of pickle.Unpickler with updated find_class() behavior to help with unpickling very old structs
    """

    def find_class(self, module, name):
        """ Overloaded ``find_class()`` that handles module renames when unpickling
        Will rename 'cube_fil_finder.structs.mask_obj_node' and 'cube_fil_finder.structs.mask_obj_node_tree' input
        modules (old, pre v0.0.1 import paths for structs) to just 'fil3d' since all imports can be done at the top
        ``fil3d`` level now.

        :param module: See ``Unpickler.find_class()``.

        :param name: See ``Unpickler.find_class()``.

        :return: See ``Unpickler.find_class()``.
        """
        renamed_module = module
        if renamed_module == 'cube_fil_finder.structs.mask_obj_node' \
                or renamed_module == 'cube_fil_finder.structs.mask_obj_node_tree':
            renamed_module = 'fil3d'
        return super(PreV001Unpickler, self).find_class(renamed_module, name)


def pre_v001_pickle_load(file_obj, encoding='latin1', **kwargs):
    """ Override of pickle.load() for unpickling very old structs

    This creates an instance of PreV001Unpickler that has an updated find_class() to fix any potential import issues
    while unpickling.

    Made possible by https://stackoverflow.com/a/53327348.

    :param file_obj: See ``pickle.load()``.

    :param encoding: For some reason old 2.7 pickles of structs (at least the ones I had on hand) were made with \
    'latin1' encoding (and not the 'ASCII' default of 3.7) so this by defaults selects 'latin1'.

    :param kwargs: See ``pickle.load()``.

    :return: See ``pickle.load()``.
    """
    return PreV001Unpickler(file_obj, encoding=encoding, **kwargs).load()


def check_node_b_cutoff(node, hdr, b_cutoff=30):
    """checks if the node is within the b_cutoff range
    Arguments:
        node {mask_node} -- node obj
        hdr {fits.header} -- slice/cube FITS header
    Keyword Arguments:
        b_cutoff {int} -- latitude cutoff (default: {30})
    Returns:
        bool -- true if within cutoff, false if not
    """
    ys = [node.corner_min[0], node.corner_max[0]]
    xs = [node.corner_min[1], node.corner_max[1]]

    ras, decs = cube_util.index_to_radec(xs, ys, hdr)
    ls, bs = cube_util.radecs_to_lb(ras, decs)

    if bs[0] * bs[1] <= 0:
        return True

    if np.abs(bs[0]) >= b_cutoff and np.abs(bs[1]) >= b_cutoff:
        return False
    else:
        return True


def get_node_plot_corners(node):
    """gets the x y plot corners for matplotlib
    Arguments:
        node {mask_node} -- node obj
    """
    return [node.corner_min[0], node.corner_max[1], node.corner_min[1], node.corner_max[1]]
