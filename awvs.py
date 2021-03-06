#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests
import requests.packages.urllib3

'''
import requests.packages.urllib3.util.ssl_
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL'
or
pip install requests[security]
'''
requests.packages.urllib3.disable_warnings()
tarurl = "https://127.0.0.1:3443/"
apikey = "1986ad8c0a5b3df4d7028d5f3c06e936c813f5224bc874113907bfe199855f008"
headers = {"X-Auth": apikey, "content-type": "application/json"}


def addtask(url=''):
    # 添加任务
    data = {"address": url, "description": url, "criticality": "10"}
    try:
        response = requests.post(tarurl + "/api/v1/targets", data=json.dumps(data), headers=headers, timeout=30,
                                 verify=False)
        result = json.loads(response.content)
        return result['target_id']
    except Exception as e:
        print(str(e))
        return


def startscan(url):
    # 先获取全部的任务.避免重复
    # 添加任务获取target_id
    # 开始扫描
    '''
    11111111-1111-1111-1111-111111111112    High Risk Vulnerabilities
    11111111-1111-1111-1111-111111111115    Weak Passwords
    11111111-1111-1111-1111-111111111117    Crawl Only
    11111111-1111-1111-1111-111111111116    Cross-site Scripting Vulnerabilities
    11111111-1111-1111-1111-111111111113    SQL Injection Vulnerabilities
    11111111-1111-1111-1111-111111111118    quick_profile_2 0   {"wvs": {"profile": "continuous_quick"}}
    11111111-1111-1111-1111-111111111114    quick_profile_1 0   {"wvs": {"profile": "continuous_full"}}
    11111111-1111-1111-1111-111111111111    Full Scan   1   {"wvs": {"profile": "Default"}}
    '''
    targets = getscan()
    if url in targets:
        return "repeat"
    else:
        target_id = addtask(url)
        data = {"target_id": target_id, "profile_id": "11111111-1111-1111-1111-111111111111",
                "schedule": {"disable": False, "start_date": None, "time_sensitive": False}}
        try:
            response = requests.post(tarurl + "/api/v1/scans", data=json.dumps(data), headers=headers, timeout=30,
                                     verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return


def getstatus(scan_id):
    # 获取scan_id的扫描状况
    try:
        response = requests.get(tarurl + "/api/v1/scans/" + str(scan_id), headers=headers, timeout=30, verify=False)
        result = json.loads(response.content)
        status = result['current_session']['status']
        # 如果是completed 表示结束.可以生成报告
        if status == "completed":
            return getreports(scan_id)
        else:
            return result['current_session']['status']
    except Exception as e:
        print(str(e))
        return


def delete_scan(scan_id):
    # 删除scan_id的扫描
    try:
        response = requests.delete(tarurl + "/api/v1/scans/" + str(scan_id), headers=headers, timeout=30, verify=False)
        # 如果是204 表示删除成功
        if response.status_code == "204":
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return


def delete_target(scan_id):
    # 删除scan_id的扫描
    try:
        response = requests.delete(tarurl + "/api/v1/targets/" + str(scan_id), headers=headers, timeout=30,
                                   verify=False)
        # 如果是204 表示删除成功
        if response.status_code == "204":
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return


def stop_scan(scan_id):
    # 停止scan_id的扫描
    try:
        response = requests.post(tarurl + "/api/v1/scans/" + str(scan_id + "/abort"), headers=headers, timeout=30,
                                 verify=False)
        # 如果是204 表示停止成功
        if response.status_code == "204":
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return
def scan_status():
    # 停止scan_id的扫描
    try:
        response = requests.get(tarurl + "/api/v1/me/stats", headers=headers, timeout=30, verify=False)
        result = json.loads(response.content)
        print (result)
        return result
    except Exception as e:
        print(str(e))
        return


def getreports(scan_id):
    # 获取scan_id的扫描报告
    '''
    11111111-1111-1111-1111-111111111111    Developer
    21111111-1111-1111-1111-111111111111    XML
    11111111-1111-1111-1111-111111111119    OWASP Top 10 2013
    11111111-1111-1111-1111-111111111112    Quick
    '''
    data = {"template_id": "11111111-1111-1111-1111-111111111111",
            "source": {"list_type": "scans", "id_list": [scan_id]}}
    try:
        response = requests.post(tarurl + "/api/v1/reports", data=json.dumps(data), headers=headers, timeout=30,
                                 verify=False)
        result = response.headers
        report = result['Location'].replace('/api/v1/reports/', '/reports/download/')
        return tarurl.rstrip('/') + report
    except Exception as e:
        print(str(e))
        return
    finally:
        delete_scan(scan_id)


def config(url):
    target_id = addtask(url)
    # 获取全部的扫描状态
    data = {
        "excluded_paths": ["manager", "phpmyadmin", "testphp"],
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        "custom_headers": ["Accept: */*", "Referer:" + url, "Connection: Keep-alive"],
        "custom_cookies": [{"url": url,
                            "cookie": "UM_distinctid=15da1bb9287f05-022f43184eb5d5-30667808-fa000-15da1bb9288ba9; PHPSESSID=dj9vq5fso96hpbgkdd7ok9gc83"}],
        "scan_speed": "moderate",  # sequential/slow/moderate/fast more and more fast
        "technologies": ["PHP"],  # ASP,ASP.NET,PHP,Perl,Java/J2EE,ColdFusion/Jrun,Python,Rails,FrontPage,Node.js
        # 代理
        "proxy": {
            "enabled": False,
            "address": "127.0.0.1",
            "protocol": "http",
            "port": 8080,
            "username": "aaa",
            "password": "bbb"
        },
        # 无验证码登录
        "login": {
            "kind": "automatic",
            "credentials": {
                "enabled": False,
                "username": "test",
                "password": "test"
            }
        },
        # 401认证
        "authentication": {
            "enabled": False,
            "username": "test",
            "password": "test"
        }
    }
    try:
        res = requests.patch(tarurl + "/api/v1/targets/" + str(target_id) + "/configuration", data=json.dumps(data),
                             headers=headers, timeout=30 * 4, verify=False)

        data = {"target_id": target_id, "profile_id": "11111111-1111-1111-1111-111111111111",
                "schedule": {"disable": False, "start_date": None, "time_sensitive": False}}
        try:
            response = requests.post(tarurl + "/api/v1/scans", data=json.dumps(data), headers=headers, timeout=30,
                                     verify=False)
            result = json.loads(response.content)
            return result['target_id']
        except Exception as e:
            print(str(e))
            return
    except Exception as e:
        raise e

def getvulnerabilities():
    # 停止scan_id的扫描
    try:
        response = requests.get(tarurl + "/api/v1/vulnerabilities", headers=headers, timeout=30, verify=False)
        result = json.loads(response.content)
        print (result)
        return result
    except Exception as e:
        print(str(e))
        return
def getscan():
    # 获取全部的扫描状态
    targets = []
    try:
        response = requests.get(tarurl + "/api/v1/scans", headers=headers, timeout=30, verify=False)
        results = json.loads(response.content)
        return results
    except Exception as e:
        raise e
def getvulnerabilitiesinfo(sid):
    # 停止scan_id的扫描
    try:
        response = requests.get(tarurl + "/api/v1/vulnerabilities/"+sid, headers=headers, timeout=30, verify=False)
        result = json.loads(response.content)
        print (result)
        return result
    except Exception as e:
        print(str(e))
        return


if __name__ == '__main__':
    
    info=getscan()
    print (info)
    print (type(info))

    #print getreports('f22d4aa1-e2de-4307-bd9d-ddf3aa531bc1',locals())
   # print config('http://testhtml5.vulnweb.com/')
    