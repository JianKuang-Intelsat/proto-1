#################################################################
def set_environment(config_suite):
	config_suite.update({'machine': 'Orion'})
	return(config_suite)
## environment set up 


def configs_init(EXPDIR):
	config_suite.update({ rotdir: 'rot_dir_here' , rundir: 'run_dir_here' })
	return config_suite
    
## configuration settings before run type determination
## config_suite is a python dict containing all configuration
## information

def get_runtype(config_suite):
	rotdir = config_suite.rotdir
	runtype = 'warm_start'
	config_suite.update({'rtype': runtype})
	return config_suite
## run type determination: cold, warm

def yaml_reader(fpath):
	with open(fpath, 'rb') as fname:
		data = yaml.load_all(fname)
		return data

def yaml_dump(filepath, data):
    with open(filepath, 'wb') as file_descriptor:
        yaml.dump(data, file_descriptor, allow_unicode=True, encoding='utf-8')

def get_configs(EXPDIR):
#	config_suite = yaml.load(EXPDIR/config.**,loader=full_loader)
	for xfile in os.listdir(EXPDIR):
		config_suite.update(yaml.reader(xfile))

	return config_suite 
## configuration setting after run type determination
## ! See if consolidating with get_config_init is possible !

def make_nml(rundir, config_suite):
	yaml.dump(config_suite,rundir)
	return(0)
## parsing namelists for executables

def mpi_launch(aprun, rundir, fexec):
	os.system("%s %s/%s", aprun, rundir, fexec)
## launch mpi

def main():
	if(len(sys.argv) != 1):
		print('invalid argument parsing')
		return(1)
	EXPDIR = sys.argv[0]
	config_suite = {}
	config_suite = set_environment(config_suite)
	print(config_suite)
	print('running on ', config_suite['machine'])
	config_suite = config_init(config_suite)
	config_suite = get_runtype(config_suite)
	print('run type is ', config_suite.rtype)
	config_suite = get_configs(config_suite)
	rundir = config_suite.rundir
	print('rundir is', rundir)
	make_nml(config_suite)
	mpi_launch(config_suite)

if __name__ == '__main__':
	import sys
	import os
	import shutil
	import yaml
	import f90nml
	main()
