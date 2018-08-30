from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@xiniudata-web-01', 'root@xiniudata-web-02']


def rsync():
    rsync_project(
            remote_dir="/var/www/",
            local_dir="../web/oss-fileserver",
            exclude=(".*", "*.pyc", '*.log','logs','node_modules'),
            delete=('oss-fileserver/')
            )