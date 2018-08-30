from __future__ import with_statement
from fabric.api import *
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

# env.hosts = ['root@tshbao-web-01', 'root@tshbao-mongodb-01', 'root@xiniudata-dev-01']
#
#
# def rsync():
#     rsync_project(
#             remote_dir="/var/www/tsb2/search",
#             local_dir="../data/",
#             exclude=(".*", "*.pyc", '*.log', 'spider', 'spider2', 'endorse',
#                      'geetest', 'main.conf', 'monitor', 'tmp', 'models'),
#             delete=('search/')
#             )

env.hosts = ['root@xiniudata-web-01', 'root@xiniudata-web-02', 'root@xiniudata-search-01', 'root@xiniudata-search-02']
# env.hosts = ['root@xiniudata-web-02', 'root@xiniudata-dev-01']


def rsync():
    rsync_project(
            remote_dir="/var/www/tsb201607/search",
            local_dir="../data/",
            exclude=(".*", "*.pyc", '*.log', 'spider', 'spider2', 'endorse', 'sms', 'patch',
                     'geetest', 'main.conf', 'monitor', 'tmp', 'models', 'recommend/cach', 'logs'),
            delete=('search/')
            )