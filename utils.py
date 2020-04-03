# pylint: disable=invalid-name

from argparse import Namespace
import os
import shutil

import errors


def namespace(ns: Namespace, d: dict):

    ''' Creates a Namespace object ns in place for an arbitrarily deep input dictionary, d. '''

    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict):
                leaf_ns = Namespace()
                ns.__dict__[k] = leaf_ns
                namespace(leaf_ns, v)
            else:
                ns.__dict__[k] = v


def safe_copy(src, dst):

    # Check that src exists
    if not os.path.exists(src):
        raise errors.FileNotFound(src)

    # Check that dst path exists and is writeable
    dst_path = os.path.dirname(dst)
    if not os.path.exists(dst_path) and os.access(dst_path, os.W_OK):
        raise errors.PathNotFound(dst_path)

    shutil.copy2(src, dst)


def safe_link(src, dst):

    # Check that src exists
    if not os.path.exists(src):
        raise errors.FileNotFound(src)

    # Check that dst path exists and is writeable
    dst_path = os.path.dirname(dst)
    if not os.path.exists(dst_path) and os.access(dst_path, os.W_OK):
        raise errors.PathNotFound(dst_path)

    os.symlink(src, dst)

def update_dict(base, updates, quiet=False):
    '''
    Overwrites all values in base dictionary with values from updates. Turn off
    print statements with queit=True.

    Input:
        base      A dict that is to be updated.
        updates   A dict containing sections and keys corresponding to
                  those in base and potentially additional ones, that will be used to
                  update the base dict.
        quiet     An optional boolean flag to turn off output.

    Output:
        None

    Result:
        The base dict is updated in place.
    '''

    for sect, values in updates.items():
        # If section is set to None, remove all contents from namelist
        if values is None:
            base[sect] = {}
        else:
            for key, value in values.items():
                if not quiet:
                    print(f'Setting {sect}.{key} = {value}')

                # Remove key from dict if config is set to None
                if value is None:
                    _ = base[sect].pop(key, None)
                else:

                    try:
                        base[sect][key] = value
                    except KeyError:
                        # Namelist section did not exist. Create it and update the value.
                        base[sect] = {}
                        base[sect][key] = value
