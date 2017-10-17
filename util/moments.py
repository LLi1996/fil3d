"""

Moments, orientations, and roundness

LL2017
"""

import numpy as np
import math


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
    x_bar, y_bar = image_centroid(mask)
    theta_1, theta_2, roundness = image_orientation(mask)
    return x_bar, y_bar, theta_1, theta_2, roundness


def get_mask_node_orientation_info(mask_node):
    x_bar, y_bar, theta_1, theta_2, roundness = get_mask_orientation_info(mask_node.mask)
    x_bar = x_bar + mask_node.corner_BL[0]
    y_bar = y_bar + mask_node.corner_BL[1]
    return x_bar, y_bar, theta_1, theta_2, roundness


def get_tree_mask_orientation_info(tree):
    x_bar, y_bar, theta_1, theta_2, roundness = get_mask_node_orientation_info(tree.root_node)
    return x_bar, y_bar, theta_1, theta_2, roundness
