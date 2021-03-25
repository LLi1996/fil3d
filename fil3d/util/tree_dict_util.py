"""
matching and finding trees
outputting distribution for a dicts of trees
"""

import logging

import sys
import pickle
import numpy as np
from fil3d.structs import mask_obj_node as maskNode
from fil3d.structs import mask_obj_node_tree as maskTree
from fil3d.structs import util as struct_util
from fil3d.util import moments


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
        raise RuntimeError("Length of velocities and dictionaries don't match")

    continuous_tree_keys_set = set()
    # iterate through every velocity channel to match nodes
    for i in xrange(len(vs)):
        node_dict_path = dict_full_paths[i]
        nodes_in_v_slice = pickle.load(open(node_dict_path, 'rb'))

        logging.info("working on v slice % {0} ...".format(vs[i]))
        logging.debug("number of currently continuous trees: {0}".format(len(continuous_tree_keys_set)))

        # iterate through the nodes in descending order (by masked area)
        for k in struct_util.sorted_struct_dict_keys_by_area(nodes_in_v_slice.keys(), key_type='node'):
            current_node = nodes_in_v_slice[k]

            logging.debug("on node {}".format(k))

            # match and add node, if not matched, create new tree and add to dict of trees
            if not match_and_add_node_onto_tree(current_node, vs[i], trees, overlap_thresh,
                                                continuous_tree_keys_set=continuous_tree_keys_set):
                new_tree = maskTree.newTreeFromNode(current_node, verbose=verbose)
                struct_util.add_tree_to_dict(new_tree, trees)

        # keep the tree dict compact
        continuous_tree_keys_set = end_noncontinuous_trees(trees, vs[i])
        delete_short_dead_trees(trees)

        #del nodes_in_v_slice

    return trees


def match_and_add_node_onto_tree(node, v_index, trees, overlap_thresh, continuous_tree_keys_set=None):
    """
    matches a node to an existing tree in the set of trees

    Arguments:
        node {maskNode} -- node trying to be matched
        trees {dict} -- of trees
    Keyword Args:
        continuous_trees {set} -- of tree keys that have't ended
            for caching on matching
    Returns:
        True -- if the node as been matched
    """
    has_matched = False
    matches = 0
    matched_tree_keys = []

    logging.debug("matching node to trees ...")

    if not trees:
        logging.warn("no match found -- empty tree dict (this is fine during the first iteration)")
        return has_matched
    else:
        # iterate through the trees in descending order to match node
        if continuous_tree_keys_set is not None:
            logging.debug('using set of continuous tree keys for fast matching')
            keys = continuous_tree_keys_set
        else:
            logging.debug('no continuous tree keys set passed in - will attempt to match to all trees')
            keys = set(trees.keys())

        for k in struct_util.sorted_struct_dict_keys_by_area(keys, key_type='tree'):
            candidate_tree = trees[k]
            if candidate_tree.has_ended:
                continue
            else:
                # match and add node, if not matched continue
                last_node_on_candidate_tree = candidate_tree.getLastNode()
                candidate_tree_has_node_on_current_v_slice = last_node_on_candidate_tree.v_slice_index[0] == v_index
                if candidate_tree_has_node_on_current_v_slice:
                    # the tree has already been matched with a node on this velocity channel
                    # in this case the last_node_on_candidate_tree isn't the node we want to match to (since that'll be on the
                    # current velocity slice, and we want to match to the node that was before that
                    candidate_node = candidate_tree.getNode(candidate_tree.length - 2)
                else:
                    # if not then we just match to the last_node_on_candidate_tree
                    candidate_node = last_node_on_candidate_tree

                if candidate_node.check_mask_overlap(node, overlap_thresh):
                    node.visited = True
                    has_matched = True
                    matches += 1
                    if candidate_tree_has_node_on_current_v_slice:
                        candidate_tree.addNodeOnSameVChannel(node)
                    else:
                        candidate_tree.addNodeOnNewVChannel(node)

                    logging.info("match found -- tree key: {0}".format(k))
                    matched_tree_keys.append(k)
                else:
                    continue

    if has_matched:
        logging.info("found {0} matches in total".format(matches))
        if matches > 1:
            new_key = back_merge_trees(trees, matched_tree_keys)
            if continuous_tree_keys_set is not None:
                # updates the set by removing the old keys and adding the new key back
                for old_key in matched_tree_keys:
                    continuous_tree_keys_set.discard(old_key)
                continuous_tree_keys_set.add(new_key)

    else:
        logging.info("no match found -- searched through tree dict")

    return has_matched


def back_merge_trees(trees, tree_keys_to_back_merge):
    """

    :param trees:
    :param tree_keys_to_back_merge:
    :return:
    """
    if len(tree_keys_to_back_merge) < 2:
        raise RuntimeError('tree_keys_to_back_merge needs at least two keys')

    logging.info('back merging trees: {0}'.format(tree_keys_to_back_merge))

    # this is the base tree that we'll merge onto
    tree = struct_util.pop_tree_from_dict(tree_keys_to_back_merge[0], trees)
    for i, k in enumerate(tree_keys_to_back_merge):
        if i != 0:  # iteratively back merge the other trees into the base tree
            other_tree = struct_util.pop_tree_from_dict(k, trees)
            tree = maskTree.back_merge_trees(tree, other_tree)

    # add the back-merged tree back in
    key = struct_util.add_tree_to_dict(tree, trees)
    logging.info('new key for the back-merged tree: {0}'.format(key))
    return key


def end_noncontinuous_trees(trees, current_v):
    """
    Will
    1) Ends the trees that have not matched in this velocity slice &
    2) returns the set of tree keys that are still continuous

    Trees will be modified in place.

    :param trees: {dict}
        of trees

    :param current_v: {int}
        the velocity slice that just finished matching

    :return: {Set[str]}
    """
    logging.info('ending trees that are non-continuous ...')
    continuous_trees = set()
    for k in sorted(trees.keys()):
        if trees[k].has_ended:
            continue
        elif trees[k].root_v_slice + trees[k].length <= current_v:
            trees[k].has_ended = True
        else:
            continuous_trees.add(k)
    return continuous_trees


# size_cutoff was 2500
def delete_short_dead_trees(trees, length_cutoff=1, size_cutoff=None, verbose=False):
    """
    Delete all the trees that have length = 1 and have ended

    Arguments:
        tree_dict {dict} -- of trees
    """
    if size_cutoff is not None:
        logging.warning('will ignore size_cutoff input')

    bad_trees_keys = [k for k, v in trees.items() if v.has_ended and v.length <= length_cutoff]

    logging.info("deleting {0} trees that are short (length <= {1}) & are non-continuous ..."
                 .format(len(bad_trees_keys), length_cutoff))

    for k in bad_trees_keys:
        del trees[k]
    return trees


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
        logging.info("\t\t deleting %d trees that don't fit the criteria" % len(bad_trees_keys))

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


def is_point_on_node(node, point=(0, 0), strict=False):
    """
    checks if point is on a node

    :param node: {MaskObjNode}
    :param coord: {tup}/{list} (default: (0,0))
        of two {int}
        assumes in (i, j)
    :param strict: {bool} (default: False)
        if strict the binary mask needs to be ON at that point
        of not will return True if point in corner bound

    :return: {bool}
    """
    mask = node.mask
    corner_min = node.corner_min
    corner_max = node.corner_max
    in_corner_bound = ((corner_min[0] <= point[0]) and (point[0] <= corner_max[0]) and
                       (corner_min[1] <= point[1]) and (point[1] <= corner_max[1]))
    if in_corner_bound:
        if not strict:
            return True
        else:
            localized_point = [point[i] - corner_min[i] for i in range(2)]
            return bool(mask[localized_point[0], localized_point[1]])
    else:
        return False


def find_nodes_on_point(nodes_dicts, point=(0, 0), strict=False):
    """
    :param nodes_dicts: {dict}
        of {dict} of nodes
    :param point: {tup}/{list}
        of two {int}
        assumes in (i, j)
    :param strict: {bool} (default: False)
        if strict the binary mask needs to be ON at that point
        of not will return True if point in corner bound
    :return nodes_dicts: {dict}
    """
    new_nodes_dicts = dict()
    for nodes_dict_key, nodes_dict in nodes_dicts.items():
        new_nodes_dict = {node_key: node
                          for node_key, node in nodes_dict.items()
                          if is_point_on_node(node, point, strict=strict)}
        new_nodes_dicts[nodes_dict_key] = new_nodes_dict

    return new_nodes_dicts


def find_trees_on_point(trees_dict, point=(0, 0), strict=False):
    """
    :param trees_dict: {dict}
        of {dict} of trees
    :param point: {tup}/{list}
        of two {int}
        assumes in (i, j)
    :param strict: {bool} (default: False)
        if strict the binary mask needs to be ON at that point
        of not will return True if point in corner bound
    :return nodes_dicts: {dict}
    """
    new_trees_dict = dict()
    for tree_key, tree in trees_dict.items():
        root_node = tree.root_node
        if is_point_on_node(root_node, point, strict=strict):
            new_trees_dict[tree_key] = tree

    return new_trees_dict