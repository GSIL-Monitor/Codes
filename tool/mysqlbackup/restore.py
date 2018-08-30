# -*- coding: utf-8 -*-
import os, sys
import datetime
import paramiko


def main():
    today = datetime.datetime.now()
    if os.path.exists("/data/backup/mysql/data.sql"):
        os.remove("/data/backup/mysql/data.sql")
    if os.path.exists("/data/backup/mysql/data.sql.gz"):
        os.remove("/data/backup/mysql/data.sql.gz")

    t = paramiko.Transport(("10.27.74.15", 22))
    t.connect(username='mysqlbackup', password='tq6xd9c1qy')
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get("/data/backup/mysql/xiniu_%s.sql.gz" % today.strftime("%Y-%m-%d"), "/data/backup/mysql/data.sql.gz")
    t.close()

    os.system("cd /data/backup/mysql; gunzip data.sql.gz")
    os.system("cd /data/backup/mysql; mysql -uroot --default-character-set=utf8 tsb_v2_test < data.sql")


if __name__ == '__main__':
    main()