'''
tree visualization lib
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from cube_fil_finder.util import moments
from cube_fil_finder.structs import mask_obj_node as maskNode
from cube_fil_finder.galfa import galfa_const
from cube_fil_finder.galfa import galfa_util
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


def vis_trees_sky_dist(trees, trees_name, vis_galactic_lines=True,
                       save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
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

    for key in trees:
        this_node = trees[key]
        this_mask = this_node.root_node.mask
        this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                             this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
        ax.contour(this_mask, colors='r', extent=this_plot_corners)

    if vis_galactic_lines:
        for b in np.linspace(-90, 90, 7):
            xs, ys = galfa_util.lbs_to_galfa_index(range(0, 360), [b] * 360, remin=True)
            ax.plot(xs, ys, color='grey', alpha=.5)

    ax.imshow([[], []], extent=[0, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS], origin='lower')

    ax.set_title('{0} Sky Distribution'.format(trees_name))

    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()


def vis_trees_sky_dist_3_panels(trees, trees_name, vis_galactic_lines=True,
                                save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
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
    fig = plt.figure(figsize=(5, 7))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    axs = [ax1, ax2, ax3]

    for key in trees:
        this_node = trees[key]
        this_mask = this_node.root_node.mask
        this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                             this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
        for ax in axs:
            ax.contour(this_mask, colors='r', extent=this_plot_corners)

    if vis_galactic_lines:
        for b in np.linspace(-90, 90, 7):
            xs, ys = galfa_util.lbs_to_galfa_index(range(0, 360), [b] * 360, remin=True)
            for ax in axs:
                ax.plot(xs, ys, color='grey', alpha=.5)

    ax1.imshow([[], []],
               extent=[0, galfa_const.GALFA_X_STEPS / 3., 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')
    ax2.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3., galfa_const.GALFA_X_STEPS / 3. * 2, 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')
    ax3.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3. * 2, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')

    ax1.set_title('{0} Sky Distribution'.format(trees_name))

    fig.tight_layout()
    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()


def vis_trees_sky_dist_names_3_panels(trees, trees_name, vis_galactic_lines=True,
                                save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
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
    fig = plt.figure(figsize=(6, 7))
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    axs = [ax1, ax2, ax3]

    for key in trees:
        this_node = trees[key]
        this_mask = this_node.root_node.mask
        this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                             this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
        for ax in axs:
            ax.contour(this_mask, colors='red', extent=this_plot_corners, linewidths=.3)
            ax.text((this_node.root_node.corners[1][0] + this_node.root_node.corners[0][0]) / 2.,
                    (this_node.root_node.corners[1][1] + this_node.root_node.corners[0][1]) / 2.,
                    key, clip_on=True, fontsize=2)

    if vis_galactic_lines:
        for b in np.linspace(-90, 90, 7):
            xs, ys = galfa_util.lbs_to_galfa_index(range(0, 360), [b] * 360, remin=True)
            for ax in axs:
                ax.plot(xs, ys, color='grey', alpha=.5)

    hdr = galfa_const.MOCK_GALFA_HDR
    ytick_index = np.linspace(0, galfa_const.GALFA_Y_STEPS, 3)
    xtick_index = np.linspace(0, galfa_const.GALFA_X_STEPS, 10)
    for ax in axs:
        ax.set_yticks(ytick_index)
        ax.set_yticklabels(np.around((ytick_index - hdr['CRPIX2']) * hdr['CDELT2'] + hdr['CRVAL2']).astype(int))
        ax.set_xticks(xtick_index)
        ax.set_xticklabels(np.around((xtick_index - hdr['CRPIX1']) * hdr['CDELT1'] + hdr['CRVAL1']).astype(int))

    ax1.imshow([[], []],
               extent=[0, galfa_const.GALFA_X_STEPS / 3., 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')
    ax2.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3., galfa_const.GALFA_X_STEPS / 3. * 2, 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')
    ax3.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3. * 2, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS, ],
               origin='lower')

    ax1.set_title('{0} Sky Distribution'.format(trees_name))

    fig.tight_layout()
    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()


def vis_trees_sky_dist_color_range(trees, trees_name, color_by, color_map_name, fig_size=(15, 3),
                                   save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
    """Plots all the masks in the trees dict at their
    Arguments:
        trees {dict} -- of maskTrees
        trees_name {str} -- of tree batch
        color_by {dict} -- of values to color by. same keys as trees
        color_map_name {str} -- matplotlib color map
    Keyword Arguments:
        fig_size {tuple of ints} -- (default: {(15, 3)})
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
        verbose {bool} -- (default: {False})
    """
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_subplot(111)

    div_cmaps = set(['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                     'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic'])

    cmap = cm.get_cmap(color_map_name)
    c_norm_max = float(max(v for v in color_by.values() if v is not None))
    c_norm_min = float(min(v for v in color_by.values() if v is not None))
    if color_map_name in div_cmaps:
        print('in div')
        c_norm_max = max(abs(c_norm_max), abs(c_norm_min))
        c_norm_min = 0 - c_norm_max
    c_norm_range = c_norm_max - c_norm_min

    def norm_color_field_val(val):
        norm_val = (val - c_norm_min) / c_norm_range
        if norm_val >= 1:
            return 1.0
        if norm_val <= 0:
            return 0.0
        return norm_val

    ax.imshow([[], []], extent=[0, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS], origin='lower')

    for key in trees:
        if color_by[key] is None:
            continue
        else:
            this_color = cmap(norm_color_field_val(color_by[key]))
            this_node = trees[key]
            this_mask = this_node.root_node.mask
            this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                                 this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
            ax.contour(this_mask, colors=(this_color, ), extent=this_plot_corners)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=c_norm_min, vmax=c_norm_max))
    sm._A = []
    cbar = plt.colorbar(sm, ax=ax, orientation='horizontal')

    ax.set_title('{0} Sky Distribution'.format(trees_name))

    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()


def vis_trees_sky_dist_color_range_3_panels(trees, trees_name, color_by, color_map_name, vis_galactic_lines=True,
                                            fig_size=(7, 7), colorbar=True,
                                            save_fig=False, save_dir=None, save_name=None, verbose=False, return_fig=False):
    """Plots all the masks in the trees dict at their
    Arguments:
        trees {dict} -- of maskTrees
        trees_name {str} -- of tree batch
        color_by {dict} -- of values to color by. same keys as trees
        color_map_name {str} -- matplotlib color map
    Keyword Arguments:
        fig_size {tuple of ints} -- (default: {(15, 3)})
        save_fig {bool} -- (default: {False})
        save_dir {str} -- (default: {None})
        save_name {str} -- (default: {None})
        verbose {bool} -- (default: {False})
    """
    fig = plt.figure(figsize=fig_size)
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    axs = [ax1, ax2, ax3]

    div_cmaps = set(['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                     'RdYlGn', 'Spectral', 'Spectral_r', 'coolwarm', 'bwr', 'seismic'])

    cmap = cm.get_cmap(color_map_name)
    c_norm_max = float(max(v for v in color_by.values() if v is not None))
    c_norm_min = float(min(v for v in color_by.values() if v is not None))
    if color_map_name in div_cmaps:
        print('in div')
        c_norm_max = max(abs(c_norm_max), abs(c_norm_min))
        c_norm_min = 0 - c_norm_max
    c_norm_range = c_norm_max - c_norm_min

    def norm_color_field_val(val):
        norm_val = (val - c_norm_min) / c_norm_range
        if norm_val >= 1:
            return 1.0
        if norm_val <= 0:
            return 0.0
        return norm_val

    for key in trees:
        if key not in color_by or color_by[key] is None:
            continue
        else:
            this_color = cmap(norm_color_field_val(color_by[key]))
            this_node = trees[key]
            this_mask = this_node.root_node.mask
            this_plot_corners = [this_node.root_node.corner_BL[0], this_node.root_node.corner_TR[0],
                                 this_node.root_node.corner_BL[1], this_node.root_node.corner_TR[1]]
            for ax in axs:
                ax.contour(this_mask, colors=(this_color, ), extent=this_plot_corners)

    if vis_galactic_lines:
        for b in np.linspace(-90, 90, 7):
            xs, ys = galfa_util.lbs_to_galfa_index(range(0, 360), [b] * 360, remin=True)
            for ax in axs:
                ax.plot(xs, ys, color='grey', alpha=.5)

    hdr = galfa_const.MOCK_GALFA_HDR
    ytick_index = np.linspace(0, galfa_const.GALFA_Y_STEPS, 3)
    xtick_index = np.linspace(0, galfa_const.GALFA_X_STEPS, 10)
    for ax in axs:
        ax.set_yticks(ytick_index)
        ax.set_yticklabels(np.around((ytick_index - hdr['CRPIX2']) * hdr['CDELT2'] + hdr['CRVAL2']).astype(int))
        ax.set_xticks(xtick_index)
        ax.set_xticklabels(np.around((xtick_index - hdr['CRPIX1']) * hdr['CDELT1'] + hdr['CRVAL1']).astype(int))

    ax1.imshow([[], []],
               extent=[0, galfa_const.GALFA_X_STEPS / 3., 0, galfa_const.GALFA_Y_STEPS],
               origin='lower')
    ax2.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3., galfa_const.GALFA_X_STEPS / 3. * 2, 0, galfa_const.GALFA_Y_STEPS],
               origin='lower')
    ax3.imshow([[], []],
               extent=[galfa_const.GALFA_X_STEPS / 3. * 2, galfa_const.GALFA_X_STEPS, 0, galfa_const.GALFA_Y_STEPS],
               origin='lower')

    if colorbar:
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=c_norm_min, vmax=c_norm_max))
        sm._A = []
        for ax in axs:
            cbar = fig.colorbar(sm, ax=ax, aspect=10, fraction=.1, shrink=.9)

    ax1.set_title('{0} Sky Distribution'.format(trees_name))
    fig.tight_layout()
    if verbose:
        fig.show()

    if save_fig:
        fig.savefig(save_dir + save_name)

    if return_fig:
        return fig

    plt.clf()
