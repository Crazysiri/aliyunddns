from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.acs_exception.exceptions import ClientException
from aliyunsdkcore.acs_exception.exceptions import ServerException
from aliyunsdkalidns.request.v20150109.DescribeSubDomainRecordsRequest import DescribeSubDomainRecordsRequest
from aliyunsdkalidns.request.v20150109.DescribeDomainRecordsRequest import DescribeDomainRecordsRequest
import requests
from urllib.request import urlopen
import json

import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ipv4_flag = 1  # 是否开启ipv4 ddns解析,1为开启，0为关闭
ipv6_flag = 0  # 是否开启ipv6 ddns解析,1为开启，0为关闭


class AliDDNS():
    """docstring for ClassName"""
    def __init__(self, accessKeyId,accessSecret,domain,sub_domain):
        self._client = AcsClient(accessKeyId, accessSecret, 'cn-hangzhou')
        self._domain = domain
        self._sub_domain = sub_domain

    def update(self,RecordId, RR, Type, Value):  # 修改域名解析记录
        from aliyunsdkalidns.request.v20150109.UpdateDomainRecordRequest import UpdateDomainRecordRequest
        request = UpdateDomainRecordRequest()
        request.set_accept_format('json')
        request.set_RecordId(RecordId)
        request.set_RR(RR)
        request.set_Type(Type)
        request.set_Value(Value)
        response = self._client.do_action_with_exception(request)


    def add(self,DomainName, RR, Type, Value):  # 添加新的域名解析记录
        from aliyunsdkalidns.request.v20150109.AddDomainRecordRequest import AddDomainRecordRequest
        request = AddDomainRecordRequest()
        request.set_accept_format('json')
        request.set_DomainName(DomainName)
        request.set_RR(RR)  # https://blog.zeruns.tech
        request.set_Type(Type)
        request.set_Value(Value)
        response = self._client.do_action_with_exception(request)
    
    def do(self):
        domain = self._domain
        sub_domain = self._sub_domain
        ipv4_out = ""
        result = False
        if ipv4_flag == 1:
            request = DescribeSubDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_DomainName(domain)
            request.set_SubDomain(sub_domain + '.' + domain)
            response = self._client.do_action_with_exception(request)  # 获取域名解析记录列表
            domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的

            ip = urlopen('https://api-ipv4.ip.sb/ip').read()  # 使用IP.SB的接口获取ipv4地址
            ipv4 = str(ip, encoding='utf-8')
            ipv4_out = ipv4
            print("获取到IPv4地址：%s" % ipv4)

            if domain_list['TotalCount'] == 0:
                add(domain, sub_domain, "A", ipv4)
                print("新建域名解析成功")
                result = True
            elif domain_list['TotalCount'] == 1:
                if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv4.strip():
                    update(domain_list['DomainRecords']['Record'][0]['RecordId'], sub_domain, "A", ipv4)
                    result = True
                    print("修改域名解析成功")
                else:  # https://blog.zeruns.tech
                    print("IPv4地址没变")
            elif domain_list['TotalCount'] > 1:
                from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
                request = DeleteSubDomainRecordsRequest()
                request.set_accept_format('json')
                request.set_DomainName(domain)  # https://blog.zeruns.tech
                request.set_RR(sub_domain)
                response = self._client.do_action_with_exception(request)
                add(domain, sub_domain, "A", ipv4)
                print("修改域名解析成功")
                result = True

        if ipv6_flag == 1:
            request = DescribeSubDomainRecordsRequest()
            request.set_accept_format('json')
            request.set_DomainName(domain)
            request.set_SubDomain(sub_domain + '.' + domain)
            response = self._client.do_action_with_exception(request)  # 获取域名解析记录列表
            domain_list = json.loads(response)  # 将返回的JSON数据转化为Python能识别的

            ip = urlopen('https://api-ipv6.ip.sb/ip').read()  # 使用IP.SB的接口获取ipv6地址
            ipv6 = str(ip, encoding='utf-8')
            print("获取到IPv6地址：%s" % ipv6)

            if domain_list['TotalCount'] == 0:
                add(domain, sub_domain, "AAAA", ipv6)
                print("新建域名解析成功")
            elif domain_list['TotalCount'] == 1:
                if domain_list['DomainRecords']['Record'][0]['Value'].strip() != ipv6.strip():
                    update(domain_list['DomainRecords']['Record'][0]['RecordId'], sub_domain, "AAAA", ipv6)
                    print("修改域名解析成功")
                else:  # https://blog.zeruns.tech
                    print("IPv6地址没变")
            elif domain_list['TotalCount'] > 1:
                from aliyunsdkalidns.request.v20150109.DeleteSubDomainRecordsRequest import DeleteSubDomainRecordsRequest
                request = DeleteSubDomainRecordsRequest()
                request.set_accept_format('json')
                request.set_DomainName(domain)
                request.set_RR(sub_domain)  # https://blog.zeruns.tech
                response = self._client.do_action_with_exception(request)
                add(domain, sub_domain, "AAAA", ipv6)
                print("修改域名解析成功")
        return ipv4_out,result



