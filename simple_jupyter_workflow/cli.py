import click
import os
import shutil
import importlib.util
import docker
import pickle
import urllib.request
import git
from requests.exceptions import ReadTimeout

dir_path = os.path.dirname(os.path.realpath(__file__))
spec = importlib.util.spec_from_file_location('constants', dir_path + '/constants.py')
constants = importlib.util.module_from_spec(spec)
spec.loader.exec_module(constants)

def verbose_message(config, message):
    if config.verbose:
        click.echo(message)

def import_settings():
    """Load settings module from project on demand"""
    spec = importlib.util.spec_from_file_location('settings', os.getcwd()+ '/simplej/settings.py')
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    return settings

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
    except ReadTimeout:
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
        verbose_message(config, "Container stopped.")

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
    """Sets up new simplej project in current directory.
    
    Create a new project in the current directory, optionally by cloning
    a git repo.  A directory called 'simplej' will be created to hold a
    pickled dictionary of project information.  If a repository is passed
    as an argument, then the git repo will be cloned bare in the current
    directory.  Finally, settings.py will be created, if none exists.

    :param config: Config object with global options
    :param clone: a string of the URL for the git repository to clone
    """
    verbose_message(config, 'Starting new project...')
    try:
        os.mkdir('./simplej')
    except FileExistsError:
        click.echo('simplej directory already exists.  Is there already a '
                'project here?')
    shutil.copyfile(dir_path + '/reference/settings.py', './simplej/settings.py')

@main.command()
@pass_config
def prepare_image(config):
    """Builds or pulls Docker container image.

    Builds a Docker image from a Dockerfile or pulls an image from Dockerhub.
    The Dockerfile can be local, online, or in a git repo.

    :param config: Config object with global options
    """
    path_to_df = '.'
    verbose_message(config, 'Starting to prepare image...')
    settings = import_settings()
    source = settings.source
    client = docker.from_env()
    if source == constants.SOURCES.DOCKERHUB:
        verbose_message(config, 'Pulling image from Dockerhub...')
        image = client.images.pull(settings.image_name, tag=settings.image_tag)
        verbose_message(config, 'Image pulled...')
    elif source == constants.SOURCES.LOCAL_IMAGE:
        verbose_message(config, 'Using local image...')
        try:
            image = client.images.get(settings.image_id)
        except docker.errors.ImageNotFound:
            click.echo('Image not found.')
            return
        except:
            click.echo("Unexpected error:", sys.exec_info()[0])
    elif source == constants.SOURCES.URL:
        verbose_message(config, 'Pulling Dockerfile from URL...')
        with urllib.request.urlopen(settings.url) as response, open(os.getcwd() 
                + '/Dockerfile', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
            source = constants.SOURCES.DOCKERFILE
    elif source == constants.SOURCES.GIT:
        verbose_message(config, 'Cloning git repo...')
        #os.mkdir('./Docker')
        git.Repo.clone_from(settings.git_url, 'Docker', **{'depth':'1'})
        shutil.rmtree('./Docker/.git', ignore_errors=True)
        for root, dirs, files in os.walk('./Docker/'):
            if settings.df_name in files:
                path_to_df = os.path.join(root)
                break
        source = constants.SOURCES.DOCKERFILE
    if source == constants.SOURCES.DOCKERFILE:
        if config.verbose:
            click.echo('Building image from Dockerfile...')
        image = client.images.build(**{'path':path_to_df, 'rm':'TRUE'})
    docker_dict = load_pkl()
    docker_dict['image_id'] = image.short_id
    write_pkl(docker_dict)
    verbose_message(config, 'Image is ready.')


@main.command()
@pass_config
def run_container(config):
    """Runs the project container.

    Runs the project container, binding the project directory to the container
    directory specified by the settings.py file.

    :param config: Config object with global options
    """
    verbose_message(config, 'Attempting to run container...')
    settings = import_settings()
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
    verbose_message(config, 'Container is running.')

@main.command()
@pass_config
def stop_container(config):
    """Stops the project container.

    Stops the project container, if it's running.

    :param config: Config object with global options
    """
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
    verbose_message(config, 'Attempting to remove container...')
    client = docker.from_env()

    docker_dict = load_pkl()
    container_id = docker_dict.pop('container_id', False)
    if container_id:
        container = client.containers.get(container_id)
        container.remove()
        verbose_message(config, 'Container removed.')
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
    verbose_message(config, 'Attempting to remove image...')
    client = docker.from_env()
    docker_dict = load_pkl()
    image_id = docker_dict.pop('image_id', False)
    if image_id:
        client.images.remove(image_id)
        verbose_message(config, 'Image removed.')
        write_pkl(docker_dict)
    else:
        click.echo("No image in project.")

@main.command()
@pass_config
def show_token(config):
    """Shows  currently running Jupyter notebook servers, including token

    Runs `docker exec <container_id> jupyter notebook list`

    :param config: Config object with global options
    """
    client = docker.APIClient()

    docker_dict = load_pkl()
    container_id = docker_dict.get('container_id', False)
    exec_id = client.exec_create(container=container_id,
            cmd='jupyter notebook list')
    click.echo(client.exec_start(exec_id))


@main.command()
@pass_config
@click.pass_context
def all_up(ctx, config):
    """Prepares image and runs container

    :param ctx: the clickcontext
    "param config: Config object with global options
    """
    ctx.forward(prepare_image, config)
    ctx.forward(run_container, config)


@main.command()
@pass_config
@click.pass_context
def destroy(ctx, config):
    """Stops container, removes conatiner and removes the image

    :param ctx: the clickcontext
    :param config: Config object with global options
    """
    ctx.forward(stop_container, config)
    ctx.forward(remove_container, config)
    ctx.forward(remove_image, config)


def get_repo():
    return git.Repo('.')

@main.command()
@pass_config
def git_start(config):
    """Starts a git repo.

    Starts a git repo; places a .gitignore file; adds an origin to the repo
    from the settings file; and makes an initial commit to the repo.

    :param config: Config object with global options
    """
    settings = import_settings()
    shutil.copyfile(dir_path + '/reference/.gitignore', '.gitignore')
    repo = git.Repo.init('.')
    origin = repo.create_remote('origin', url=settings.git_origin)
    repo.git.add(A=True)
    commit = repo.index.commit('initial commit')

def print_branch(repo):
    click.echo('Currently on branch', repo.active_branch.name)


@main.command()
@pass_config
def branch(config):
    """Starts a dev branch.

    If the current branch is master, creates a new branch called dev and checks
    it out.

    :param config: Config object with global options
    """
    repo = get_repo()
    if repo.active_branch.name == 'master':
        new_branch = repo.create_head('dev')
        new_branch.checkout()
    else:
        click.echo('Not on master branch, so no new branch created.')
        print_branch(repo)

@main.command()
@click.argument('message')
@pass_config
def commit(config, message):
    """Commits changes to dev branch.

    If the current branch is dev, add all files with changes, and commit.

    :param config: Config object with global options
    :param message: Message to be passed to git commit
    """
    repo = get_repo()
    if repo.active_branch.name == 'dev':
        repo.git.add(A=True)
        commit = repo.index.commit(message)
    else:
        click.echo('Not on dev branch, so no commit will be made.'
                'Please use \'branch\' subcommand first.')
        print_branch(repo)

@main.command()
@pass_config
def merge(config):
    """Merge commits from dev branch with master.

    If the current branch is dev, then checkout master and merge with dev.

    :param config: Config object with global options
    """
    repo = get_repo()
    if repo.active_branch.name == 'dev':
        repo.git.checkout('master')
        repo.git.merge('master', 'dev')
    else:
        click.echo('Not on dev branch, so no merge will be made.')
        print_branch(repo)

@main.command()
@pass_config
def status(config):
    """Print the git status.

    :param config: Config object with global options
    """
    repo = get_repo()
    click.echo(repo.git.status())


@main.command()
@pass_config
@click.pass_context
def push(ctx, config):
    """Push repo to origin.

    Pushes repo to origin.  Prints warning if current branch is not master.

    :param config: Config object with global options
    """
    repo = get_repo()
    repo.remotes.origin.push('--all')
    if repo.active_branch.name != 'master':
        click.echo('Warning: current branch is not master.')
        print_branch(repo)
        ctx.invoke(status, config)

@main.command()
@pass_config
def rollback(config):
    """Rollback to last master commit and delete the dev branch.

    :param config: Config object with global options
    """
    repo = get_repo()
    repo.git.checkout('master')
    #repo.git.branch('-D dev')  ## does not work
    for branch in repo.branches:
        if branch.name == 'dev':
            repo.delete_head(branch, **{'force':'True'})
            break

@main.command()
@click.argument('message')
@pass_config
@click.pass_context
def commit_push(ctx, config, message):
    """ Commits a change, merges to master, and pushes the changes.

    :param ctx: the clickcontext
    "param config: Config object with global options
    :param message: Message to be passed to git commit
    """
    ctx.forward(commit, config)
    ctx.invoke(merge, config)
    ctx.invoke(push, config)



@main.command()
@pass_config
@click.pass_context
def project_info(ctx, config):
    """Display the projevt information

    Display the image and container IDs, and the git status.

    :param ctx: the clickcontext
    "param config: Config object with global options
    """
    click.echo(load_pkl())
    ctx.invoke(status, config)

