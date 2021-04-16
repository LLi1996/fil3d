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

    assert_array_equal(node_v001.mask, node_pre_v001.mask)
    assert node_v001.corners_original == node_pre_v001.corners_original
    assert node_v001.v_slice_index == node_pre_v001.v_slice_index
    assert node_v001.visited == node_pre_v001.visited
    assert node_v001.mask_size == node_pre_v001.mask_size
    assert node_v001.masked_area_size == node_pre_v001.masked_area_size


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
    (np.asarray([[0, 0, 0], [1, 1, 1], [0, 1, 1], [0, 0, 0]], bool),
     [[1, 1], [5, 4]],
     0,
     12,
     5)
])
def test_MaskObjNode(mask, corners, v_index, expected_mask_size, expected_mask_area_size):
    """Simple test of object creation from mask, corners and v_index"""
    node = MaskObjNode(mask, corners, v_index)

    assert_array_equal(node.mask, mask)
    assert len(node.mask.shape) == 2
    assert node.mask.shape[0] == corners[1][0] - corners[0][0]
    assert node.mask.shape[1] == corners[1][1] - corners[0][1]
    assert node.corners_original == corners
    assert len(node.v_slice_index) == 1
    assert node.v_slice_index[0] == v_index
    assert not node.visited
    assert node.mask_size == expected_mask_size
    assert node.masked_area_size == expected_mask_area_size
