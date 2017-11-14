'''
tree visualization lib
'''

import numpy as np
import matplotlib.pyplot as plt
from cube_fil_finder.util import moments
from cube_fil_finder.structs import mask_obj_node as maskNode
from cube_fil_finder.galfa import galfa_const


def vis_tree_shadow(tree, tree_name, save_fig=False, save_dir=None, save_name=None):
    '''
    Arguments:
        tree {[type]} -- [description]
        tree_name {[type]} -- [description]

    Keyword Arguments:
        save_fig {bool} -- [description] (default: {False})
        save_dir {[type]} -- [description] (default: {None})
        save_name {[type]} -- [description] (default: {None})
    '''

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

    pass


def vis_mask_node_moments(mask_node, mask_name, save_fig=False, save_dir=None,
                          save_name=None, figsize=None):

    if save_fig and save_name is None:
        save_name = mask_name
    if figsize is None or type(figsize) is not tuple or len(figsize) != 2:
        figsize = (10, 10)

    mask = mask_node.mask

    plot_corners = maskNode.get_node_plot_corners(mask_node)

    x_bar, y_bar, theta_1, theta_2, roundness = moments.get_mask_node_orientation_info(mask_node)

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111)

    ax.imshow([[], []], extent=plot_corners, origin='lower', cmap='gray')
    ax.contour(mask, colors='black', extent=plot_corners)

    theta_1_scale = np.sqrt(mask_node.mask_size) / 2
    theta_2_scale = theta_1_scale * roundness

    ax.plot([x_bar - theta_1_scale * np.cos(theta_1), x_bar + theta_1_scale * np.cos(theta_1)],
            [y_bar - theta_1_scale * np.sin(theta_1), y_bar + theta_1_scale * np.sin(theta_1)], color='red')
    ax.plot([x_bar - theta_2_scale * np.cos(theta_2), x_bar + theta_2_scale * np.cos(theta_2)],
            [y_bar - theta_2_scale * np.sin(theta_2), y_bar + theta_2_scale * np.sin(theta_2)], color='green')

    fig.suptitle(mask_name)
    ax.set_title('Mask Axis of Min/Max Image Second Moments (Roundness: {0:.5f})'.format(roundness))

    if save_fig:
        fig.savefig(save_dir + save_name)

    plt.clf()


def vis_mask_tree_moment(mask_tree, tree_name, save_fig=False, save_dir=None,
                         save_name=None, figsize=None):
    root_mask_node = mask_tree.root_node
    vis_mask_node_moments(root_mask_node, tree_name, save_fig=save_fig,
                          save_dir=save_dir, save_name=save_name, figsize=figsize)
    pass #WIP


def vis_mask_sky_dist(mask_node, mask_name, save_fig=False, save_dir=None, save_name=None, verbose=False):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.imshow([[], []], extent=[0, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS], origin='lower')

    this_mask = mask_node.mask
    this_plot_corners = [mask_node.corner_BL[0], mask_node.corner_TR[0],
                         mask_node.corner_BL[1], mask_node.corner_TR[1]]
    ax.contour(this_mask, colors='r', extent=this_plot_corners)

    ax.set_title('{0} Sky Position'.format(mask_name))

    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    plt.clf()


def vis_all_trees_sky_dist(trees, trees_name, save_fig=False, save_dir=None, save_name=None, verbose=False):
    """Plots all the masks in the trees dict at their
    Arguments:
        trees {dict} -- of maskTrees
        trees_name {str} -- of tree batch
    Keyword Arguments:
        save_fig {bool} -- [description] (default: {False})
        save_dir {[type]} -- [description] (default: {None})
        save_name {[type]} -- [description] (default: {None})
        verbose {bool} -- [description] (default: {False})
    """
    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.imshow([[], []], extent=[0, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS], origin='lower')

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

    plt.clf()
