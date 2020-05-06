#pylint: disable=invalid-name

import argparse
import datetime as dt
import os

import yaml

def file_exists(arg):

    ''' Checks whether a file exists, and returns the path if it does. '''

    if not os.path.exists(arg):
        msg = f'{arg} does not exist!'
        raise argparse.ArgumentTypeError(msg)

    return arg

def load_config_section(arg):

    '''
    Checks whether the config file exists and if it contains the input
    section. Returns the config as a Python dict.
    '''

    if len(arg) > 2:
        msg = f'{len(arg)} arguments were provided for config. Only 2 allowed!'
        raise argparse.ArgumentTypeError(msg)

    file_name = file_exists(arg[0])
    section_name = arg[1] if len(arg) == 2 else None

    # Load the YAML file into a dictionary
    with open(file_name, 'r') as fn:
        cfg = yaml.load(fn, Loader=yaml.Loader)

    err_msg = 'Section {section_name} does not exist in top level of {file_name}'
    if section_name:
        if isinstance(section_name, str):
            section_name = [section_name]

        # Support multi-layer configurations and single level
        for sect in section_name:
            try:
                cfg = cfg[sect]
            except KeyError:
                try:
                    cfg = cfg[sect.lower()]
                except:
                    raise KeyError(err_msg.format(section_name=sect, file_name=file_name))

    return [cfg, section_name]

def load_config_file(arg):

    '''
    Check to ensure that the provided config file exists. If it does, load it
    with YAML's safe loader and return the corresponding Python dict.
    '''

    # Check for existence of file
    arg = file_exists(arg)

    # Load the yaml config and return the Python dict
    with open(arg, 'r') as fn:
        ret = yaml.safe_load(fn)

    return ret

def load_str(arg):

    ''' Load a dict string safely using YAML. Return the resulting dict.  '''

    return yaml.load(arg, Loader=yaml.SafeLoader)


def to_datetime(arg):

    ''' Return a datetime object from input in the form YYYYMMDDHH[mm[ss]]. '''

    arg_len = len(arg)

    if arg_len not in [10, 12, 14]:
        msg = f'{arg} does not conform to input format YYYYMMDDHH[MM[SS]]'
        raise argparse.ArgumentTypeError(msg)

    # Use a subset of the string corresponding to the input length of the string
    # 2 chosen here since Y is a 4 char year.
    date_format = '%Y%m%d%H%M%S'[0:arg_len-2]

    return dt.datetime.strptime(arg, date_format)
