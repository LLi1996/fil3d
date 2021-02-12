"""

Moments, orientations, and roundness

LL2017
"""

import numpy as np
import math

ROUNDNESS_AR_CONVERSION = {
    '1_2': 0.25,
    '1_4': 0.0625,
    '1_6': 0.027555027555027554,
    '1_8': 0.015624015624015624,
    '1_9': 0.012345776558419324,
    '1_10': 0.01,
    '1_11': 0.0082645283791947348,
    '1_12': 0.0069444996141874256,
    '1_13': 0.0059172068204821496,
    '1_14': 0.005102081424401053,
    '1_16': 0.0039680039680039681
}


def image_moment(data, i_order, j_order, i_bar=None, j_bar=None):
    """Finds the i_th, j_th image moment
    Taken from https://alyssaq.github.io/2015/computing-the-axes-or-orientation-of-a-blob/ with improvements
    Arguments:
        data {np.array} -- 2d binary np array
        i_order {int} -- i_th order of moment
        j_order {int} -- j_th order of moment
    Keyword Arguments:
        i_bar {int} -- i center of mass (default: {None})
        j_bar {int} -- j center of mass (default: {None})
    """
    nrows, ncols = data.shape
    y_indices, x_indicies = np.mgrid[:nrows, :ncols]

    if i_bar is not None:
        x_indicies = x_indicies - i_bar
    if j_bar is not None:
        y_indices = y_indices - j_bar

    return (data * x_indicies**i_order * y_indices**j_order).sum()


def image_centroid(data):
    """Calculates image centroid
    Arguments:
        data {np.array} -- 2d binary np array
    Returns:
        {int}, {int} -- x_bar, y_bar
    """
    x_bar = image_moment(data, 1, 0) / image_moment(data, 0, 0)
    y_bar = image_moment(data, 0, 1) / image_moment(data, 0, 0)

    return x_bar, y_bar


def image_roundness(a, b, c, theta_1):
    """Calculates image roundness
    Defined as E_min / E_max where E is the second moment with respect to an axis
    Arguments:
        a {int} -- x^2 moment
        b {int} -- 2 * xy moment
        c {int} -- y^2 moment
        theta_1 {float} -- radian of axis of least second moment
    Returns:
        {float} -- roundness
    """
    def get_E(a, b, c, theta):
        """Calculates E
        Standard definition
        """
        return a * np.sin(theta) ** 2 - b * np.sin(theta) * np.cos(theta) + c * np.cos(theta) ** 2

    return get_E(a, b, c, theta_1) / get_E(a, b, c, theta_1 + np.pi / 2)


def image_orientation(data, calculate_roundness=True, degrees=False):
    """Calculates image orientation and roundness
    Arguments:
        data {np.array} -- 2d binary array
    Keyword Arguments:
        calculate_roundness {bool} -- return roundness (default: {True})
        degrees {bool} -- return theta in degrees (instead of radians) (default: {False})
    Returns:
        {float}, {float}, {float} -- theta_1 (axis of min E), theta_2 (axis of max E), roundness
    """
    x_bar, y_bar = image_centroid(data)

    a = image_moment(data, 2, 0, i_bar=x_bar, j_bar=y_bar)
    b = 2 * image_moment(data, 1, 1, i_bar=x_bar, j_bar=y_bar)
    c = image_moment(data, 0, 2, i_bar=x_bar, j_bar=y_bar)

    theta_1 = math.atan2(b, a - c) / 2
    theta_2 = theta_1 + np.pi / 2

    roundness = None
    if calculate_roundness:
        roundness = image_roundness(a, b, c, theta_1)

    if degrees:
        theta_1 = np.degrees(theta_1)
        theta_2 = np.degrees(theta_2)

    return theta_1, theta_2, roundness


def get_mask_orientation_info(mask):
    """
    orientation info for a mask
    Arguments:
        mask {2D np.array} -- mask
    Returns:
        x_bar, y_bar, theta_1, theta_2, roundness
    """
    x_bar, y_bar = image_centroid(mask)
    theta_1, theta_2, roundness = image_orientation(mask)
    return x_bar, y_bar, theta_1, theta_2, roundness


def get_node_mask_orientation_info(node):
    """
    orientation info for a node
    Arguments:
        node {maskNode} -- node
    Returns:
        x_bar, y_bar, theta_1, theta_2, roundness
    """
    x_bar, y_bar, theta_1, theta_2, roundness = get_mask_orientation_info(node.mask)
    y_bar = y_bar + node.corner_min[0]
    x_bar = x_bar + node.corner_min[1]
    return x_bar, y_bar, theta_1, theta_2, roundness


def get_tree_mask_orientation_info(tree):
    """
    orientation info for a tree
    Arguments:
        tree {maskTree} -- tree
    Returns:
        x_bar, y_bar, theta_1, theta_2, roundness
    """
    x_bar, y_bar, theta_1, theta_2, roundness = get_node_mask_orientation_info(tree.root_node)
    return x_bar, y_bar, theta_1, theta_2, roundness


def get_node_mask_centroid(node):
    """ warapper for getting mask centroid from a node
    """
    x_bar, y_bar = image_centroid(node.mask)
    return x_bar, y_bar


def get_tree_mask_centroid(tree):
    """image centroid for a tree, used in tree -> l&b conversion
    Arguments:
        tree {maskTree} -- tree
    Return:
        x_bar, y_bar
    """
    return get_node_mask_centroid(tree.root_node)