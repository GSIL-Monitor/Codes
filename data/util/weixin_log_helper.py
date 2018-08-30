# nohup /opt/py-env/bin/python /data/task-201606/util/weixin_log_helper.py > /data/task-201606/util/logs/wechat.log 2>&1 &
# scan the Qrcode in log remotely
# OR scp root@xiniudata-dev-01:/data/task-201606/util/QR.png ~/Downloads


import itchat
import os
import time
from datetime import datetime

import loghelper

loghelper.init_logger("weixin_log_helper", stream=True)
logger = loghelper.get_logger("weixin_log_help")

login_information = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'files/weixin_log_helper.pkl')


class WeChator(object):

    def __init__(self):

        global login_information, logger
        self.wechat = itchat.new_instance()
        self._update_status()

    def _update_status(self):

        self.load_status = self.wechat.load_login_status(login_information)
        self.load_status_code = self.load_status['BaseResponse']['Ret']
        self.alive = (self.load_status_code == 0)

    def init_login(self):

        # first time login
        if self.load_status_code == -1002:
            self.wechat.auto_login(hotReload=True, enableCmdQR=True, statusStorageDir=login_information)
            logger.info('First login, scan qr code')
        # login failed, relogin
        elif self.load_status_code == -1003:
            os.remove(login_information)
            self.wechat.auto_login(hotReload=True, enableCmdQR=True, statusStorageDir=login_information)
            logger.info('Fail to login')
        # login succeeded
        elif self.load_status_code == 0:
            logger.info('Login succeed')
        else:
            logger.exception('Other error')
        logger.info(str(self.load_status))

        self._update_status()

    def new_login(self):

        self.wechat.auto_login(hotReload=True, enableCmdQR=True, statusStorageDir=login_information)
        self._update_status()

    def get_friend_username(self, nickname):

        r = self.wechat.get_friends()
        r = filter(lambda x: x["NickName"] == nickname, r)
        if r:
            return r[0]["UserName"]
        else:
            return None

    def get_chatroom_username(self, nickname):

        r = self.wechat.get_chatrooms()
        r = filter(lambda x: x["NickName"] == nickname, r)
        if r:
            return r[0]["UserName"]
        else:
            return None

    def send_msg(self, msg, user):

        self.wechat.send_company_message_msg(msg=msg, toUserName=user)

    def is_alive(self):

        return self.wechat.alive

    def keep_alive(self):

        global login_information, logger
        while self.alive:
            try:
                self.wechat.send_company_message_msg(msg=str(datetime.now()), toUserName='filehelper')
            except Exception, e:
                logger.error(e, exc_info=True)
                break

            time.sleep(60)
            self.wechat.dump_login_status(login_information)
            self._update_status()
        logger.info("Need to relogin.")


if __name__ == "__main__":

    wc = WeChator()
    wc.init_login()
    wc.keep_alive()
