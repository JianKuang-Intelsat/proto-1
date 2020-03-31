import os


class BatchJob():

    def __init__(config, starttime, workdir):

        self.config = utils.namespace(config)
        self.workdir = workdir

    def source_modules(self):
        pass

    def link_static_files(self):
        pass

    def copy_files(self):
        pass

    def create_yml(self, outfile, items):
        pass

    def render_template(self, outfile, items):
        pass

    @property
    def executable(self):
        pass

    def parallel_run(self):
        pass



class Forecast(BatchJob):

    def __init__(starttime):

        self.starttime = starttime

