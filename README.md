{{project_name}}
-----------------------

####Starting from scratch

Setup Virtual Environment:

    mkvirtualenv [your_project_name]
    
    or 
    
    virtualenv [your_project_name]


Create Django Project:

    pip install django

    django-admin.py startproject --template=git@bitbucket.org:ampersandlabs-gh/django-template.git [your_project_name]

#### Joining an on going project

Clone repo:

    git clone origin
     
     
#### Next Steps

Install Dependencies:

    pip install -r requirements.txt [--upgrade]

Setup Development Settings file
    
    rename .dev.example.py to .dev.py

Setup Environmental Variables:

    rename .env.example to .env and populate the missing keys.

Run project:

    gem install foreman #if not already installed
    
    foreman start -f Procfile.dev
    # tip: create an alias in your .bash_profile or .bash_rc and use it to start the server
    

Management tasks:
    
    fab deploy
    
    fab collectstatic:environment
    
    fab deploy_config:environment
    
--------
Helpful Info

[Python Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

[Install Foreman](https://github.com/ddollar/foreman)

[Foreman, Procfile & .env](https://mauricio.github.io/2014/02/09/foreman-and-environment-variables.html#isolating-the-configuration)