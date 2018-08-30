import os,sys

# sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../../../../util'))
# import loghelper
#
# loghelper.init_logger("crawler_crunchbase_company", stream=True)
# logger = loghelper.get_logger("crawler_crunchbase_company")

def __clear_brs():

    # gcs = map(lambda y: str(y[1]),
    #           filter(lambda x: int(x[2]) == 1,
    #                  [line.split() for line in os.popen('ps -ef |grep firefox').readlines()]))
    #
    # if gcs:
    #     logger.info(gcs)
    #     os.popen('kill %s' % ' '.join(gcs))

    for line in os.popen('ps -ef |grep firefox').readlines():
        vars = line.split()
        proc = ''.join(vars[7:])  # get proc description
        print(proc)
        if line.find('/root/firefox') == -1: continue
        pid = vars[1]  # get pid
        ppd = vars[2]
        print("here")
        print(pid)
        print("here")
        out = os.popen('kill ' + pid)
        out = os.popen('kill ' + ppd)


    print('clear firefox done')

    # gcs = map(lambda y: str(y[1]),
    #           filter(lambda x: int(x[2]) == 1,
    #                  [line.split() for line in os.popen('ps -ef | grep Xvfb').readlines()]))
    # if gcs:
    #     os.popen('kill %s' % ' '.join(gcs))
    #
    # logger.info('clear firefox done')

if __name__ == '__main__':
    __clear_brs()