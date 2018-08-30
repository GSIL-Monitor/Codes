from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@tshbao-task-01']

def commit():
    code_dir = '../'
    with cd(code_dir):
        local("git add . && git commit -m 'update from fabric'")

def push():
    local("git push origin master")

def upload():
    commit()
    push()

