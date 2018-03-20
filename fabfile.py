import os
from contextlib import contextmanager

from fabric.api import env, task
from fabric.context_managers import prefix, cd
from fabric.contrib.files import exists
from fabric.operations import run, put
from fabric.tasks import execute


class Config:
    project_path = '~/webapps/darioskyflat'
    port = 29606
    venv = "~/.pyenv/versions/flat"
    git_repo = 'git@github.com:dariosky/flatdario.git'
    requirements = 'requirements.txt'


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


def clone():
    with cd(Config.project_path):
        run(f"git clone {Config.git_repo} .")


def update_requirements():
    with virtualenv():
        with cd(Config.project_path):
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
def collect():
    """ Update the collected sources """


@task
def upload_secrets():
    """ Send local secrets to the remote server """


def upload_files(uploads):
    project_folder = os.path.dirname(__file__)
    remote_folder = Config.project_path
    for filepath in uploads:
        put(os.path.join(project_folder, filepath),
            os.path.join(remote_folder, filepath))


@task
def upload_db():
    """ Upload the local DB online (deleting it) """
    uploads = ['db.sqlite']
    upload_files(uploads)


if not env.hosts:
    set_hosts('dariosky')  # the host where to deploy
