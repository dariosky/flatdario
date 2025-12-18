import glob
import os
import subprocess
from contextlib import contextmanager
from functools import wraps

from crontab import CronTab
from fabric.api import env, task
from fabric.context_managers import prefix, cd, lcd, settings, hide
from fabric.contrib.files import exists
from fabric.operations import run, put, local, get
from fabric.tasks import execute

project_folder = os.path.dirname(__file__)
os.chdir(project_folder)


class Config:
    project_path = '~/apps/darioskyflat'
    venv = "~/.pyenv/versions/flat"
    git_repo = 'git@github.com:dariosky/flatdario.git'
    requirements = 'requirements.txt'
    port = 29606


if os.path.exists(os.path.expanduser("~/.ssh/config")):
    env.use_ssh_config = True

# Default host alias (matches ~/.ssh/config entry)
DEFAULT_HOST = ['opal']


def _load_identity_from_ssh_config(host_alias):
    """
    Try to read IdentityFile from `ssh -G <host>` so includes/Match rules are honored.
    """
    try:
        output = subprocess.check_output(
            ['ssh', '-G', host_alias], stderr=subprocess.DEVNULL, text=True
        )
    except Exception:
        return
    parsed = {}
    keys = []
    for line in output.splitlines():
        parts = line.strip().split()
        if len(parts) == 2 and parts[0].lower() == 'identityfile':
            candidate = os.path.expanduser(parts[1])
            if os.path.isfile(candidate):
                keys.append(candidate)
        elif len(parts) == 2:
            parsed[parts[0].lower()] = parts[1]
    return parsed, keys


def set_hosts(hosts):
    # using env.hosts only didn't work for me
    if isinstance(hosts, str):
        hosts = [hosts]
    resolved_hosts = []
    keyfiles = []
    first_host = hosts[0]
    host_alias = first_host.split('@')[-1]
    parsed, keys = _load_identity_from_ssh_config(host_alias) or ({}, [])
    if keys:
        keyfiles.extend(keys)
    user = parsed.get('user', None)
    port = parsed.get('port', None)
    for h in hosts:
        alias = h.split('@')[-1]
        host_cfg, host_keys = _load_identity_from_ssh_config(alias) or ({}, [])
        if host_keys:
            keyfiles.extend(host_keys)
        host_user = host_cfg.get('user', user)
        host_port = host_cfg.get('port', port)
        host_entry = alias  # keep SSH alias to respect ssh_config resolution
        if host_user:
            host_entry = f"{host_user}@{host_entry}"
        if host_port:
            host_entry = f"{host_entry}:{host_port}"
        resolved_hosts.append(host_entry)
    env.hosts = resolved_hosts
    env.host_string = ",".join(resolved_hosts)
    if keyfiles:
        env.key_filename = keyfiles


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
    if not env.hosts:
        set_hosts(DEFAULT_HOST)
    with cd(Config.project_path):
        if not exists('.git'):
            print("Cloning GIT repo")
            execute(clone)
        execute(pull_repo)
        execute(update_requirements)
        execute(build)
        execute(upload_build)


@task
def build():
    """ Create an optimized production build """
    with lcd(os.path.join(project_folder, 'api', 'ui')):
        local('yarn build')


@task
def upload_secrets():
    """ Send local secrets to the remote server """
    uploads = glob.glob('appkeys/*.json') + glob.glob('userkeys/*.json')
    upload_files(uploads)


def upload_files(uploads):
    remote_folder = Config.project_path
    with lcd(project_folder):
        with cd(Config.project_path):
            for filepath in uploads:
                src_path = os.path.join(project_folder, filepath)
                dst_path = os.path.join(remote_folder, filepath)
                if os.path.isdir(src_path):
                    run(f"mkdir -p {dst_path}")
                    dst_path = os.path.dirname(dst_path)
                put(src_path, dst_path)


def is_dir(path, use_sudo=False):
    """
    Check if a path exists, and is a directory.
    """
    with settings(hide('running', 'warnings'), warn_only=True):
        return run(f'[ -d "{path}" ]').succeeded


def download_files(downloads):
    remote_folder = Config.project_path
    with lcd(project_folder):
        with cd(Config.project_path):
            for filepath in downloads:
                src_path = os.path.join(remote_folder, filepath)
                dst_path = os.path.join(project_folder, filepath)
                if is_dir(src_path):
                    local(f"mkdir -p {dst_path}")
                    dst_path = os.path.dirname(dst_path)
                get(src_path, dst_path)


@task
def upload_build():
    """ Upload the React build """
    # be sure that the build folder is there:
    build_folder = 'api/ui/build'
    upload_files([build_folder])


@task
def upload_db():
    """ Upload the local DB online (deleting it) """
    confirm = input("WARNING: You're overwriting the remote DB [y/N]: ")
    if confirm.strip().lower() == "y":
        uploads = ['db.sqlite']
        upload_files(uploads)


@task
def upload_secret_claims():
    uploads = ['push/private_key.pem', 'push/claims.json']
    upload_files(uploads)


@task
def download_db():
    """ Download the remote DB online (deleting the local one) """
    downloads = ['db.sqlite']
    download_files(downloads)


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

    run_command = f'nohup {python} {command_full_path} {run_params}'
    log_command = f'>> {log_destination} 2>&1'
    cd_command = f'cd {Config.project_path}'

    full_command = f'{cd_command} && {run_command} {log_command} &'

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


@task
@flat_command
def reset():
    """ Update the collected sources """
    run('git reset --hard')


if not env.hosts:
    set_hosts('opal')  # the host where to deploy

if __name__ == '__main__':
    # to debug the fabfile, we can specify the command here
    import sys
    from fabric.main import main

    sys.argv[1:] = [
        "download_db",
        # "deploy",
    ]
    main()
