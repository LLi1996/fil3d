"""

"""

__version__ = '0.1.0'

import logging

from fil3d.structs import MaskObjNode
from fil3d.structs import MaskObjNodeTree

from fil3d import _const
from fil3d.galfa import galfa_const

if _const.NAXIS_X is None:
    logging.warning('Setting default NAXIS_X, import `fil3d._const` to modify `fil3d._const.NAXIS_X`')
    _const.NAXIS_X = galfa_const.GALFA_X_STEPS

if _const.NAXIS_Y is None:
    logging.warning('Setting default NAXIS_Y, import `fil3d._const` to modify `fil3d._const.NAXIS_Y`')
    _const.NAXIS_Y = galfa_const.GALFA_Y_STEPS

if _const.CDELT_V is None:
    _const.CDELT_V = galfa_const.GALFA_W_SLICE_SEPARATION
