"""Management utilities."""

import os
import time
import yaml
from fabric.contrib.console import confirm
from fabric import api as fab
from fabric.api import task
from fabric.colors import green, red
import boto.ec2

########## GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

APP_CONFIG_FILE = BASE_DIR('conf', 'app_config.yml')
try:
    _CONFIGS = yaml.load(open(APP_CONFIG_FILE, 'r'))
    APP_CONFIG = _CONFIGS['APP']

    SECRET_KEY = APP_CONFIG.get('SECRET_KEY')
    AWS_REGION = APP_CONFIG.get('AWS_REGION')
    AWS_ACCESS_KEY = APP_CONFIG.get('AWS_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = APP_CONFIG.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = APP_CONFIG.get('AWS_STORAGE_BUCKET_NAME')
    DEBUG = APP_CONFIG.get('DEBUG')
    TEMPLATE_DEBUG = DEBUG
except:
    SECRET_KEY = os.environ.get('SECRET_KEY', '')
    AWS_REGION = os.environ.get('AWS_REGION')
    AWS_ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    DEBUG = os.environ.get('DEBUG')
    TEMPLATE_DEBUG = DEBUG

fab.env.run = 'python manage.py'

SERVER_USER = 'ubuntu'
SSH_KEY_FILE = '~/.ssh/{{project_name}}.pem' #Replace with path/to/your/.pem/key
DJANGO_SETTINGS_MODULE = '{{project_name}}.settings'

CONFIGS = (
    'DJANGO_SETTINGS_MODULE={{project_name}}.settings',
    'SECRET_KEY={0}'.format(SECRET_KEY),
    'AWS_REGION={0}'.format(AWS_REGION),
    'AWS_ACCESS_KEY_ID={0}'.format(AWS_ACCESS_KEY),
    'AWS_SECRET_ACCESS_KEY={0}'.format(AWS_SECRET_ACCESS_KEY),
    'AWS_STORAGE_BUCKET_NAME={0}'.format(AWS_STORAGE_BUCKET_NAME),
    'DEBUG={0}'.format(DEBUG),
    'TEMPLATE_DEBUG={0}'.format(TEMPLATE_DEBUG),
)


def aws_hosts():
    #connect to ec2
    conn = boto.ec2.connect_to_region(
        AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY
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


@task
def exists(path, d=None):
    """Check if file or directory exists"""
    with fab.settings(warn_only=True):
        if d is None:
            return fab.run('test -e {}'.format(path))
        else:
            return fab.run('test -d {}'.format(path))


@task
def pip_install(packages):
    """pip install packages"""
    if not exists('/usr/local/bin/pip'):
        fab.sudo('/usr/bin/easy_install pip')
    fab.run('pip install {}'.format(' '.join(packages)))
        
########## END HELPERS


########## DATABASE MANAGEMENT
@task
def create_database(db_user, db_pass, db):
    """Creates PostgreSQL role and database"""
    fab.sudo('psql -c "CREATE USER {0} WITH NOCREATEDB NOCREATEUSER " \
             "ENCRYPTED PASSWORD E\'{1}\'"'.format(db_user, db_pass),
             user='postgres')
    fab.sudo('psql -c "CREATE DATABASE {0} WITH OWNER {1}"'.format(db, db_user), 
             user='postgres')
    fab.run('echo export "{0}" >> .bashrc'.format(
        'DATABASE_URL=postgres://{0}:{0}@localhost:5432/{0}'.format(db_user, db_pass, db)
    ))


@task
def backup_db():
    for host in fab.env.hosts:
        date = time.strftime('%Y%m%d%H%M%S')
        fname = '/tmp/{host}-backup-{date}.xz'.format(**{
            'host': host,
            'date': date,
        })

        if exists(fname):
            fab.run('rm "{0}"'.format(fname))

        fab.sudo('cd; pg_dumpall | xz > {0}'.format(fname), user='postgres')

        fab.get(fname, os.path.basename(fname))
        fab.sudo('rm "{0}"'.format(fname), user='postgres')


@task
def makemigrations():
    """Create migrations."""
    fab.local('{} makemigrations'.format(fab.env.run))


@task
def migrate(app=None):
    """Apply one (or more) migrations. If no app is specified, fabric will
    attempt to run a site-wide migration.

    :param str app: Django app name to migrate.
    """
    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        with fab.prefix('source env/bin/activate'):
            if app:
                fab.run('{} migrate {} --settings={}'.format(fab.env.run, app,DJANGO_SETTINGS_MODULE))
            else:
                fab.run('{} migrate --settings={}'.format(fab.env.run, DJANGO_SETTINGS_MODULE))
                        
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    fab.local('{} collectstatic --noinput'.format('foreman run ./manage.py'))
########## END FILE MANAGEMENT


@task
def update_code(git_remote='production'):
    """Commit & push codebase to remotes"""
    fab.local('pip freeze > requirements.txt')
    fab.local('git add .')
    print(green('Commit message >>> '))
    msg = raw_input()
    l_cont('git commit -m "{}"'.format(msg), 'git commit failed, continue?')
    fab.local('git pull bitbucket master')
    fab.local('git push -u bitbucket master')
    fab.local('git push {} master'.format(git_remote))

    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        fab.run('git pull origin master')
        with fab.prefix('source env/bin/activate'):
            fab.run('pip install -r requirements.txt')


@task
def deploy():
    """Commit & push codebase to remotes, restart gunicorn server"""
    update_code()
    migrate()
    fab.sudo('supervisorctl status gunicorn | sed "s/.*[pid ]\([0-9]\+\)\,.*/\1/" | xargs kill -HUP')
    # fab.sudo('supervisorctl restart {{project_name}}')


@task
def setup_project():
    """Setup repo and allow deployment by git"""
    if not exists('/usr/bin/git'):
        fab.sudo('sudo apt-get install git')
    with fab.cd('/home/ubuntu/'):
        with fab.cd('git-repos/{{project_name}}.git'):
            fab.run('git init --bare')

        if not exists('/home/ubuntu/servers/{{project_name}}/', d=1):
            fab.run('mkdir -p servers/{{project_name}}')

        with fab.cd('servers/{{project_name}}/'):
            fab.run('git init')
            fab.run('git remote add origin /home/ubuntu/git-repos/{{project_name}}.git')
            fab.run('mkdir -p logs')
            fab.run('touch logs/gunicorn_supervisor.log')            
            fab.run('mkdir -p {{project_name}}/static')
            fab.run('mkdir -p {{project_name}}/templates')  
                      
    fab.local('git init')
    fab.local('git remote add bitbucket git@bitbucket.org:drewbrns/{{project_name}}.git')
    fab.local('git remote add production {{project_name}}:/home/ubuntu/git-repos/{{project_name}}.git')
    update_code()
    
    #Setup virtualenv
    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        fab.run('virtualenv env')
        with fab.prefix('source env/bin/activate'):
            fab.run('pip install -r requirements.txt')
    


@task
def update_nginx_conf():
    su_cont('cp /home/ubuntu/servers/{{project_name}}/{{project_name}}/conf/nginx.conf '
            '/etc/nginx/sites-available/{{project_name}}',
            "Couldn't copy nginx config file into sites-available directory")
            
    su_cont('ln -s /etc/nginx/sites-available/{{project_name}} /etc/nginx/sites-enabled/{{project_name}}',
            "Couldn't symlink nginx config, continue anyway?")            


@task 
def update_supervisord_conf():
    su_cont('cp /home/ubuntu/servers/{{project_name}}/{{project_name}}/conf/supervisord.conf '
            '/etc/supervisor/conf.d/{{project_name}}.conf',
            "Couldn't copy supervisor conf file, continue?")
            
    su_cont('supervisorctl reread',
            "Couldn't Reread supervisorctl, continue anyway?")

    su_cont('supervisorctl update',
            "Couldn't update supervisorctl , continue anyway?")

    su_cont('supervisorctl status',
            "Couldn't get supervisorctl status, continue anyway?")

    su_cont('supervisorctl restart {{project_name}}',
            "Couldn't restart supervisorctl, continue anyway?")
                        

@task
def update_gunicorn_start_script():
    su_cont('chmod u+x /home/ubuntu/servers/{{project_name}}/{{project_name}}/bash_scripts/gunicorn_start',
            "Couldn't make script executable, continue anyway?")


@task
def nginx(state='start'):
    su_cont('service nginx {}'.format(state),
            "Couldn't start nginx, continue anyway?")


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
    su_cont('apt-get update -y',
            "Couldn't update EC2 Instance, continue anyway?")

    #Upgrade ubuntu
    su_cont('apt-get upgrade -y',
            "Couldn't upgrade EC2 Instance, continue anyway?")

    #Add config to .bashrc
    for config in CONFIGS:
        cont('echo export ""{}"" >> ~/.bashrc'.format(config),
             "Couldn't add {} to your .bashrc, continue anyway?".format(config))

    cont('source ~/.bashrc', "Couldn't `source` .bashrc, continue anyway?")

    #Install postgreSQL & configue it to work with python/django
    su_cont('apt-get install postgresql postgresql-contrib -y',
            "Couldn't install PostgresSQL, continue anyway?")

    su_cont('apt-get install libpq-dev python-dev -y',
            "Couldn't configure postgres to work with django, continue anyway?")

    su_cont('apt-get install python-dev -y',
            "Couldn't install python-dev, continue anyway?")
            
    #Create db
    create_database('playgroun_admin', '{{project_name}}', '{{project_name}}_v1')

    #Install memcached
    su_cont('apt-get install memcached -y', 
            "Couldn't install memcached, continue anyway?")

    #Install python virtualenv
    su_cont('apt-get install python-virtualenv -y',
            "Couldn't install python-virtualenv, continue anyway?")

    setup_project()

    su_cont('apt-get install supervisor -y',
            "Couldn't install supervisord, continue anyway?")

    su_cont('apt-get install nginx -y',
            "Couldn't install nginx, continue anyway?")
            
    su_cont('sudo service nginx start',
            "Couldn't start nginx, continue anyway?")

    update_gunicorn_start_script()

    update_supervisord_conf()
    
    update_nginx_conf()
    
    nginx(state='restart')


########## END AWS MANAGEMENT

