"""Management utilities."""

import os
from fabric.contrib.console import confirm
from fabric import api as fab
from fabric.api import task
from fabric.colors import green, red
import boto.ec2

########## GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

fab.env.run = 'python manage.py'

SERVER_USER = 'ubuntu'
SSH_KEY_FILE = './ssh/' #Replace with path/to/your/.pem/key

CONFIGS = (
    'DJANGO_SETTINGS_MODULE={{project_name}}.settings',
    'SECRET_KEY={0}'.format(os.environ.get('SECRET_KEY', '')),
    'AWS_REGION={0}'.format(os.environ.get('AWS_REGION', '')),
    'AWS_ACCESS_KEY_ID={0}'.format(os.environ.get('AWS_S3_ACCESS_KEY_ID', '')),
    'AWS_SECRET_ACCESS_KEY={0}'.format(os.environ.get('AWS_S3_SECRET_ACCESS_KEY', '')),
    'AWS_STORAGE_BUCKET_NAME={0}'.format(os.environ.get('AWS_STORAGE_BUCKET_NAME', '')),
    'DATABASE_URL={0}'.format(os.environ.get('DATABASE_URL', '')),
    'DEBUG={0}'.format(os.environ.get('DEBUG', '')),
    'TEMPLATE_DEBUG={0}'.format(os.environ.get('TEMPLATE_DEBUG', '')),
)


def aws_hosts():
    #connect to ec2
    conn = boto.ec2.connect_to_region(
        os.environ.get('AWS_REGION'),
        aws_access_key_id=os.environ.get('AWS_S3_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_S3_SECRET_ACCESS_KEY')
    )

    reservations = conn.get_all_instances()

    instance_ids = []
    for reservation in reservations:
        for i in reservation.instances:
            instance_ids.append(i.id)

    # Get the public CNAMES for those instances.
    hosts = []
    for host in conn.get_all_instances(instance_ids):
        hosts.extend([i.public_dns_name for i in host.instances])
    hosts.sort() # Put them in a consistent order, so that calling code can do hosts[0] and hosts[1] consistently.

    return hosts


fab.env.hosts = aws_hosts()
fab.env.key_filename = SSH_KEY_FILE
fab.env.user = SERVER_USER
# fab.env.parallel = True


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
        result = fab.run(cmd, capture=True)

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
        result = fab.local(cmd)

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
def makemigrations():
    """Setup database."""
    fab.local('{} makemigrations'.format(fab.env.run))


@task
def migrate(app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app name to migrate.
    """
    if app:
        fab.local('{} migrate {}'.format(fab.env.run, app))
    else:
        fab.local('{} migrate '.format(fab.env.run))


@task
def createsuperuser():
    fab.local('{} createsuperuser'.format(fab.env.run))
    # if fab.env.hosts:
    #     fab.run('{} createsuperuser'.format(fab.env.run))

########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    fab.local('{} collectstatic --noinput'.format(fab.env.run))
########## END FILE MANAGEMENT


@task
def update_code():
    fab.local('pip freeze > requirements.txt')
    fab.local('git add .')
    print(green('Commit message >>> '))
    msg = raw_input()
    l_cont('git commit -m "{}"'.format(msg), 'git commit failed, continue?')
    fab.local('git pull bitbucket master')
    fab.local('git push -u bitbucket master')
    fab.local('git push production master')

    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        fab.run('git pull origin master')


@task
def deploy():
    update_code()
    fab.sudo('service gunicorn restart')


@task
def setup_repo():
    #Setup repo and allow deployment by git
    if not exists('/usr/bash_scripts/git'):
        fab.sudo('sudo apt-get install git')
    with fab.cd('/home/ubuntu/'):
        fab.run('mkdir -p git-repos/{{project_name}}.git')
        fab.cd('git-repos/{{project_name}}.git')
        fab.run('git init --bare')

        if not exists('/home/ubuntu/servers/{{project_name}}/', d=1):
            fab.run('mkdir -p servers/{{project_name}}')

        with fab.cd('servers/{{project_name}}/'):
            fab.run('git init')
            fab.run('git remote add origin /home/ubuntu/git-repos/{{project_name}}.git')
            fab.run('mkdir -p {{project_name}}/static')
            fab.run('mkdir -p {{project_name}}/templates')
    fab.local('git init')
    fab.local('git remote add bitbucket git@bitbucket.org:{{project_name}}.git') #replace
    fab.local('git remote add production {{project_name}}:/home/ubuntu/git-repos/{{project_name}}.git')
    update_code()


@task
def exists(path, d=None):
    with fab.settings(warn_only=True):
        if d is None:
            return fab.run('test -e {}'.format(path))
        else:
            return fab.run('test -d {}'.format(path))

@task
def pip_install(packages):
    if not exists('/usr/local/bash_scripts/pip'):
        fab.sudo('/usr/bash_scripts/easy_install pip')
    fab.run('pip install {}'.format(' '.join(packages)))


def postgres():
    pass


def nginx(state='start'):
    pass


def gunicorn(state='start'):
    pass




########## AWS SETUP
@task
def bootstrap():
    """Bootstrap your new application:

        - Update & Upgrade EC2 Instance.
        - Install all ``tools & packages``.
        - Sync the database.
        - Apply all database migrations.
        - Initialize New Relic's monitoring add-on.
    """
    #Update ubuntu
    su_cont('apt-get update',
            "Couldn't update EC2 Instance, continue anyway?")

    #Upgrade ubuntu
    su_cont('apt-get upgrade',
            "Couldn't upgrade EC2 Instance, continue anyway?")

    #Add config to .bashrc
    for config in CONFIGS:
        cont('echo export "{0}" >> ~/.bashrc'.format(config),
             "Couldn't add {} to your .bashrc, continue anyway?".format(config))

    cont('source ~/.bashrc', "Couldn't `source` .bashrc, continue anyway?")

    #Install postgreSQL
    su_cont('apt-get install postgresql postgresql-contrib',
            "Couldn't install PostgresSQL, continue anyway?")

    # sudo_cont('sudo su - postgres', "Couldn't login as postgres")

    setup_repo()

    # push local source files to remote instance
    # update_code()

    #Install python virtualenv
    su_cont('apt-get install python-virtualenv',
            "Couldn't install python-virtualenv, continue anyway?")

    #Setup virtualenv
    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        fab.run('virtualenv env')
        with fab.prefix('source env/bash_scripts/activate'):
            fab.run('pip install -r requirements.txt')

    #Configure postgres to work with python
    su_cont('apt-get install libpq-dev python-dev',
            "Couldn't configure postgres to work with django, continue anyway?")

    su_cont('apt-get install python-dev',
            "Couldn't install python-dev, continue anyway?")

    #Install Supervisor
    su_cont('apt-get install supervisor',
            "Couldn't install supervisord, continue anyway?")

    #Install nginx
    su_cont('apt-get install nginx',
            "Couldn't install nginx, continue anyway?")

    #Create supservisor log file
    with fab.cd('/home/ubuntu/servers/{{project_name}}'):
        fab.run('mkdir -p logs')
        fab.run('touch logs/gunicorn_supervisor.log')

    su_cont('cp /home/ubuntu/servers/{{project_name}}/{{project_name}}/conf/nginx '
            '/etc/nginx/sites-available/{{project_name}}',
            "Couldn't copy nginx config file into sites-available directory")

    su_cont('ln -s /etc/nginx/sites-available/{{project_name}} /etc/nginx/sites-enabled/{{project_name}}',
            "Couldn't symlink nginx config, continue anyway?")

    su_cont('cp /home/ubuntu/servers/{{project_name}}/{{project_name}}/conf/supervisord '
            '/etc/supervisor/conf.d/{{project_name}}.conf',
            "Couldn't copy supervisor conf file, continue?")

    su_cont('chmod u+x /home/ubuntu/servers/{{project_name}}/{{project_name}}/bash_scripts/gunicorn_start',
            "Couldn't make script executable, continue anyway?")

    migrate()

    su_cont('service nginx start',
            "Couldn't start nginx, continue anyway?")

    su_cont('supervisorctl reread',
            "Couldn't Reread supervisorctl, continue anyway?")

    su_cont('sudo supervisorctl update',
            "Couldn't update supervisorctl , continue anyway?")

    su_cont('sudo supervisorctl status',
            "Couldn't get supervisorctl status, continue anyway?")

    su_cont('sudo supervisorctl restart {{project_name}}',
            "Couldn't restart supervisorctl, continue anyway?")

########## END AWS MANAGEMENT

