"""
contains all the functions related to processing a cube and parsing data

"""

import sys
import pickle
import numpy as np
from cube_fil_finder.structs import mask_obj_node as maskNode
from cube_fil_finder.structs import mask_obj_node_tree as maskTree
from cube_fil_finder.structs import util as struct_util
from cube_fil_finder.util import moments


def find_all_trees_from_slices(vs, dict_full_paths, overlap_thresh=.85, reverse_find=False, verbose=False):
    """
    find all the trees given a list of velocity and a list of dict names
    reverse find currently not implemented!

    Arguments:
        vs {list} -- of velocity slices
        dict_full_paths {dict} -- of paths to the pickled node dictionaries

    Keyword Arguments:
        overlap_thresh {number} -- [description] (default: {.85})
        reverse_find {bool} -- [description] (default: {False})
        verbose {bool} -- [description] (default: {False})
    """
    trees = {}

    if len(vs) != len(dict_full_paths):
        print("\n\nLength of velocities and dictionaries don't match")
        sys.exit()

    continuous_trees = set()
    # iterate through every velocity channel to match nodes
    for i in xrange(len(vs)):
        node_dict_path = dict_full_paths[i]
        nodes_in_v_slice = pickle.load(open(node_dict_path, 'rb'))

        if verbose:
            print("working on v slice %d..." % vs[i])
            print("continuous_trees: {0}".format(len(continuous_trees)))

        # iterate through the nodes in descending order (by masked area)
        for k in struct_util.sorted_struct_dict_keys_by_area(nodes_in_v_slice.keys(), key_type='node'):
            current_node = nodes_in_v_slice[k]

            if verbose:
                print("\ton mask {}".format(k))

            # match and add node, if not matched, create new tree and add to dict of trees
            if not match_and_add_node_onto_tree(current_node, vs[i], trees,
                                                overlap_thresh, continuous_trees=continuous_trees,
                                                verbose=verbose):
                new_tree = maskTree.newTreeFromNode(current_node, verbose=verbose)
                struct_util.add_tree_to_dict(new_tree, trees)

        # keep the tree dict compact
        continuous_trees = end_noncontinuous_trees(trees, vs[i])
        delete_short_dead_trees(trees, verbose=verbose)

        del nodes_in_v_slice

    return trees


def match_and_add_node_onto_tree(node, v_index, trees, overlap_thresh, continuous_trees=None, verbose=False):
    """
    matches a node to an existing tree in the set of trees

    Arguments:
        node {maskNode} -- node trying to be matched
        trees {dict} -- of trees
    Keyword Args:
        continuous_trees {set} -- of tree keys that have't ended
    Returns:
        True -- if the node as been matched
    """
    has_matched = False

    if verbose:
        print("\t\tmatching...")

    if not trees:
        print("\t\tno match found -- empty tree dict")
        return has_matched
    else:
        # iterate through the trees in descending order to match node
        keys = trees.keys() if continuous_trees is None else continuous_trees
        for k in struct_util.sorted_struct_dict_keys_by_area(keys, key_type='tree'):
            if continuous_trees is None and trees[k].has_ended:
                continue
            else:
                # match and add node, if not matched continue
                if trees[k].getLastNode().checkMaskOverlap(node, overlap_thresh):
                    node.visited = True
                    has_matched = True
                    if v_index == trees[k].getLastNode().v_slice_index[0]:
                        trees[k].getLastNode().combineMask(node, merge_type='OR')
                    #print(trees[k].root_node.mask.shape)
                    #print(trees[k].root_node.corners_original)
                    trees[k].addNode(node, verbose, new_channel=False)
                    #print(trees[k].root_node.mask.shape)
                    #print(trees[k].root_node.corners_original)
                    if verbose:
                        print("\t\tmatch found -- tree %s" % k)
                    return has_matched
                else:
                    continue

    if verbose:
        print("\t\tno match found -- searched through tree dict")
    return has_matched


def end_noncontinuous_trees(trees, current_v):
    """
    ends the trees that have not matched in this velocity slice
    Arguments:
        trees {dict} -- of trees
        current_v {int} -- the velocity slice that just finished matching
    """
    continuous_trees = set()
    for k in sorted(trees.keys()):
        if trees[k].has_ended:
            continue
        elif trees[k].root_v_slice + trees[k].length <= current_v:
            trees[k].has_ended = True
        else:
            continuous_trees.add(k)
    return continuous_trees


def delete_short_dead_trees(trees, length_cutoff=1, size_cutoff=2500, verbose=False):
    """
    delete all the trees that have length = 1 and have ended
    Arguments:
        tree_dict {dict} -- of trees
    """
    bad_trees_keys = []

    for k in trees:
        if trees[k].has_ended:
            if trees[k].getTreeMaskedArea2D() <= size_cutoff and trees[k].length <= length_cutoff:
                bad_trees_keys.append(k)

    if verbose:
        print("\tdeleting %d trees that are small & dead" % len(bad_trees_keys))

    for k in bad_trees_keys:
        del trees[k]


def prune_trees(all_trees, size_cut=30, length_cut=3, length_limit=36, verbose=False):
    pruned_trees = dict(all_trees)

    bad_trees_keys = []

    for k in pruned_trees:
        # cut length
        if pruned_trees[k].length >= length_limit or pruned_trees[k].length < length_cut:
            bad_trees_keys.append(k)
            continue

        # cut size
        if pruned_trees[k].getTreeMaskedArea2D() < size_cut:
            bad_trees_keys.append(k)
            continue

    if verbose:
        print "\t\t deleting %d trees that don't fit the criteria" % len(bad_trees_keys)

    for k in bad_trees_keys:
        del pruned_trees[k]

    return pruned_trees


def get_velocity_span_dist(all_trees):
    """
    return the lengths of the trees in velocity space
    Arguments:
        all_trees {dict} -- of trees

    Returns:
        {np.array} -- of lengths in velocity space
    """
    length_dist = []

    for k in all_trees:
        length_dist.append(all_trees[k].length)

    return np.array(length_dist)


def get_mask_size_dist(all_trees):
    """
    return the sizes (mask) of all the trees
    Arguments:
        all_trees {dict} -- of trees

    Returns:
        {np.array} -- of sizes (pixels^2)
    """
    size_dist = []

    for k in all_trees:
        size_dist.append(all_trees[k].root_node.masked_area_size)

    return np.array(size_dist)


def get_mask_box_ar_dist(all_trees):
    """
    return the aspect ratios of the all the boxes of the masks
    Arguments:
        all_trees {dict} -- of trees
    Returns:
        {np.array} -- of AR
    """
    ar_dist = []

    for k in all_trees:
        ar_dist.append(all_trees[k].getTreeAspectRatio())

    return np.array(ar_dist)


def get_mask_roundness_dist(trees):
    """
    return the roudnesses of all the masks of the trees
    Arguments:
        trees {dict} -- of trees
    Returns:
        {np.array} -- of roundness
    """
    roundness = []
    for k in trees:
        roundness.append(moments.get_tree_mask_orientation_info(trees[k])[4])
    return np.array(roundness)
