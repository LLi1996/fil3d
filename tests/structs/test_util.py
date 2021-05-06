"""

"""

import pytest

import tests
from fil3d import MaskObjNode
from fil3d.structs import util


@pytest.mark.parametrize('pre_v001_py2_pickle_path', [
    tests.abs_path_from_project_root('data/testing/unpickle/node_a_py2.pickle'),
    tests.abs_path_from_project_root('data/testing/unpickle/node_b_py2.pickle'),
    tests.abs_path_from_project_root('data/testing/unpickle/node_c_py2.pickle')])
def test_pre_v001_pickle_load_nodes(pre_v001_py2_pickle_path):
    obj = util.pre_v001_pickle_load(open(pre_v001_py2_pickle_path, 'rb'))
    assert isinstance(obj, MaskObjNode)
