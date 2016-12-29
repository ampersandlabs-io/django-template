{{project_name}}
-----------------------

Setup virtual environment:

    mkvirtualenv [your_project_name]
    
    or 
    
    virtualenv [your_project_name]


Create django project:

    pip install django

    django-admin.py startproject --template=git@bitbucket.org:ampersandlabs-gh/django-template.git [your_project_name]

Install Dependencies:

    pip install -r requirements.txt [--upgrade]

Run project:

    python manage.py runserver
    