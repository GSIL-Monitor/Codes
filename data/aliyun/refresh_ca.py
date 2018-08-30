# -*- coding: utf-8 -*-
import os, datetime
import json
import sys
from aliyunsdkcore import client
from aliyunsdkslb.request.v20140515 import UploadServerCertificateRequest
from aliyunsdkslb.request.v20140515 import DescribeLoadBalancerHTTPSListenerAttributeRequest
from aliyunsdkslb.request.v20140515 import SetLoadBalancerHTTPSListenerAttributeRequest

AK = "LTAIYT13z6IqNsrr"
SECRET = "nwlUs3HiDU62lZyagTPFECt3mKRmzL"
REGION = "cn-beijing"
SLB = "lb2zeoqxj84s246eeron"

def upload():
    s_ca_fp = open("/etc/letsencrypt/live/xiniudata.com/fullchain.pem")
    s_ca = s_ca_fp.read()
    s_ca_fp.close()
    p_ca_fp = open("/etc/letsencrypt/live/xiniudata.com/rsa_privkey.pem")
    p_ca = p_ca_fp.read()
    p_ca_fp.close()
    now = datetime.datetime.now()
    clt = client.AcsClient(AK, SECRET, REGION)
    request = UploadServerCertificateRequest.UploadServerCertificateRequest()
    request.set_accept_format("json")
    request.set_ServerCertificate(s_ca)
    request.set_PrivateKey(p_ca)
    request.set_ServerCertificateName(now.strftime("%Y%m%d_%H%M%S"))
    result = clt.do_action_with_exception(request)
    data = json.loads(result)
    print data
    ServerCertificateId = data["ServerCertificateId"]
    return ServerCertificateId


def get_attribute():
    clt = client.AcsClient(AK, SECRET, REGION)
    request = DescribeLoadBalancerHTTPSListenerAttributeRequest.DescribeLoadBalancerHTTPSListenerAttributeRequest()
    request.set_accept_format("json")
    request.set_LoadBalancerId(SLB)
    request.set_ListenerPort(443)
    result = clt.do_action_with_exception(request)
    data = json.loads(result)
    print data
    return data

def set_attribute(data, ServerCertificateId):
    # {"
    # ServerCertificateId":"1560561242368936_15a9491fb86",
    # "XForwardedFor_SLBID":"off",
    # "Gzip":"on",
    # "Scheduler":"wrr",
    # "StickySession":"off",
    # "XForwardedFor_SLBIP":"off",
    # "XForwardedFor_proto":"off",
    # "Bandwidth":1,
    # "HealthCheck":"off",
    # "ListenerPort":443,
    # "Status":"running",
    # "XForwardedFor":"on",
    # "RequestId":"776F8751-3A39-4D7F-A14F-4DE02B7F26D6",
    # "BackendServerPort":80}

    clt = client.AcsClient(AK, SECRET, REGION)
    request = SetLoadBalancerHTTPSListenerAttributeRequest.SetLoadBalancerHTTPSListenerAttributeRequest()
    request.set_accept_format("json")
    request.set_LoadBalancerId(SLB)
    request.set_ListenerPort(443)
    request.set_Bandwidth(data["Bandwidth"])
    request.set_XForwardedFor(data["XForwardedFor"])
    request.set_Scheduler(data["Scheduler"])
    request.set_StickySession(data["StickySession"])
    request.set_HealthCheck(data["HealthCheck"])
    request.set_HealthCheckURI(data["HealthCheckURI"])
    request.set_HealthCheckTimeout(data["HealthCheckTimeout"])
    request.set_ServerCertificateId(ServerCertificateId)

    result = clt.do_action_with_exception(request)
    data = json.loads(result)
    print data


def refresh_ca():
    # output = os.popen("certbot --dry-run renew")
    output = os.popen("certbot renew")
    result = output.read()
    print result
    if "No renewals were attempted" in result:
        return False
    if "Congratulations, all renewals succeeded" in result:
        output = os.popen("openssl rsa -in /etc/letsencrypt/live/xiniudata.com/privkey.pem -out /etc/letsencrypt/live/xiniudata.com/rsa_privkey.pem")
        print(output.read())
        return True
    else:
        return False

def main():
    print "Begin..."
    print datetime.datetime.now()
    if len(sys.argv) == 1:
        flag = refresh_ca()
        if flag is False:
            print "End."
            exit()
    ServerCertificateId = upload()
    print "ServerCertificateId: %s" % ServerCertificateId
    data = get_attribute()
    set_attribute(data, ServerCertificateId)
    print "End."

if __name__ == "__main__":
    main()