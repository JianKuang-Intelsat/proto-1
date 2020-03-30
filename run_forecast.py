import os

import argparse
import yaml

import checks


def parse_args():

    parser = argparse.ArgumentParser(
        description='Run a Forecast'
    )

    parser.add_argument('-c', '--config',
                        help='Full path to a YAML user config file, and a \
                        top-level section to use (optional).',
                        nargs='*',
                        type=checks.load_config,
                        )

    parser.add_argument('-d', '--start_date',
                        help='The forecast start time in YYYYMMDDHH[mm[ss]]
                        format',
                        required=True,
                        type=checks.to_datetime,
                        )

    return parser.parse_args()

def main():
    pass

if __name__ == '__main__'():
    cla = parse_args()
    main(cla)
