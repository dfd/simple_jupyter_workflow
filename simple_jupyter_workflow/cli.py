import click
import os
import shutil
#import imp
import importlib.util
#import constants

dir_path = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location('constants', dir_path + '/constants.py')
constants = importlib.util.module_from_spec(spec)
#click.echo(module_spec)
spec.loader.exec_module(constants)

class Config(object):

    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', '-v', is_flag=True,
        help='Print all output to standard out')
@pass_config
def main(config, verbose):
    config.verbose = verbose 

@main.command()
@click.option('--clone', '-c', default=None,
        help='Start a new project by cloning a git repo.')
@pass_config
def new_project(config, clone=None):
    """Sets up new sjwf project in current directory.
    
    Create a new project in the current directory, optionally by cloning
    a git repo.  A directory called 'python_data' will be created to hold a
    pickled dictionary of project information.  If a repository is passed
    as an argument, then the git repo will be cloned bare in the current
    directory.  Finally, settings.py and constants.py files will be created,
    if none exists.

    :param clone: a string of the URL for the git repository to clone
    """
    if config.verbose:
        click.echo('Starting new project...')
    try:
        os.mkdir('./python_data')
    except FileExistsError:
        click.echo('python_data directory already exists.  Is there already a '
                'project here?')
    shutil.copyfile(dir_path + '/reference/settings.py', 'settings.py')
    #os.chdir('tests')
    #click.echo(os.listdir())

@main.command()
@pass_config
def build_image(config):
    click.echo('Starting to build image...')
    #### don't work aMod = __import__(os.getcwd() + '/settings.py', globals(), locals(), [''])
    #a, b, c = imp.find_module('settings', [os.getcwd()])
    #imp.load_module('settings', a, b, c)
    spec = importlib.util.spec_from_file_location('settings', os.getcwd()+ '/settings.py')
    settings = importlib.util.module_from_spec(spec)
    #click.echo(module_spec)
    spec.loader.exec_module(settings)
    click.echo(settings.source)

@main.command()
def run_container():
    pass

@main.command()
def stop_container():
    pass

@main.command()
def remove_container():
    pass

@main.command()
def remove_image():
    pass

@main.command()
def git_branch():
    pass

@main.command()
def git_commit():
    pass

@main.command()
def git_merge():
    pass

@main.command()
def git_push():
    pass

@main.command()
def git_rollback():
    pass

@main.command()
def project_info():
    pass

#@click.command()
#@click.option('--as-cowboy', '-c', is_flag=True, help='Greet as a cowboy.')
#@click.argument('name', default='world', required=False)
#def main(name, as_cowboy):
#    """CLI with simple workflow for running Jupyter within Docker containers and version control for notebooks with git."""
#    greet = 'Howdy' if as_cowboy else 'Hello'
#    click.echo('{0}, {1}.'.format(greet, name))
