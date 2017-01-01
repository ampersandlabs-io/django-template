### Management utilities

import os
import time
import yaml
from fabric.contrib.console import confirm
from fabric import api as fab
from fabric.api import task
from fabric.colors import yellow, green, blue, red
#import boto.ec2
from contextlib import contextmanager


########## GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

APP_CONFIG_FILE = BASE_DIR('{{ project_name }}', '{{ project_name }}', 'conf', 'app_config.yaml')

try:
    fab.env.app_conf = yaml.load(open(APP_CONFIG_FILE, 'r'))['APP']
except IOError:
    raise RuntimeError(
        """
        There was an error loading the application config file: %s \n
        Please make sure the file exists and does not contain errors \n.
        """ % APP_CONFIG_FILE
    )

fab.env.django_settings_module = '{{ project_name }}.settings'
fab.env.local_run = 'python manage.py'
fab.env.run = 'heroku run python manage.py'
fab.env.production_app = '' # Needs a value
fab.env.staging_app = '' # Needs a value

########## END GLOBALS


########## HELPERS
def cont(cmd, message):
    """Given a command, ``cmd``, and a message, ``message``, allow a user to
    either continue or break execution if errors occur while executing ``cmd``.

    :param str cmd: The command to execute on the local system.
    :param str message: The message to display to the user on failure.

    .. note::
        ``message`` should be phrased in the form of a question, as if ``cmd``'s
        execution fails, we'll ask the user to press 'y' or 'n' to continue or
        cancel exeuction, respectively.

    Usage::

        cont('heroku run ...', "Couldn't complete %s. Continue anyway?" % cmd)
    """
    with fab.settings(warn_only=True):
        result = fab.run(cmd)

    if message and result.failed and not confirm(message):
        fab.abort('Stopped execution per user request.')


def l_cont(cmd, message):
    """Given a command, ``cmd``, and a message, ``message``, allow a user to
    either continue or break execution if errors occur while executing ``cmd``.

    :param str cmd: The command to execute on the local system.
    :param str message: The message to display to the user on failure.

    .. note::
        ``message`` should be phrased in the form of a question, as if ``cmd``'s
        execution fails, we'll ask the user to press 'y' or 'n' to continue or
        cancel exeuction, respectively.

    Usage::

        cont('heroku run ...', "Couldn't complete %s. Continue anyway?" % cmd)
    """
    with fab.settings(warn_only=True):
        result = fab.local(cmd, capture=True)

    if message and result.failed and not confirm(message):
        fab.abort('Stopped execution per user request.')


def su_cont(cmd, message):
    """Given a command, ``cmd``, and a message, ``message``, allow a user to
    either continue or break execution if errors occur while executing ``cmd``.

    :param str cmd: The command to execute on the local system.
    :param str message: The message to display to the user on failure.

    .. note::
        ``message`` should be phrased in the form of a question, as if ``cmd``'s
        execution fails, we'll ask the user to press 'y' or 'n' to continue or
        cancel exeuction, respectively.

    Usage::

        cont('heroku run ...', "Couldn't complete %s. Continue anyway?" % cmd)
    """
    with fab.settings(warn_only=True):
        result = fab.sudo(cmd)

    if message and result.failed and not confirm(message):
        fab.abort('Stopped execution per user request.')


########## END HELPERS


########## DATABASE MANAGEMENT

@task
def backup_db():
    pass


@task
def mkmigrations():
    """Create migrations."""
    fab.local('{} makemigrations'.format(fab.env.local_run))


@task
def migrate(env='staging', app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app.
    """

    fab.local('{0} migrate'.format(
        fab.env.local_run
    ))


@task
def remote_migrate(env='staging', app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str env: Heroku environment.
    :param str app: Django app.
    """
    heroku_app = fab.env.staging_app

    if env == 'production':
        heroku_app = fab.env.production_app

    fab.local('heroku maintenance:on --app {0}'.format(
        heroku_app
    ))
    fab.local('{0} migrate --app {1}'.format(
        fab.env.run, heroku_app
    ))
    fab.local('heroku maintenance:off --app {0}'.format(
        heroku_app
    ))


########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    fab.local('{} collectstatic --noinput'.format(fab.env.local_run))
########## END FILE MANAGEMENT


@task
def create_superuser():
    """Create super user."""
    fab.local('{} createsuperuser'.format(fab.env.local_run))


@task
def remote_create_superuser(env='staging'):

    heroku_app = fab.env.staging_app

    if env == 'production':
        heroku_app = fab.env.production_app

    fab.local('heroku maintenance:on --app {0}'.format(heroku_app))
    fab.local('{0} createsuperuser --app {1}'.format(fab.env.run, heroku_app))
    fab.local('heroku maintenance:off --app {0}'.format(heroku_app))


@task
def update_code(branch, remote_name='origin'):
    """Commit & push codebase to bitbucket, don't forget to create a PR"""
    fab.local('pip freeze > requirements.txt')
    fab.local('git add .')
    print(green('Commit message >>> '))
    msg = raw_input()
    l_cont('git commit -m "{0}"'.format(msg), 'git commit failed, continue?')
    fab.local('git pull {0} {1}'.format(remote_name, branch))
    fab.local('git push -u {0} {1}'.format(remote_name, branch))


@task
def update_app_config(env='staging'):

    heroku_app = fab.env.staging_app

    if env == 'production':
        heroku_app = fab.env.production_app

    fab.local('heroku maintenance:on --app {0}'.format(
        heroku_app
    ))

    fab.env.app_conf.pop('DATABASE_URL', None)

    for config_key in fab.env.app_conf:

        if config_key != 'DEBUG' or config_key != 'TEMPLATE_DEBUG':
            fab.local('heroku config:set {0}="{1}" --app {2}'.format(
                config_key, fab.env.app_conf[config_key], heroku_app
            ))
        else:
            fab.local('heroku config:set {0}={1} --app {2}'.format(
                config_key, fab.env.app_conf[config_key], heroku_app
            ))

    fab.local('heroku maintenance:off --app {0}'.format(
        heroku_app
    ))


@task
def create_heroku_app(name):
    fab.local('heroku create {}'.format(name))


@task
def prep_staging():
    pass


@task
def prep_production():
    pass


