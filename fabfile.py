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
def start_sslcontainer(ip='0.0.0.0', port='80'):
    #migrate()
    local('nohup python3 manage.py runsslserver --certificate aicvs_server.pem --key aicvs_server.key {}:{} &'.format(ip, port))

@task
def do_test():
    local('python manage.py test')

@task
def display():
    local('sh goods/shelfdisplay/deamon.sh')

@task
def choose():
    local('sh goods/choose_goods/choose_goods_version_01/choose_goods_task.sh')

@task
def order():
    local('sh goods/sellgoods/shell/listener_order.sh')

@task
def auto():
    local('sh goods/shelfdisplay/deamon.sh')
    local('sh goods/choose_goods/choose_goods_version_01/choose_goods_task.sh')
    local('sh goods/sellgoods/shell/listener_order.sh')

