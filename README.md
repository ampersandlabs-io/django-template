{{project_name}}
-----------------------

Start new project:

    django-admin.py startproject --template=git@bitbucket.org:ampersandlabs-gh/django-template.git [your_project_name]

Setup project:
    
    setup virtual environment of your choice:
    
    mkvirtualenv [your_project_name]
    
    or 
    
    virtualenv [your_project_name]

    pip install -r requirements.txt

    fab init()

Run project:

    python manage.py runserver
    