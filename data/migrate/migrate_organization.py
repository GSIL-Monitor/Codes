# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("migrate_organization", stream=True)
logger = loghelper.get_logger("migrate_organization")


conn = db.connect_torndb()


def main():
    # 正式用户
    # select id,name,active,trial,serviceEndDate from organization where trial is null;
    # update organization set serviceType=80003 where trial is null;

    # 试用用户
    # select id,name,active,trial,serviceEndDate from organization where trial='Y' and serviceEndDate is not null;
    # update organization set serviceType=80002 where trial='Y' and serviceEndDate is not null;

    # 服务结束用户
    # select id,name,active,trial,serviceEndDate from organization where trial is null and (serviceEndDate is null or serviceEndDate > '2018-06-20');
    # update organization set serviceStatus='Y' where trial is null and (serviceEndDate is null or serviceEndDate > '2018-06-20');
    # select id,name,active,trial,serviceEndDate from organization where trial='Y' and (serviceEndDate is not null and serviceEndDate > '2018-06-20');
    # update organization set serviceStatus='Y' where trial='Y' and (serviceEndDate is not null and serviceEndDate > '2018-06-20');
    pass


if __name__ == '__main__':
    main()