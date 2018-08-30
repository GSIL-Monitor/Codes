from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

# 'root@192.168.1.208',
env.hosts = ['root@tshbao-task-01', 'root@192.168.1.208']

# env.hosts = []

def rsync():
    rsync_project(
            remote_dir="/data/task-v2/spider",
            local_dir="../data/spider/proxy",
            exclude=(".*", "*.pyc", '*.log'),
            delete=('proxy/')
            )
