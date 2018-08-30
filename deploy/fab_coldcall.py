from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@tshbao-task-01']

def rsync():
    rsync_project(
            remote_dir="/data/task-v2/",
            local_dir="../data/coldcall",
            exclude=(".*", "*.pyc", '*.log'),
            delete=('coldcall/')
            )