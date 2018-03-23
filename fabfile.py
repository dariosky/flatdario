import glob
import os
from contextlib import contextmanager
from functools import wraps

from crontab import CronTab
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
    run_params = f'runapi --port {Config.port}'
    run(f'python flat.py {run_params}')


def add_to_cron_command(command, run_params, comment_id, log_filename, schedule):
    cron = CronTab(user=True)

    command_full_path = os.path.join(Config.project_path, command)

    log_destination = os.path.join(Config.project_path, 'logs', log_filename)
    python = os.path.join(Config.venv, 'bin', 'python')

    check_command = f'pgrep -f {command}'
    run_command = f'nohup {python} {command_full_path} {run_params}'
    log_command = f'>> {log_destination} 2>&1'
    cd_command = f'cd {Config.project_path}'

    full_command = f'{check_command} || {cd_command} && {run_command} {log_command} &'

    existing_jobs = list(cron.find_comment(comment_id))

    if not existing_jobs:
        # create the job
        print("Creating job:")
        job = cron.new(command=full_command, comment=comment_id)
        for time_attr, value in schedule.items():
            every = job.every(value)
            getattr(every, time_attr)()  # example: job.every(5).minutes()

        print(job)
        # create log folder
        with lcd(project_folder):
            os.makedirs('./logs', exist_ok=True)
        cron.write()


@task
@flat_command
def local_install():
    """ Install a cronjob in the current host to start the api if it's not running """
    add_to_cron_command(command='flat.py',
                        run_params=f'runapi --port {Config.port}',
                        comment_id='flat-dariosky',
                        log_filename='flat_run.log',
                        schedule={"minutes": 5},
                        )
    #  Install a cronjob in the current host to collect from all available sources
    add_to_cron_command(command='flat.py',
                        run_params=f'collect',
                        comment_id='flat-dariosky-collect',
                        log_filename='flat_collect.log',
                        schedule={"hours": 6},
                        )


@task
@flat_command
def remote_install():
    """ Update the collected sources """
    run('fab local_install')


if not env.hosts:
    set_hosts('dariosky')  # the host where to deploy

if __name__ == '__main__':
    # to debug the fabfile, we can specify the command here
    import sys
    from fabric.main import main

    sys.argv[1:] = [
        "local_install",
    ]
    main()
