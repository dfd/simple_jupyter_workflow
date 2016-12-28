import click
import os
import shutil
import importlib.util
import docker
import pickle

dir_path = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location('constants', dir_path + '/constants.py')
constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants)

def load_pkl():
    """Loads project dictionary from pickle.

    Helper function that loads the project dictionary from a set location
    defined in the constants module.

    :return: `docker_dict` dictionary with project information
    """
    if constants.DICT_PKL.is_file():
        with open(str(constants.DICT_PKL), 'rb') as f:
            docker_dict = pickle.load(f)
            return docker_dict
    else:
        return {}

def write_pkl(docker_dict):
    """Writes dictionary to pickle
    
    Stores dictionary with project information to a designated location
    set by the constants module.

    :param docker_dict: dictionary of project information

    """
    with open(str(constants.DICT_PKL), 'wb') as f:
        pickle.dump(docker_dict, f)

def get_container(container_id, client):
    """Gets docker container object from a client given an ID

    Returns a docker container object from a client for a given ID,
    handling exceptions.

    :param container_id: string of container ID
    :param client: docker client
    :return: `container` the docker container object

    """
    try:
        container = client.containers.get(container_id)
    except NotFound:
        click.echo("Container not found.")
    except:
        click.echo("Unexpected error:", sys.exc_info()[0])
    else:
        return container

def container_start(container):
    pass


def container_stop(container, client, config):
    """Stops a running container

    Stops a running container within a client, handling exceptions.

    :param container: docker container object to stop
    :param client: docker client
    :param config: Config class passed from main function
    """
    try:
        container.stop()
    except timeout:
        print(timeout)
        container_list = client.containers.list(**{'id':container_id})
        if container_list:
            click.echo("Socket timeout.  Container status is: " + 
                    container_list[0].status)
        else:
            click.echo("Container not found. No containers were stopped.")
    except:
        click.echo("Unexpected error:", sys.exec_info()[0])
    else:
        if config.verbose:
            click.echo("Container stopped.")

class Config(object):

    def __init__(self):
        self.verbose = False

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@click.option('--verbose', '-v', is_flag=True,
        help='Print all output to standard out')
@pass_config
def main(config, verbose):
    """Entry point function for CLI tool
    
    :param config: Config object with global options
    :param verbose: flag indicating whether the output should be verbose
    """
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

    :param config: Config object with global options
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

@main.command()
@pass_config
def build_image(config):
    """Builds or pulls Docker container image.

    Builds a Docker image from a Dockerfile or pulls an image from Dockerhub.
    The Dockerfile can be local, online, or in a git repo.

    :param config: Config object with global options
    """
    if config.verbose:
        click.echo('Starting to build image...')
    spec = importlib.util.spec_from_file_location('settings', os.getcwd()+ '/settings.py')
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    client = docker.from_env()
    if settings.source == constants.SOURCES.DOCKERFILE:
        image = client.images.build(**{'path':'.', 'rm':'TRUE'})
    elif settings.source == constants.SOURCES.DOCKERHUB:
        image = client.images.pull(settings.image_name, tag=settings.image_tag)
        if config.verbose:
            click.echo('Image pulled...')
    elif settings.source == constants.SOURCES.URL:
        pass
    docker_dict = load_pkl()
    docker_dict['image_id'] = image.short_id
    write_pkl(docker_dict)
    if config.verbose:
        click.echo('Image is ready.')


@main.command()
@pass_config
def run_container(config):
    """Runs the project container.

    Runs the project container, binding the project directory to the container
    directory specified by the settings.py file.

    :param config: Config object with global options
    """
    if config.verbose:
        click.echo('Attempting to run container...')
    spec = importlib.util.spec_from_file_location('settings', os.getcwd()+ '/settings.py')
    settings = importlib.util.module_from_spec(spec)
    #click.echo(module_spec)
    spec.loader.exec_module(settings)
    client = docker.from_env()
    docker_dict = load_pkl()
    container_id = docker_dict.get('container_id', False)
    if container_id:
        container = get_container(container_id, client)
        container.start()
    else:
        volumes = {os.getcwd(): {'bind': settings.dir_to_mount, 'mode': 'rw'}}
        image_id = client.images.get(docker_dict['image_id'])
        container = client.containers.run(image_id, volumes=volumes, detach=True, ports={'8888/tcp':'8888', '6060/tcp':'6060'})
        docker_dict['container_id'] = container.short_id
        write_pkl(docker_dict)
    if config.verbose:
        click.echo('Container is running.')

@main.command()
@pass_config
def stop_container(config):
    """Stops the project container.

    Stops the project container, if it's running.

    :param config: Config object with global options
    """
    spec = importlib.util.spec_from_file_location('settings', os.getcwd()+ '/settings.py')
    settings = importlib.util.module_from_spec(spec)
    #click.echo(module_spec)
    spec.loader.exec_module(settings)
    client = docker.from_env()

    docker_dict = load_pkl()
    container_id = docker_dict.get('container_id', False)
    if container_id:
        container = get_container(container_id, client)
        if container.status != "running":
            click.echo("Container is not running.")
        else:
            container_stop(container, client, config)
    else:
        click.echo("No container found in project.")


@main.command()
@pass_config
def remove_container(config):
    """Removes project container.

    Removes the project container, if it exists.

    :param config: Config object with global options
    """
    client = docker.from_env()

    docker_dict = load_pkl()
    container_id = docker_dict.pop('container_id', False)
    if container_id:
        container = client.containers.get(container_id)
        container.remove()
        write_pkl(docker_dict)
    else:
        click.echo("No container in project.")

@main.command()
@pass_config
def remove_image(config):
    """Removes project image.

    Removes the project image, if it exists.

    :param config: Config object with global options
    """
    client = docker.from_env()
    docker_dict = load_pkl()
    image_id = docker_dict.pop('image_id', False)
    if image_id:
        client.images.remove(image_id)
        write_pkl(docker_dict)
    else:
        click.echo("No image in project.")

@main.command()
@pass_config
def git_branch(config):
    pass

@main.command()
@pass_config
def git_commit(config):
    pass

@main.command()
@pass_config
def git_merge(config):
    pass

@main.command()
@pass_config
def git_push(config):
    pass

@main.command()
@pass_config
def git_rollback(config):
    pass

@main.command()
@pass_config
def project_info(config):
    pass

