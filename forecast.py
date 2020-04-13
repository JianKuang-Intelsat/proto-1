# pylint: disable=invalid-name,no-member,too-many-arguments

from argparse import Namespace
import os
import shlex
import shutil
import subprocess

import jinja2 as j2
import yaml

import f90nml

import errors
import utils

class BatchJob():

    def __init__(self, config, machine, starttime, **kwargs):

        self.config = self.config_namespace(config)
        self.machine = self.config_namespace(machine)
        self.starttime = starttime

        overwrite = kwargs.get('overwrite', False)
        self.workdir = self.create_workdir(overwrite)

    @staticmethod
    def config_namespace(config):

        ns = Namespace()
        utils.namespace(ns, config)
        return ns

    def create_workdir(self, overwrite=True):

        cycle = self.starttime.strftime('%Y%m%d%H')

        workdir = self.config.paths.workdir.format(
            n=self.config.paths,
            cycle=cycle
            )

        if os.path.exists(workdir):
            if overwrite:
                shutil.rmtree(workdir)
            else:
                msg = f"create_workdir: {workdir} exists & will not be removed!"
                raise errors.DirectoryExists(msg)

        os.makedirs(workdir)

        return workdir

    def stage_files(self, action, links):

        if not links:
            return

        if action not in ['copy', 'link']:
            msg = 'link_static_files: action = {action} is not copy or link.'
            raise ValueError(msg)

        if not isinstance(links, dict):
            msg = 'link_static_files: links is type {type(links)}, expected dict.'
            raise ValueError(msg)

        n = self.config

        files = []
        for path_name, filelist in links.items():

            path_dir = n.paths.__dict__.get(
                path_name,
                self.machine.dirs.__dict__.get(path_name),
                )

            if not path_dir:
                msg = f'stage_files: cannot find a path entry for {path_name}'
                raise ValueError(msg)

            for src_dst in filelist:

                # First item of list will be the name of the source. Join with
                # the path specified by the section header.
                filepath = os.path.join(path_dir, src_dst[0])

                # Last item of list will be the name of the destination
                dest_name = os.path.basename(src_dst[-1])
                destination = os.path.join(self.workdir, dest_name)

                # Add the processed src_dst to the filelist
                files.append((filepath, destination))

        for src, dst in files:
            if action == 'copy':
                utils.safe_link(src.format(n), dst.format(n))
            if action == 'link':
                utils.safe_copy(src.format(n), dst.format(n))

    @staticmethod
    def create_yml(outfile, settings):

        with open(outfile, 'w') as fn:
            yaml.dump(settings, fn)


    @staticmethod
    def render_template(outfile, template, tmpl_vars):

        with open(template, 'r') as tmpl_file:
            template = j2.Template(tmpl_file.read())

        xml_contents = template.render(**tmpl_vars)

        with open(outfile, 'w') as out_file:
            out_file.write(xml_contents)

    @property
    def executable(self):
        pass

    def parallel_run(self, exe):

        run_cmd = self.machine.run_command.format(n=self.config)
        cmd = shlex.split(f'{run_cmd} {exe}')
        pc = subprocess.run(cmd, check=True, stdout=subprocess.PIPE)

        while True:
            output = pc.stdout.readline()
            if not output and pc.poll():
                break
            if output:
                print(output.strip())

        rc = pc.poll()
        return rc


class Forecast(BatchJob):

    def __init__(self, config, machine, starttime, **kwargs):

        BatchJob.__init__(self, config, machine, starttime, **kwargs)

        # Set of configuration Namespace objects.
        self.grid = self.config_namespace(kwargs.get('grid'))
        self.nml = self.config_namespace(kwargs.get('nml'))



    def run(self, dry_run=False):

        # Create workdir (currently handled by J-JOB, is that NCO-necessary?)

        # Link/copy in static and cycle dependent files
        for section in ['static', 'cycledep']:
            self.stage_all(section)

        # Create diag_table
        self.create_diag_table()

        # Create model_config
        self.create_model_config()

        # Create input.nml
        self.create_nml()

        # Run the forecast
        if not dry_run:
            self.parallel_run(self.config.static.copy.fv3_exec[0])

    def create_diag_table(self):

        outfile = os.path.join(self.workdir, 'model_config')
        template = self.config.paths.diag_tmpl.format(n=self.config)
        template_vars = {
            'res': self.config.res,
            'starttime': self.starttime,
            }
        self.render_template(outfile, template, template_vars)

    def create_model_config(self):

        # Output file
        model_config_out = os.path.join(self.workdir, 'model_config')

        # Aliasing object variables for consistency with YAML
        # pylint: disable=possibly-unused-variable
        config = self.config
        grid = self.grid
        machine = self.machine
        # pylint: enable=possibly-unused-variable

        # Start with config items set in fv3_script
        model_config_items = config.model_config

        # Loop through each item and add it to the model_config dict
        model_config = {}

        for item in model_config_items:

            # Each item should be a key, value pair, or a single string item.
            if isinstance(item, dict):

                # For key, value pairs, set the model_config dict with the key,
                # and use the value as a reference to a configuration set by one
                # of the object variables: config, grid, machine, etc. If this
                # the value does not reference a local variable, then set it to
                # the value provided in the config.
                for key, value in item.items():
                    var_val = locals().get(value).__dict__.get(key)
                    value = var_val if var_val else value
                    value = f'.{str(value).lower()}' if isinstance(value, bool) else value

                    model_config[key] = var_val if var_val else value

            else: # item is a single item string
                try:
                    # Call the method named by the item
                    model_config.update(self.__getattribute__(item)())

                except KeyError:
                    msg = f'{__name__}: {item} is not an available method!'
                    print(msg)

        self.create_yml(model_config_out, model_config)

    def _pe_member01(self):

        mpi_tasks = self.grid.layout_x * self.grid.layout_y

        if self.config.quilting:
            mpi_tasks += self.grid.write_groups * self.grid.write_tasks_per_group

        # The number of processors will be used when running non-slurm
        # subprocess. Make note of it in the config.
        self.config.__dict__['nproc'] = mpi_tasks

        return {'pe_member01': mpi_tasks}

    def _quilting(self):

        ret = {'quilting': self.config.quilting}

        if self.config.quilting:
            ret.update(self.grid.quilting)

        return ret

    def _start_times(self):
        times = ['year', 'month', 'day', 'hour', 'minute', 'second']
        return {f'start_{t}': f'{self.starttime.__getattribute__(t):02d}' for t in times}


    def create_nml(self):

        fv3_nml = os.path.join(self.workdir, 'input.nml')

        # Read in the namelist that has all the base settings.
        base_nml = f90nml.read(self.config.paths.base_nml)

        # Update the base namelist with settings for the current configuration
        # Send self.nml, a Namespace object, as dict to update_dict.
        # Update_dict modifies dict in place.
        utils.update_dict(base_nml, self.nml.__dict__)

        with open(fv3_nml, 'w') as fn:
            base_nml.write(fn)


    def stage_all(self, section):

        allowed_sections = ['static', 'cycledep']
        if section not in allowed_sections:
            msg = f'stage_all: {section} is not in {allowed_sections}.'
            raise ValueError(msg)

        n = self.config
        links = self.config.static.link
        copies = self.config.static.copy

        for action in ['copy', 'link']:
            self.stage_files(action, self.config.static.__dict__.get(action, {}))
