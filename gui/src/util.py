"""
code from : https://github.com/ussserrr/pid-controller-gui/blob/master/pid-controller-gui/util.py
util.py - utility things for all other modules


function resource_path
    routine to correct a given path to some resource in accordance to whether the program is running in frozen mode or
    not (see https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile)
"""

import os
import sys


def resource_path(relative_path: str) -> str:
    """
    Use it to correct a given path to some resource in accordance to whether the program is running in frozen mode or
    not. Wrap an every request for a local file by this function to be able to run the script both in normal and bundle
    mode without any changes (see https://stackoverflow.com/questions/7674790)

    :param relative_path: string representing some relative path
    :return: appropriate path
    """

    if hasattr(sys, '_MEIPASS'):
        if relative_path[:2] == '..':
            # remove parent directory identifier
            return os.path.join(sys._MEIPASS, relative_path[3:])
        else:
            return os.path.join(sys._MEIPASS, relative_path)

    return relative_path
