import os

import argparse

import checks
from forecast import Forecast
import utils


def parse_args():

    parser = argparse.ArgumentParser(
        description='Run a Forecast.'
    )

    # Required
    parser.add_argument('-c', '--user_config',
                        help='Full path to a YAML user config file, and a \
                        top-level section to use (optional).',
                        required=True,
                        type=checks.load_config_file,
                        )

    parser.add_argument('-d', '--start_date',
                        help='The forecast start time in YYYYMMDDHH[mm[ss]] \
                        format',
                        required=True,
                        type=checks.to_datetime,
                        )

    # Optional - configure files
    parser.add_argument('-g', '--grid_config',
                        help='Full path to a YAML grids config file, and a \
                        grid name corresponding to the top-level key of \
                        the YAML file.',
                        nargs=2,
                        type=checks.load_config_section,
                        )

    parser.add_argument('-m', '--machine_config',
                        help='Full path to a YAML machines config file, and a \
                        machine to use: Hera, WCOSS, Jet, etc.',
                        nargs=2,
                        type=checks.load_config_section,
                        )

    parser.add_argument('-n', '--nml_config',
                        help='Full path to a YAML namelist config file, and a \
                        top-level section to use (optional).',
                        nargs=2,
                        type=checks.load_config_section,
                        )

    parser.add_argument('-s', '--script_config',
                        help='Full path to a YAML script config file',
                        type=checks.load_config_file,
                        )

    parser.add_argument('--overwrite',
                        action='store_true',
                        help='If included, overwrites the current working \
                        directory. Otherwise, exits on existence of workdir',
                        )

    # Optional - switches
    parser.add_argument('--dry-run',
                        action='store_true',
                        dest='dry_run',
                        help='Set up a run directory, but don\'t run the \
                        executable.',
                        )

    parser.add_argument('--quiet',
                        action='store_true',
                        help='Suppress all output.',
                        )


    return parser.parse_args()

def main(cla):

    # Load the user-defined settings, and script settings
    # ----------------------------------------------------
    user_config = cla.user_config

    print(f"user config: {user_config}")
    script_config = cla.script_config
    print(f"script config: {script_config}")
    if not script_config:
        ushdir = os.path.join(user_config['paths']['homerrfs'], 'configs')
        script_config = checks.load_config_file(
            os.path.join(ushdir, 'fv3_script.yml')
            )

    # Update script config with user-supplied config file
    # ----------------------------------------------------
    utils.update_dict(script_config, user_config)

    # Create Namespace of config for easier syntax
    # ---------------------------------------------
    config = argparse.Namespace()
    utils.namespace(config, script_config)

    # Now config and script_config contain identical information in Namespace
    # and dict formats, respectively.

    # Load each of the standard YAML config files
    # --------------------------------------------
    #
    # Reminder:
    # checks.load_config_section(arg) takes a two-element list as it's input.
    #    arg = [file_name, section_name(s)]
    #
    grid = cla.grid_config
    if not grid:
        grid = checks.load_config_section([
            config.paths.grid.format(n=config),
            [config.grid_name, config.grid_gen_method],
            ])

    machine = cla.machine_config
    if not machine:
        machine_path = config.paths.machine.format(n=config)
        machine = checks.load_config_section([
            machine_path,
            config.machine,
            ])

    namelist = cla.nml_config
    if not namelist:
        namelist = checks.load_config_section([
            config.paths.namelist.format(n=config),
            config.phys_pkg,
            ])

    # Update each of the provided configure files with user-supplied settings
    # ------------------------------------------------------------------------
    for cfg in ['grid', 'machine', 'namelist']:
        utils.update_dict(locals()[cfg], script_config.get(cfg), quiet=cla.quiet)

    # Set up a kwargs dict for Forecast object
    # -----------------------------------------
    fcst_kwargs = {
        'grid': grid,
        'nml': namelist,
        'overwrite': cla.overwrite,
        }

    # Create the Forecast object
    # ---------------------------
    fcst = Forecast(
        config=config,
        machine=machine,
        starttime=cla.start_date,
        **fcst_kwargs,
        )

    # Run the forecast job
    # ---------------------
    fcst.run(dry_run=cla.dry_run)

if __name__ == '__main__':
    CLARGS = parse_args()
    main(CLARGS)
