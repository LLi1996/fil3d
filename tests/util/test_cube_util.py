"""

"""

import pytest
from astropy.io import fits

import tests
from fil3d.util import cube_util


@pytest.fixture
def sample_data_cube_and_header():
    return fits.getdata(
        tests.abs_path_from_project_root('data/testing/fits/test_cube.fits'),
        header=True)


def test_cube_transfer(sample_data_cube_and_header):
    data_cube, header = sample_data_cube_and_header
    ret = cube_util.cube_transfer(data_cube, header)
    print(ret)
