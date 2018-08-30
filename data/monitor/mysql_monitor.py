# -*- coding: utf-8 -*-
import os, sys
import datetime, time

reload(sys)
sys.setdefaultencoding("utf-8")

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import loghelper, db

#logger
loghelper.init_logger("mysql_monitor", stream=True)
logger = loghelper.get_logger("mysql_monitor")

WEBS = [
    "10.25.143.108",    # xiniudata-openapi-01
    "10.27.73.101",     # xiniudata-openapi-02
    "10.27.73.209",     # xiniudata-web-01
    "10.27.73.237",     # xiniudata-web-02
    "10.27.78.81",      # xiniudata-personal-01
    "10.27.80.140",     # xiniudata-personal-02
]

def main():
    conn = db.connect_torndb()
    items = conn.query("show full processlist")
    for item in items:
        Command = item["Command"]
        if Command == "Sleep":
            continue

        Id = item["Id"]
        Info = item["Info"]
        Host = item["Host"]
        Time = item["Time"]
        if Time is None:
            continue

        temps = Host.split(":")
        Host = temps[0]
        if Host not in WEBS:
            continue

        if Time >= 2:
            logger.info("id: %s, info:%s, host: %s, time: %s", Id, Info, Host, Time)
            conn.execute("kill %s" % Id)
    conn.close()


if __name__ == "__main__":
    while True:
        main()
        time.sleep(1)