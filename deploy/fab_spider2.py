from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@tshbao-task-01',
             'root@tshbao-task-02'
                ]

def rsync():
    rsync_project(
            remote_dir="/data/task-v2/",
            local_dir="../data/spider2",
            exclude=(".*", "*.pyc", '*.log', 'logs'),
            delete=('spider2/')
            )