#!/bin/sh

 DJANGODIR=/home/ubuntu/servers/{{project_name}}/

cd $DJANGODIR
source env/bin/activate

python manage.py "$@"