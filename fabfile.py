"""Management utilities."""

import os
from fabric.contrib.console import confirm
from fabric.api import abort, env, local, settings, task, cd, run
from fabric.colors import green, red


# env.hosts = [os.environ.get('ENV')]

########## GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

env.run = 'python manage.py'

AWS_EC2_CONFIGS = (
    'DJANGO_SETTINGS_MODULE={{ project_name }}.settings.prod',
    'SECRET_KEY={0}'.format(os.environ.get('SECRET_KEY', '')),
    'AWS_ACCESS_KEY_ID={0}'.format(os.environ.get('AWS_S3_ACCESS_KEY_ID', '')),
    'AWS_SECRET_ACCESS_KEY={0}'.format(os.environ.get('AWS_S3_SECRET_ACCESS_KEY', '')),
    'AWS_STORAGE_BUCKET_NAME={0}'.format(os.environ.get('AWS_STORAGE_BUCKET_NAME', '')),
    'DEBUG={0}'.format(os.environ.get('DEBUG', '')),
    'TEMPLATE_DEBUG={0}'.format(os.environ.get('TEMPLATE_DEBUG', '')),
    'DATABASE_URL={0}'.format(os.environ.get('DATABASE_URL', ''))
)
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
    with settings(warn_only=True):
        result = local(cmd, capture=True)

    if message and result.failed and not confirm(message):
        abort('Stopped execution per user request.')
########## END HELPERS


########## DATABASE MANAGEMENT
@task
def makemigrations():
    """Setup database."""
    local('{}(run)s makemigrations'.format(env))


@task
def migrate(app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app name to migrate.
    """
    if app:
        local('{} migrate {}'.format(env.run, app))
    else:
        local('{}(run)s migrate '.format(env))
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    local('{}(run)s collectstatic --noinput'.format(env))
########## END FILE MANAGEMENT


########## AWS MANAGEMENT
@task
def bootstrap():
    """Bootstrap your new application:

        - Update & Upgrade EC2 Instance.
        - Install all ``HEROKU_ADDONS``.
        - Sync the database.
        - Apply all database migrations.
        - Initialize New Relic's monitoring add-on.
    """
    cont('sudo apt-get update',
         "Couldn't update EC2 Instance, continue anyway?")
    cont('sudo apt-get upgrade',
         "Couldn't upgrade EC2 Instance, continue anyway?")
    cont('sudo apt-get install postgresql postgresql-contrib',
         "Couldn't install PostgresSQL, continue anyway?")
    cont('sudo su - postgres', "Couldn't login as postgres")
    cont('sudo apt-get install python-virtualenv',
         "Couldn't install python-virtualenv, continue anyway?")
    cd(BASE_DIR)
    cont('virtualenv env',
         "Couldn't create a virtual environment, continue anyway?")
    run('pip install -r requirements.txt')
    cont('sudo apt-get install libpq-dev python-dev',
         "Couldn't configure postgres to work with django, continue anyway?")

    for config in AWS_EC2_CONFIGS:
        cont('export {0}={1}'.format(config, config),
             "Couldn't add {} to your bash_rc, continue anyway?".format(config))

    cont('sudo chmod u+x {}'.format(BASE_DIR('bin/start_gunicorn.bash')),
         "Couldn't make script executable, continue anyway?")


    cont('sudo apt-get install python-dev',
         "Couldn't install python-dev, continue anyway?")
    cont('sudo apt-get install supervisor',
         "Couldn't install supervisord, continue anyway?")

    cont('sudo apt-get install nginx',
         "Couldn't install nginx, continue anyway?")

    cont('git push aws master',
         "Couldn't push application to AWS, continue anyway?")

    cont('mkdir -p {}'.format(BASE_DIR('logs')),
         "Couldn't create logs folder, continue anyway?")
    cont('touch {}'.format(BASE_DIR('logs', 'gunicorn_supervisor.log')),
         "Couldn't create gunicorn_supervisor log file, continue anyway?")

    cont('sudo supervisorctl reread',
         "Couldn't Reread supervisorctl, continue anyway?")

    cont('sudo supervisorctl update',
         "Couldn't update supervisorctl , continue anyway?")

    cont('sudo supervisorctl status',
         "Couldn't get supervisorctl status, continue anyway?")

    cont('sudo supervisorctl restart {{project_name}}',
         "Couldn't restart supervisorctl, continue anyway?")

    cont('sudo cp {} /etc/nginx/sites-available/{{project_name}}'.format(BASE_DIR('{{project_name}}',
                                                                                  'conf',
                                                                                  '{{project_name}}')),
         "Coundn't copy nginx config file into sites-available directory")

    cont('sudo ln -s /etc/nginx/sites-available/{{project_name}} /etc/nginx/sites-enabled/{{project_name}}',
         "Couldn't symlink nginx config, continue anyway?")

    cont('sudo service nginx start',
         "Couldn't start nginx, continue anyway?")



    makemigrations()
    migrate()

    # cont('%(run)s newrelic-admin validate-config - stdout' % env,
    #         "Couldn't initialize New Relic, continue anyway?")

########## END AWS MANAGEMENT


def update_code():
    with cd(BASE_DIR):
        local('pip freeze > requirements.txt')
        local('git add .')
        print(green("Enter your git commit comment: "))
        comment = raw_input()
        try:
            local('git commit -m "{}"'.format(comment))
        except Exception as e:
            print(red(e))

        run('git pull bitbucket master')
        local('git push -u bitbucket master')
        local('git push aws master')


def deploy():
    update_code()
    run('sudo service gunicorn restart')


def ss(port=8001):
    if env.hosts:
        run('sudo service gunicorn restart')
    else:
        local('foreman run ./manage.py runserver {}'.format(port))








