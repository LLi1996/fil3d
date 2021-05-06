"""

"""

import os

import pathlib

project_root_dir = str(pathlib.Path(__file__).parent.parent.absolute())

def abs_path_from_project_root(path):
    if path[0] == '/':
        path = path[1:]
    return os.path.join(project_root_dir, path)
