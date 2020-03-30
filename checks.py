import argparse
import os

def config_exists(arg):

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
        cfg = yaml.load(fn, Loader=yaml.SafeLoader)

    if section_name:
        try:
            cfg = cfg[section_name]
        except KeyError:
            msg = f'Section {section_name} does not exist in top level of {file_name}'
            raise argparse.ArgumentTypeError(msg)

    return cfg

def file_exists(arg):

    ''' Checks whether a file exists, and returns the path if it does. '''

    if not os.path.exists(arg):
        msg = f'{arg} does not exist!'
        raise argparse.ArgumentTypeError(msg)

    return arg

def load_config(arg):

    '''
    Check to ensure that the provided config file exists. If it does, load it
    with YAML's safe loader and return the resulting dict.
    '''

    # Check for existence of file
    if not os.path.exists(arg):
        msg = f'{arg} does not exist!'
        raise argparse.ArgumentTypeError(msg)

    return yaml.safe_load(arg)

def load_str(arg):

    ''' Load a dict string safely using YAML. Return the resulting dict.  '''

    return yaml.load(arg, Loader=yaml.SafeLoader)


def to_datetime(arg):

    ''' Return a datetime object from input in the form YYYYMMDDHH[mm[ss]]. '''

    arg_len = len(arg)

    if arg_len not in [10, 12, 14]:
        msg = f'{value} does not conform to input format YYYYMMDDHH[MM[SS]]'
        raise argparse.ArgumentTypeError(msg)

    # Use a subset of the string corresponding to the input length of the string
    # 2 chosen here since Y is a 4 char year.
    date_format = '%Y%m%d%H%M%S'[0:val_len-2]

    return dt.datetime.strptime(value, date_format)
