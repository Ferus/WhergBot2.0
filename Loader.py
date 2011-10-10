# (c) Proxy of KOS-MOS Productions
# Official IRC channel: irc.datnode.net/#KOS-MOS
# Official repository on github: https://github.com/proxypoke/KOS-MOS_IRC_Bot
#
# This program is part of the KOS-MOS IRC Bot,
# hereafter called "KOS-MOS", and
# is Free Software under the terms of the 
# GNU General Public License, which can be found at
# http://www.gnu.org/copyleft/gpl.html

import os
import glob

def load(folder):
    '''A generic module loader that imports all python modules from a
    given folder. It assumes that folder is a package.
    Currently this only supports python source files (.py), compiled or
    optimized python files won't be loaded.

    Arguments:
        folder -- A folder that represents a package.

    Returns:
        A dictionary of {module_name : loaded_module}.
    '''
    # Appends the OS specific seperator to the path if it is missing
    if not folder.endswith(os.sep):
        folder += os.sep

    # Makes a list of all files in the folder which end with .py
    files = [file_ for file_ in glob.glob("{0}*.py".format(folder))]

    modules = []
    for file_ in files:
        # Reformats the filepath into a python module path
        path = file_[:-3].replace(os.sep, ".")
        # gtfo __init__
        if path.endswith("__init__"):
            continue
        modules.append(path)

    imported = {}
    for path in modules:
        # The module name only
        module = path[len(folder):]
        # Abuses __import__. Don't do this kids, mkay?
        try:
            imported[module] = __import__(path, {}, {},
                [module])
        except Exception as e:
            print("=================================")
            print("An error occured trying to import {0}:"
                    .format(module))
            print(repr(e))
            print("Ignored. Fix this shit bro.")
            print("Moving on...")
            print("=================================")

    return imported
