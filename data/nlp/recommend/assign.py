# coding=utf-8
__author__ = 'victor'

import os
import sys
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '..'))
sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../util'))
reload(sys)
sys.setdefaultencoding('utf-8')

import db as dbconn
from common import dbutil

from abc import abstractmethod
from random import choice


class Assigner(object):

    @abstractmethod
    def assign(self, *args):
        pass


class ColdcallAssigner(Assigner):

    def __init__(self):

        self.db = dbconn.connect_torndb()

    def assign(self, ccid):

        oid = dbutil.get_coldcall_infos(self.db, ccid).organizationId
        uids = dbutil.get_organization_watcher_users(self.db, oid, purpose='coldcall')
        if not uids:
            return

        uid = choice(uids)
        dbutil.update_coldcall_user(self.db, ccid, uid, 21020)
