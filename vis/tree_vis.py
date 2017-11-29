'''
tree visualization lib
'''

import numpy as np
import matplotlib.pyplot as plt
from cube_fil_finder.util import moments
from cube_fil_finder.structs import mask_obj_node as maskNode
from cube_fil_finder.galfa import galfa_const
from cube_fil_finder.vis import node_vis


def vis_tree_shadow(tree, tree_name, save_fig=False, save_dir=None, save_name=None):
    """tree mask contour
    Arguments:
        tree {maskTree} -- tree
        tree_name {str} -- name of tree
    Keyword Arguments:
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
    """

    root = tree.root_node
    starting_v = tree.root_v_slice
    length = tree.length

    assert(tree.has_ended)

    plot_corners = maskNode.get_node_plot_corners(root)

    if save_fig and save_name is None:
        save_name = tree_name

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.imshow([[], []], extent=plot_corners)
    ax.contour(root.mask, colors='r', extent=plot_corners)

    fig.suptitle(tree_name)
    ax.set_xlabel('tree length: {0}'.format(length))

    if save_fig:
        fig.savefig(save_dir + save_name)

    plt.clf()


def vis_tree_stack(tree, tree_name, save_fig=False, save_dir=None, save_name=None):
    """
    Arguments:
        tree {[type]} -- [description]
        tree_name {[type]} -- [description]

    Keyword Arguments:
        save_fig {bool} -- [description] (default: {False})
        save_dir {[type]} -- [description] (default: {None})
        save_name {[type]} -- [description] (default: {None})
    """
    # WIP
    pass


def vis_tree_mask_moment(mask_tree, tree_name, save_fig=False, save_dir=None,
                         save_name=None, figsize=None, return_fig=False):
    """tree mask contour with axis of least 2nd moment
        calls vis_node_mask_moments on the root node of tree
    Arguments:
        mask_tree {maskTree} -- tree
        tree_name {str} -- name of tree
    Keyword Arguments:
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
        figsize {tuple of ints (x,y)} -- (default: {None})
        return_fig {bool} -- (default: {False})
    """
    root_mask_node = mask_tree.root_node
    return node_vis.vis_node_mask_moments(root_mask_node, tree_name, save_fig=save_fig,
                                          save_dir=save_dir, save_name=save_name,
                                          figsize=figsize, return_fig=return_fig)


def vis_roundness_histogram(roundness_list, list_name, save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
    """roundness histogram from list of roundness measurement
    Arguments:
        roundness_list {np.array} -- of roundness measurement
        list_name {str} -- name of the roundness list for identification
    Keyword Arguments:
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
        verbose {bool} -- (default: {False})
        return_fig {bool} -- (default: {False})
    
    Returns:
        [type] -- [description]
    """
    fig = plt.figure(figsize=(15, 5))
    ax1 = fig.add_subplot(111)

    roundness_range = np.linspace(0, 1, 101)
    r_cnt, r_bin, _ = ax1.hist(roundness_list, roundness_range, color='grey')

    # lines of 1:2, 1:4, 1:8, 1:16
    ax1.plot([moments.ROUNDNESS_AR_CONVERSION['1_2'], moments.ROUNDNESS_AR_CONVERSION['1_2']],
             [0, np.max(r_cnt)], color='red')
    ax1.plot([moments.ROUNDNESS_AR_CONVERSION['1_4'], moments.ROUNDNESS_AR_CONVERSION['1_4']],
             [0, np.max(r_cnt)], color='red')
    ax1.plot([moments.ROUNDNESS_AR_CONVERSION['1_8'], moments.ROUNDNESS_AR_CONVERSION['1_8']],
             [0, np.max(r_cnt)], color='red')
    ax1.plot([moments.ROUNDNESS_AR_CONVERSION['1_16'], moments.ROUNDNESS_AR_CONVERSION['1_16']],
             [0, np.max(r_cnt)], color='red')

    ax1.set_xlabel('Roundness')
    ax1.set_ylabel('Count')
    ax1.set_title(list_name)

    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()


def vis_trees_sky_dist(trees, trees_name, save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
    """Plots all the masks in the trees dict at their
    Arguments:
        trees {dict} -- of maskTrees
        trees_name {str} -- of tree batch
    Keyword Arguments:
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
        verbose {bool} -- (default: {False})
    """
    fig = plt.figure(figsize=(14, 2))
    ax = fig.add_subplot(111)

    ax.imshow([[], []], extent=[0, galfa_const.GALFA_Y_STEPS, 0, galfa_const.GALFA_X_STEPS], origin='lower')

    for key in trees:
        this_node = trees[key]
        this_mask = this_node.root_node.mask
        this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                             this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
        ax.contour(this_mask, colors='r', extent=this_plot_corners)

    ax.set_title('{0} Sky Distribution'.format(trees_name))

    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()
