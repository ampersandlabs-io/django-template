# ### Management utilities

import os
import uuid
import boto3
from fabric.contrib.console import confirm
from fabric import api as fab
from fabric.api import task, env
from fabric.colors import yellow, green, blue, red

from contextlib import contextmanager

# ######### GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

ENV_FILE = BASE_DIR('{{ project_name }}', '.env')

try:

    with open(ENV_FILE) as f:
        keys = f.read().split('\n')
        fab.env.app_config = dict([x.split('=') for x in keys])

except IOError:

    raise RuntimeError(
        """
        There was an error loading the application config file: {} \n
        Please make sure the file exists and does no
        t contain errors \n.
        """.format(ENV_FILE)
    )

fab.env.django_settings_module = '{{ project_name }}.settings.dev'
fab.env.local_run = 'python manage.py'
fab.env.run = 'heroku run python manage.py'
fab.env.production_app = fab.env.app_config.get('HEROKU_PRODUCTION_APP')
fab.env.staging_app = fab.env.app_config.get('HEROKU_STAGING_APP')

# ######### END GLOBALS


# ######### HELPERS
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


# ######### END HELPERS


# ######### DATABASE MANAGEMENT

@task
def backup_db():
    fab.local('heroku pg:backups:capture && heroku pg:backups:download')


@task
def clone_remote_db_to_local(destination=None):

    fab.local('heroku pg:backups:capture && heroku pg:backups:download')

    database_url = fab.env.app_config.get('DATABASE_URL', None)

    if database_url is not None:
        db_params = database_url.split('/')
        db_name = destination or db_params[-1]
        db_cred = db_params[-2].split('@')[0].split(':')
        db_host_params = db_params[-2].split('@')[1].split(':')

        db_user = db_cred[0]
        db_host = db_host_params[0]

        fab.local('pg_restore - -verbose - -clean - -no - acl - -no - owner - h {0} - U {1} - d {2} {3}.dump'.format(
            db_user, db_host, db_name, uuid.uuid4()
        ))


@task
def import_local_db_to_remote():

    database_url = fab.env.app_config.get('DATABASE_URL', None)

    if database_url is not None:
        db_params = database_url.split('/')
        db_name = db_params[-1]
        db_cred = db_params[-2].split('@')[0].split(':')
        db_host_params = db_params[-2].split('@')[1].split(':')

        db_user = db_cred[0]
        db_pswd = db_cred[1]
        db_host = db_host_params[0]

        fab.local('PGPASSWORD={0} pg_dump -Fc --no-acl --no-owner -h {1} -U {2} {3} > {3}.dump'.format(
            db_pswd, db_host, db_user, db_name,
        ))

        # # upload to aws and get pre-signed url

        client = boto3.client(
            's3',
            aws_access_key_id=fab.env.app_config.get('AWS_S3_ACCESS_KEY_ID'),
            aws_secret_access_key=fab.env.app_config.get('AWS_S3_SECRET_ACCESS_KEY'),
        )

        # Upload a new file
        with open('{0}.dump'.format(db_name), 'rb') as data:
            client.put_object(
                Bucket=fab.env.app_config.get('AWS_STORAGE_BUCKET_NAME'),
                Key='uploads/db_backups/{0}.dump'.format(db_name),
                Body=data
            )

            db_url = client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': fab.env.app_config.get('AWS_STORAGE_BUCKET_NAME'),
                    'Key': 'uploads/db_backups/{0}.dump'.format(db_name),
                }
            )

            fab.local("heroku pg:backups:restore '{0}' DATABASE_URL".format(db_url))


@task
def create_superuser(target_env='dev'):

    if target_env.lower() == 'prod':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.production_app
        ))
        fab.local('{0} createsuperuser -a {1}'.format(
            fab.env.run, fab.env.production_app
        ))
        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.production_app
        ))

    elif target_env.lower() == 'staging':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.staging_app
        ))
        fab.local('{0} createsuperuser -a {1}'.format(
            fab.env.run, fab.env.staging_app
        ))
        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.staging_app
        ))

    elif target_env.lower() == 'dev':

        fab.local('{0} createsuperuser '.format(
            fab.env.local_run
        ))

    else:

        print(red('Please specify an environment. Valid options include dev, staging, prod'))


@task
def migrate(target_env='dev', app=''):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app.
    :param str target_env: Environment application exists in.
    """

    if target_env.lower() == 'prod':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.production_app
        ))
        fab.local('{0} migrate -a {1}'.format(
            fab.env.run, fab.env.production_app
        ))
        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.production_app
        ))

    elif target_env.lower() == 'staging':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.staging_app
        ))
        fab.local('{0} migrate -a {1}'.format(
            fab.env.run, fab.env.staging_app
        ))
        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.staging_app
        ))

    elif target_env.lower() == 'dev':

        fab.local('{0} makemigrations && {0} migrate'.format(
            fab.env.local_run
        ))

    else:

        print(red('Please specify an environment. Valid options include dev, staging, prod'))


# ######### END DATABASE MANAGEMENT


# ######### FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files."""
    fab.local('{} collectstatic --noinput'.format(fab.env.local_run))
# ######### END FILE MANAGEMENT


@task
def update_code(branch=None):
    """Commit & push codebase to bitbucket, don't forget to create a PR"""
    # fab.local('pip freeze > requirements.txt')
    fab.local('git add .')

    print(green('Commit message >>> '))
    msg = raw_input()

    if branch is None:
        branch = fab.local('git rev-parse --abbrev-ref HEAD', capture=True)

    l_cont('git commit -m "{0}"'.format(msg), 'git commit failed, continue?')
    fab.local('git pull origin {0}'.format(branch))
    fab.local('git push origin -u {0}'.format(branch))


@task
def update_app_config(target_env):

    app_config = fab.env.app_config

    app_config.pop('DATABASE_URL', None)
    app_config.pop('DEBUG', None)
    app_config.pop('REDIS_URL', None)

    if target_env.lower() == 'prod':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.production_app
        ))

        for config_key in app_config.keys():
            fab.local('heroku config:set {0}="{1}" -a {2}'.format(
                config_key, app_config[config_key], fab.env.production_app
            ))

        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.production_app
        ))

    elif target_env.lower() == 'staging':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.staging_app
        ))

        for config_key in app_config.keys():
            fab.local('heroku config:set {0}="{1}" -a {2}'.format(
                config_key, app_config[config_key], fab.env.staging_app
            ))

        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.staging_app
        ))

    else:

        print(red('Please specify an environment. Valid options include staging, prod'))


@task
def update_staging():
    update_app_config('staging')


@task
def update_prod():
    update_app_config('prod')


# ###### HEROKU

@task
def scale_dyno(target_env, d_type, n=0):

    if target_env.lower() == 'staging' or target_env.lower() == 'prod':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
        ))

        if d_type == 'web':
            fab.local('heroku scale web={0} -a {1}'.format(
                n, fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
            ))
        elif d_type == 'worker':
            fab.local('heroku scale worker={0} -a {1}'.format(
                n, fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
            ))

        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
        ))

    else:

        print(red('Please specify an environment. Valid options include staging, prod'))


@task
def logs(target_env, real_time=False):

    if target_env.lower() == 'staging' or target_env.lower() == 'prod':

        fab.local('heroku maintenance:on -a {0}'.format(
            fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
        ))

        fab.local('heroku logs {1} -a {0}'.format(
            fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app,
            '-t' if real_time else ''
        ))

        fab.local('heroku maintenance:off -a {0}'.format(
            fab.env.production_app if target_env.lower() == 'prod' else fab.env.staging_app
        ))

    else:

        print(red('Please specify an environment. Valid options include staging, prod'))


# ###### END HEROKU

