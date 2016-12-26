import click
import os

@click.group()
def main():
    pass

@main.command()
@click.option('--clone', '-c', default=None,
        help='Start a new project by cloning a git repo.')
def new_project(clone=None):
    """Sets up new sjwf project in current directory.
    
    Create a new project in the current directory, optionally by cloning
    a git repo.  A directory called 'python_data' will be created to hold a
    pickled dictionary of project information.  If a repository is passed
    as an argument, then the git repo will be cloned bare in the current
    directory.  Finally, settings.py and constants.py files will be created,
    if none exists.

    :param clone: a string of the URL for the git repository to clone
    """
    click.echo('new project')
    os.chdir('tests')
    click.echo(os.listdir())

@main.command()
def build_image():
    pass

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
