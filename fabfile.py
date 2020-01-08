import os, sys
from fabric.api import task, local

@task
def migrate():
    local('python manage.py makemigrations')
    local('python manage.py migrate')

@task
def start_container(ip='0.0.0.0', port='80'):
    #migrate()
    local('nohup python3 manage.py runserver {}:{} &'.format(ip, port))

@task
def do_test():
    local('python manage.py test')

@task
def display():
    local('sh goods/shelfdisplay/deamon.sh')