from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@xiniudata-task-01']


def rsync():
    rsync_project(
            remote_dir="/data/task-201606/",
            local_dir="../data/visit_control",
            exclude=(".*", "*.pyc", '*.log'),
            delete=('visit_control/')
            )