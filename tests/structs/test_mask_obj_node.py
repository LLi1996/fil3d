"""

"""

import pickle

import numpy as np
import pytest
from numpy.testing import assert_array_equal

import tests
from fil3d import MaskObjNode
from fil3d.structs import util


@pytest.mark.parametrize('v001_pickle_path, pre_v001_py2_pickle_path', [
    (tests.abs_path_from_project_root('data/testing/unpickle/node_a.pickle'),
     tests.abs_path_from_project_root('data/testing/unpickle/node_a_py2.pickle')),
    (tests.abs_path_from_project_root('data/testing/unpickle/node_b.pickle'),
     tests.abs_path_from_project_root('data/testing/unpickle/node_b_py2.pickle')),
    (tests.abs_path_from_project_root('data/testing/unpickle/node_c.pickle'),
     tests.abs_path_from_project_root('data/testing/unpickle/node_c_py2.pickle'))
])
def test_unpickling(v001_pickle_path, pre_v001_py2_pickle_path):
    """Testing unpicking from pickles created in various points in time (from the same node)"""
    node_v001 = pickle.load(open(v001_pickle_path, 'rb'))
    node_pre_v001 = util.pre_v001_pickle_load(open(pre_v001_py2_pickle_path, 'rb'))

    assert isinstance(node_v001, MaskObjNode)
    assert isinstance(node_pre_v001, MaskObjNode)

    assert node_v001 == node_pre_v001


@pytest.mark.parametrize('pre_v001_py2_pickle_path', [
    tests.abs_path_from_project_root('data/testing/unpickle/node_a_py2.pickle'),
    tests.abs_path_from_project_root('data/testing/unpickle/node_b_py2.pickle'),
    tests.abs_path_from_project_root('data/testing/unpickle/node_c_py2.pickle')
])
def test_pre_v001_function_name_backwards_compatibility(pre_v001_py2_pickle_path):
    """Testing the function rename aliasing still works for pre v001 nodes"""
    node_pre_v001 = util.pre_v001_pickle_load(open(pre_v001_py2_pickle_path, 'rb'))

    assert node_pre_v001.checkMaskedAreaSize() == node_pre_v001.check_masked_area_size()
    assert node_pre_v001.checkAreaSize() == node_pre_v001.check_area_size()
    assert node_pre_v001.getDimentions() == node_pre_v001.get_dimensions()
    assert node_pre_v001.getAR() == node_pre_v001.get_ar()
    # todo add more to this backwards compatibility


@pytest.mark.parametrize('mask, corners, v_index, expected_mask_size, expected_mask_area_size', [
    (np.zeros((3, 6), bool),
     [[0, 0], [3, 6]],
     0,
     18,
     0),
    (np.ones((6, 4), bool),
     [[1, 3], [7, 7]],
     9,
     24,
     24),
    (np.asarray([[0, 0, 0],
                 [1, 1, 1],
                 [0, 1, 1],
                 [0, 0, 0]], bool),
     [[1, 1], [5, 4]],
     0,
     12,
     5),
    (np.asarray([[0, 0, 1],
                 [0, 0, 1]], bool),
     [[9, 8], [11, 11]],
     [10, 11],
     6,
     2)
])
def test_MaskObjNode(mask, corners, v_index, expected_mask_size, expected_mask_area_size):
    """Simple test of object creation from mask, corners and v_index"""
    node = MaskObjNode(mask, corners, v_index)

    assert_array_equal(node.mask, mask)
    assert len(node.mask.shape) == 2
    assert node.mask.shape[0] == corners[1][0] - corners[0][0]
    assert node.mask.shape[1] == corners[1][1] - corners[0][1]
    assert node.corners_original == corners
    if isinstance(v_index, list):
        assert node.v_slice_index == v_index
    else:
        assert len(node.v_slice_index) == 1
        assert node.v_slice_index[0] == v_index
    assert not node.visited
    assert node.mask_size == expected_mask_size
    assert node.masked_area_size == expected_mask_area_size


@pytest.mark.parametrize('node_a, node_b, is_equal', [
    (MaskObjNode(np.zeros((3, 6), bool), [[0, 0], [3, 6]], 0),
     MaskObjNode(np.zeros((3, 6), bool), [[0, 0], [3, 6]], 0),
     True),
    (MaskObjNode(np.zeros((3, 6), bool), [[0, 0], [3, 6]], 0),
     MaskObjNode(np.ones((6, 4), bool), [[1, 3], [7, 7]], 9),
     False)
])
def test___eq__(node_a, node_b, is_equal):
    assert (node_a == node_b) == is_equal


@pytest.mark.parametrize('node, other_node, corners_overlap', [
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     True),  # fully covered
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[2, 2], [4, 4]], 0),
     True),  # corners overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-5, 0], [-3, 2]], 0),
     False),  # up, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[5, 0], [7, 2]], 0),
     False),  # down, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, -4], [2, -2]], 0),
     False),  # left, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 10], [2, 12]], 0),
     False),  # right, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[3, 3], [5, 5]], 0),
     False),  # to bottom right, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-2, -2], [0, 0]], 0),
     False),  # to top left no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-2, 6], [0, 8]], 0),
     False),  # to top right, no overlap
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[7, -3], [9, -1]], 0),
     False)  # to bottom left no overlap
])
def test_check_corners_overlap(node, other_node, corners_overlap):
    assert node.check_corners_overlap(other_node) == corners_overlap


@pytest.mark.parametrize('node, other_node, new_corners', [
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[0, 0], [3, 3]]),
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-1, -1], [1, 1]], 0),
     [[-1, -1], [3, 3]]),
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-1, 7], [1, 9]], 0),
     [[-1, 0], [3, 9]]),
    (MaskObjNode(np.ones((3, 3), bool), [[0, 0], [3, 3]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[8, 0], [10, 2]], 0),
     [[0, 0], [10, 3]])
])
def test_match_corners(node, other_node, new_corners):
    assert node.match_corners(other_node) == new_corners


@pytest.mark.parametrize('node, new_corners, new_mask', [
    (MaskObjNode(np.zeros((3, 3), bool), [[3, 3], [6, 6]], 0),
     [[3, 3], [6, 6]],
     np.zeros((3, 3), bool)),
    (MaskObjNode(np.zeros((3, 3), bool), [[3, 3], [6, 6]], 0),
     [[2, 1], [7, 9]],
     np.zeros((5, 8), bool)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[0, 0], [3, 2]],
     np.asarray([[1, 1],
                 [1, 1],
                 [0, 0]], bool)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[0, 0], [2, 3]],
     np.asarray([[1, 1, 0],
                 [1, 1, 0]], bool)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[-1, 0], [2, 2]],
     np.asarray([[0, 0],
                 [1, 1],
                 [1, 1]], bool)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[0, -1], [2, 2]],
     np.asarray([[0, 1, 1],
                 [0, 1, 1]], bool)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     [[-1, -1], [3, 3]],
     np.asarray([[0, 0, 0, 0],
                 [0, 1, 1, 0],
                 [0, 1, 1, 0],
                 [0, 0, 0, 0]], bool))
])
def test_expand_mask(node, new_corners, new_mask):
    assert_array_equal(node.expand_mask(new_corners), new_mask)


@pytest.mark.parametrize('node, other_node, overlap_thresh, mask_overlap', [
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[2, 2], [4, 4]], 0),
     0,
     False),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     0.0,
     True),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     1.0,
     True),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[1, 1], [3, 3]], 0),
     .25,
     True),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[1, 1], [3, 3]], 0),
     .26,
     False),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((1, 1), bool), [[1, 1], [2, 2]], 0),
     .26,
     True),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((1, 1), bool), [[1, 1], [2, 2]], 0),
     1.0,
     True)
])
def test_check_mask_overlap(node, other_node, overlap_thresh, mask_overlap):
    assert node.check_mask_overlap(other_node, overlap_thresh) == mask_overlap


@pytest.mark.parametrize('node, other_node, result_node', [
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 1),
     MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], [0, 1])),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[1, 1], [3, 3]], 0),
     MaskObjNode(np.asarray([[1, 1, 0],
                             [1, 1, 1],
                             [0, 1, 1]], bool),
                 [[0, 0], [3, 3]], 0)),
    (MaskObjNode(np.ones((2, 2), bool), [[0, 0], [2, 2]], 0),
     MaskObjNode(np.ones((2, 2), bool), [[-2, -2], [0, 0]], 1),
     MaskObjNode(np.asarray([[1, 1, 0, 0],
                             [1, 1, 0, 0],
                             [0, 0, 1, 1],
                             [0, 0, 1, 1]], bool),
                 [[-2, -2], [2, 2]], [0, 1]))
])
def test_merge_node(node, other_node, result_node):
    node.merge_node(other_node)
    assert node == result_node
