from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

env.hosts = ['root@xiniudata-dev-01']


def rsync():
    rsync_project(
            remote_dir="/var/www/",
            local_dir="../web/node-websocket-server",
            exclude=(".*", "node_modules", 'logs', 'config.js'),
            delete=('node-websocket-server/')
            )