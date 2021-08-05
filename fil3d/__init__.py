"""

"""

__version__ = '0.1.0'

import logging

from fil3d.structs import MaskObjNode
from fil3d.structs import MaskObjNodeTree

from fil3d import _const
from fil3d.galfa import galfa_const

if _const.X_STEPS is None:
    logging.warning('Setting default X_STEPS, import `fil3d._const` to modify `fil3d._const.X_STEPS`')
    _const.X_STEPS = galfa_const.GALFA_X_STEPS

if _const.Y_STEPS is None:
    logging.warning('Setting default Y_STEPS, import `fil3d._const` to modify `fil3d._const.Y_STEPS`')
    _const.Y_STEPS = galfa_const.GALFA_Y_STEPS
