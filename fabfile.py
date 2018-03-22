import glob
import os
from contextlib import contextmanager
from functools import wraps

from fabric.api import env, task
from fabric.context_managers import prefix, cd, lcd
from fabric.contrib.files import exists
from fabric.operations import run, put
from fabric.tasks import execute

project_folder = os.path.dirname(__file__)
os.chdir(project_folder)


class Config:
    project_path = '~/webapps/darioskyflat'
    venv = "~/.pyenv/versions/flat"
    git_repo = 'git@github.com:dariosky/flatdario.git'
    requirements = 'requirements.txt'
    port = 29606


if os.path.exists(os.path.expanduser("~/.ssh/config")):
    env.use_ssh_config = True


def set_hosts(hosts):
    # using env.hosts only didn't work for me
    env.hosts = hosts
    env.host_string = ",".join(hosts)


@contextmanager
def virtualenv():
    """ Put fabric commands in a virtualenv """
    with prefix("source %s" % os.path.join(Config.venv, "bin/activate")):
        yield


def flat_command(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        with virtualenv():
            with cd(Config.project_path):
                return func(*args, **kwargs)

    return wrapped


def clone():
    with cd(Config.project_path):
        run(f"git clone {Config.git_repo} .")


@task
@flat_command
def update_requirements():
    """ Silently update requirements """
    run(f'pip install -q -U pip wheel')
    run(f'pip install -q -r {Config.requirements}')


def pull_repo():
    with cd(Config.project_path):
        run(f'git pull')


@task
def deploy():
    """ Pull the changes, update requirements on remote host"""
    with cd(Config.project_path):
        if not exists('.git'):
            print("Cloning GIT repo")
            execute(clone)
        execute(update_requirements)
        execute(pull_repo)


@task
def upload_secrets():
    """ Send local secrets to the remote server """
    uploads = glob.glob('appkeys/*.json') + glob.glob('userkeys/*.json')
    upload_files(uploads)


def upload_files(uploads):
    remote_folder = Config.project_path
    with lcd(project_folder):
        for filepath in uploads:
            put(os.path.join(project_folder, filepath),
                os.path.join(remote_folder, filepath))


@task
def upload_build():
    """ Upload the React build """
    # be sure that the build folder is there:
    build_folder = 'api/ui/build'
    with cd(Config.project_path):
        run(f"mkdir -p {build_folder}")
    upload_files([build_folder])


@task
def upload_db():
    """ Upload the local DB online (deleting it) """
    uploads = ['db.sqlite']
    upload_files(uploads)


@task
@flat_command
def collect():
    """ Update the collected sources """
    run('python flat.py collect')


@task
@flat_command
def start():
    """ Run the API as production """
    run(f'python flat.py runapi --port {Config.port}')


if not env.hosts:
    set_hosts('dariosky')  # the host where to deploy

if __name__ == '__main__':
    # to debug the fabfile, we can specify the command here
    import sys
    from fabric.main import main

    sys.argv[1:] = [
        "start",
    ]
    main()
