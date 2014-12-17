"""Management utilities."""

import os
import time
import yaml
from fabric.contrib.console import confirm
from fabric import api as fab
from fabric.api import task
from fabric.colors import green, red
import boto.ec2
from contextlib import contextmanager


########## GLOBALS
BASE_DIR = lambda *x: os.path.join(
    os.path.dirname(os.path.dirname(__file__)), *x)

APP_CONFIG_FILE = BASE_DIR('playground', 'playground', 'conf', 'app_config.yaml')
try:
    _CONFIGS = yaml.load(open(APP_CONFIG_FILE, 'r'))
    APP_CONFIG = _CONFIGS['APP']
except IOError:
    raise RuntimeError(
        """
        There was an error loading the application config file: %s \n
        Please make sure the file exists and does not contain errors \n.
        """ % APP_CONFIG_FILE
    )

SERVER_USER = 'ubuntu'
SSH_KEY_FILE = '~/.ssh/{{project_name}}.pem' #Replace with path/to/your/.pem/key
DJANGO_SETTINGS_MODULE = '{{project_name}}.settings'


def aws_hosts():
    #connect to ec2
    conn = boto.ec2.connect_to_region(
        APP_CONFIG.get('AWS_REGION'),
        aws_access_key_id=APP_CONFIG.get('AWS_ACCESS_KEY'),
        aws_secret_access_key=APP_CONFIG.get('AWS_SECRET_ACCESS_KEY')
    )

    reservations = conn.get_all_instances()

    instance_ids = []
    instance_ids_append = instance_ids.append
    for reservation in reservations:
        for i in reservation.instances:
            instance_ids_append(i.id)

    # Get the public CNAMES for those instances.
    hosts = []
    hosts_extend = hosts.extend
    for host in conn.get_all_instances(instance_ids):
        hosts_extend([i.public_dns_name for i in host.instances])
    hosts.sort() # Put them in a consistent order, so that calling code can do hosts[0] and hosts[1] consistently.
    return hosts


fab.env.hosts = aws_hosts()
fab.env.key_filename = SSH_KEY_FILE
fab.env.user = SERVER_USER
fab.env.run = 'python manage.py'
fab.env.psql_user = '{{project_name}}_admin'
fab.env.psql_password = '{{project_name}}'
fab.env.psql_db = '{{project_name}}_v1'
fab.env.venv_path = '/home/ubuntu/servers/{{project_name}}'
fab.env.proj_dirname = '/home/ubuntu/servers/{{project_name}}'
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


@task()
def update():
    """
    Update system
    """
    fab.sudo("apt-get update -y -q")
    fab.sudo("apt-get upgrade -y -q")


@contextmanager
def virtualenv():
    """
    Runs commands within the project's virtualenv.
    """
    with fab.cd(fab.env.venv_path): # /home/ubuntu/servers/django_base
        with fab.prefix("source {}/env/bin/activate".format(fab.env.venv_path)):
            yield


@contextmanager
def project():
    """
    Runs commands within the project's directory.
    """
    with virtualenv():
        with fab.cd(fab.env.proj_dirname):
            yield


@task
def pip_install(packages):
    """pip install packages"""
    if not exists('/usr/local/bin/pip'):
        fab.sudo('/usr/bin/easy_install pip')
    with virtualenv():
        fab.run('pip install {}'.format(' '.join(packages)))

########## END HELPERS


########## DATABASE MANAGEMENT
@task
def create_database():
    """Creates PostgreSQL role and database"""
    with fab.cd('/home/ubuntu/servers/{{project_name}}/{{project_name}}/conf'):

        try:
            config = yaml.load(open('app_config.yaml', 'r'))
            db_configs = {
                'DATABASE_URL': '"postgres://{0}:{1}@localhost:5432/{2}"'.format(
                    fab.env.psql_user, fab.env.psql_password, fab.env.psql_db
                ),
                'TEST_DATABASE_URL': '"postgres://{0}:{1}@localhost:5432/{2}_test"'.format(
                    fab.env.psql_user, fab.env.psql_password, fab.env.psql_db
                ),
            }

            fab.sudo('psql -c "CREATE USER {0} WITH ENCRYPTED PASSWORD E\'{1}\' NOCREATEDB NOCREATEUSER "'.format(
                fab.env.psql_user, fab.env.psql_password),
                user='postgres'
            )

            fab.sudo('psql -c "CREATE DATABASE {0} WITH OWNER {1}"'.format(
                fab.env.psql_db, fab.env.psql_user),
                user='postgres'
            )

            #Test database
            fab.sudo('psql -c "CREATE DATABASE {0}_test WITH OWNER {1}"'.format(
                fab.env.psql_db, fab.env.psql_user),
                user='postgres'
            )

            config['APP'] = db_configs

            yaml.dump(config, open('app_config.yaml', 'w'))
        except IOError:
            raise RuntimeError(
                """
                There was an error loading the application config file: %s \n
                Please make sure the file exists and does not contain errors \n.
                """ % APP_CONFIG_FILE
            )


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
                fab.run('{} migrate {} --settings={}'.format(fab.env.run, app, DJANGO_SETTINGS_MODULE))
            else:
                fab.run('{} migrate --settings={}'.format(fab.env.run, DJANGO_SETTINGS_MODULE))
                        
########## END DATABASE MANAGEMENT


########## FILE MANAGEMENT
@task
def collectstatic():
    """Collect all static files, and copy them to S3 for production usage."""
    fab.local('{} collectstatic --noinput'.format(fab.env.run))
########## END FILE MANAGEMENT

@task
def restart():
    """
    Reload nginx/gunicorn
    """
    with fab.settings(warn_only=True):
        fab.sudo("supervisorctl restart {{project_name}}")
        fab.sudo('/etc/init.d/nginx reload')


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
        with virtualenv():
            fab.run('pip install -r requirements.txt')


@task
def deploy():
    """Commit & push codebase to remotes, restart gunicorn server"""
    update_code()
    migrate()
    with fab.settings(warn_only=True):
        fab.sudo('supervisorctl restart {{project_name}}')
        fab.sudo('/etc/init.d/nginx reload')


@task
def setup_project(git_remote='production'):
    """Setup repo and allow deployment by git"""
    if not exists('/usr/bin/git'):
        fab.sudo('sudo apt-get install git -y')
        fab.run('mkdir -p git-repos/{{project_name}}.git')
        fab.run('mkdir -p servers/{{project_name}}')
    with fab.cd('/home/ubuntu/'):
        with fab.cd('/home/ubuntu/git-repos/{{project_name}}.git'):
            fab.run('git init --bare')
        with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
            fab.run('git init')
            fab.run('virtualenv env') #Setup virtualenv
            fab.run('git remote add origin /home/ubuntu/git-repos/{{project_name}}.git')
            fab.run('mkdir -p logs')
            fab.run('touch logs/gunicorn_supervisor.log')
            fab.run('touch logs/nginx-access.log')
            fab.run('touch logs/nginx-error.log')
            fab.run('mkdir -p {{project_name}}/static')
            fab.run('mkdir -p {{project_name}}/templates')

            #Create app_config.yaml, export app configs
            fab.run('touch {{project_name}}/conf/app_config.yaml')
            config = {'APP': {
                'DJANGO_SETTINGS_MODULE': 'playground.settings',
                'SECRET_KEY': '"'+APP_CONFIG.get('SECRET_KEY')+'"',
                'AWS_REGION': '"'+APP_CONFIG('AWS_REGION')+'"',
                'AWS_ACCESS_KEY_ID': '"'+APP_CONFIG('AWS_ACCESS_KEY')+'"',
                'AWS_SECRET_ACCESS_KEY': '"'+APP_CONFIG('AWS_SECRET_ACCESS_KEY')+'"',
                'AWS_STORAGE_BUCKET_NAME': '"'+APP_CONFIG('AWS_STORAGE_BUCKET_NAME')+'"',
                'DEBUG': APP_CONFIG('DEBUG'),
                'TEMPLATE_DEBUG': APP_CONFIG('TEMPLATE_DEBUG'),
                'REDIS_URL': '/var/run/redis/redis.sock',
                'DEFAULT_REDISDB': '&default_rdb 0',
            }}
            yaml.dump(config, open('{{project_name}}/conf/app_config.yaml', 'w'))

    fab.local('git init')
    fab.local('git remote add bitbucket git@bitbucket.org:drewbrns/{{project_name}}.git') #replace with actual bitbucket url
    fab.local('git remote add production {{project_name}}:/home/ubuntu/git-repos/{{project_name}}.git')
    fab.local('pip freeze > requirements.txt')
    fab.local('git add .gitignore')
    fab.local('git commit -m"Add .gitignore"')
    fab.local('git add .')
    fab.local('git commit -m"Initial project setup"')
    fab.local('git push -u bitbucket master')
    fab.local('git push -u bitbucket master')
    fab.local('git push -u {} master'.format(git_remote))
    fab.local('git push -u {} master'.format(git_remote))

    with fab.cd('/home/ubuntu/servers/{{project_name}}/'):
        fab.run('git pull origin master')
        with virtualenv():
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

    # #Append app's environmental variables to supervisord conf file
    # su_cont('echo %s >> /etc/supervisor/conf.d/playground.conf' % str((','+','.join(CONFIGS))),
    #         "Couldn't appead enviromental variables to playground.conf, continue anyway?")

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
    su_cont('service nginx {0}'.format(state),
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

    #Install postgreSQL & configue it to work with python/django
    su_cont('apt-get install postgresql postgresql-contrib -y',
            "Couldn't install PostgresSQL, continue anyway?")

    su_cont('apt-get install libpq-dev python-dev -y',
            "Couldn't configure postgres to work with django, continue anyway?")

    su_cont('apt-get install python-dev -y',
            "Couldn't install python-dev, continue anyway?")
            
    #Create db
    create_database()

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

    collectstatic()
    # migrate()

    restart()


########## END AWS MANAGEMENT


@task
def integrate_logentries():
    fab.run('wget https://raw.githubusercontent.com/logentries/le/master/install/linux/logentries_install.sh')
    fab.sudo('bash logentries_install.sh')


@task
def install_redis():
    fab.sudo('apt-get install redis-server -y')