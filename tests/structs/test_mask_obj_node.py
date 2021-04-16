"""

"""

import pickle

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
     tests.abs_path_from_project_root('data/testing/unpickle/node_c_py2.pickle'))])
def test_unpickling(v001_pickle_path, pre_v001_py2_pickle_path):
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
