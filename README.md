{{project_name}}
-----------------------

#### To Begin

Setup Virtual Environment:

    mkvirtualenv [your_project_name]
    
    or 
    
    virtualenv [your_project_name]

####Start from scratch

Create Django Project:

    pip install django

    django-admin.py startproject --template=https://github.com/ampersandlabs-io/django-template/archive/master.zip [your_project_name]

#### Join an on going project

Clone repo:

    git clone origin
     
     
#### Next Steps

Install Dependencies:

    pip install -r requirements/base.txt [--upgrade]
    pip install -r requirements/dev.txt [--upgrade]

Setup Development Settings file
    
    rename .dev.example.py to .dev.py

Setup Environmental Variables:

    rename .env.example to .env and populate the missing keys.
    
    #it's important it follows this format
    AWS_ACCESS_KEY_ID=this-is-some-access-key
    

Run project:

    gem install foreman #if not already installed
    
    # setup your Procfile.dev, then. 
        
    fab start
    

Management tasks:

    fab start
    
    fab mg_cmd:command
    
    fab update_code:branch # if not provided it picks the current branch
    
    fab collectstatic:environment
    
    fab deploy_config:environment
    
--------
Helpful Info

[Python Virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/install.html)

[Install Foreman](https://github.com/ddollar/foreman)

[Foreman, Procfile & .env](https://mauricio.github.io/2014/02/09/foreman-and-environment-variables.html#isolating-the-configuration)