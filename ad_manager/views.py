# -*- coding: utf-8 -*-
from django.shortcuts import render
from common.mymako import render_json
import json
from ldap3 import Server, Connection, ALL, NTLM
from datetime import datetime
import time
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from django.conf import settings

# 开发框架中通过中间件默认是需要登录态的，如有不需要登录的，可添加装饰器login_exempt
# 装饰器引入 from blueapps.account.decorators import login_exempt

# start_time = time.time() - 30 * 24 * 60 * 60 + 11644473600
# start_time2 = time.time() - 15 * 24 * 60 * 60 + 11644473600  # 默认45天


def home(request):
    """
    首页
    """
    return render(request, 'ad_manager/home.html')


def index(request):
    """
    测试索引页
    """
    return render(request, 'index.html')


def contact(request):
    """
    联系我们
    """
    return render(request, 'ad_manager/contact.html')


def search_statistic_data(request):
    """查询统计数据"""
    condition = json.loads(request.body)['condition']
    domain = condition.get('domain', 'corp.gwm.cn')
    ldap_conn = get_ldap_connection(domain)
    result_list = []
    for i in range(8):
        inner_count = search_metric_value(domain, ldap_conn, i)
        result_list.append(inner_count)
    return render_json({'result': True, 'message': result_list})


def search_statistic_data2(request):
    """查询统计数据"""
    condition = json.loads(request.body)['condition']
    domain = condition.get('domain', 'corp.gwm.cn')
    ldap_conn = get_ldap_connection(domain)
    result_list = [['amount', 'usertype']]
    metrics = ['从未登录过', '最近30天内登录', '30天内密码即将过期', '组数量', '安全组', '通讯组', '无成员组', '组织单位']
    for i in range(8, 17):
        if i == 11:
            result_list.append(['amount', 'grouptype'])
            continue
        elif i > 11:
            inner_count = search_metric_value(domain, ldap_conn, i-1)
            result_list.append([inner_count, metrics[i-9]])
        else:
            inner_count = search_metric_value(domain, ldap_conn, i)
            result_list.append([inner_count, metrics[i-8]])

    return render_json({'result': True, 'message': result_list})


def search_reports_dataset(request):
    """查询详情，返回列表"""
    condition = json.loads(request.body)['condition']
    domain = condition.get('domain', 'corp.gwm.cn')
    report_type = condition.get('report_type', ['account_reports', 'forbidden_user'])
    checked_attrs = condition.get('checkedAttrs', None)
    attr_list = []
    report_fields_ = []
    if checked_attrs is None:
        attr_list = condition.get('attr_list', ['displayName', 'name', 'mail', 'department', 'company', 'whenCreated'])
    else:
        for checkedAttr in checked_attrs:
            for item in report_fields:
                if checkedAttr == item['value']:
                    attr_list += [item['name']]
                    report_fields_.append(item)
    page = condition.get('page', 1)
    page_size = condition.get('page_size', 10)
    ldap_conn = get_ldap_connection(domain)
    basedn = "ou=sites,dc={0},dc=gwm,dc=com".format(domain.split('.')[0])
    start_end_date = condition.get('start_end_date', None)
    if start_end_date:
        filter_ = generate_filter_string(report_type, start_end_date[0], start_end_date[1])
    else:
        filter_ = generate_filter_string(report_type, None, None)
    print(filter_)
    result_list_ = generate_report_dataset(ldap_conn, basedn, filter_=filter_, page_size=page_size, page=page,
                                           attrlist=attr_list)
    result_list_count = 0
    if page == 1:
        result_list_count_tmp = generate_report_dataset_all(ldap_conn, basedn, filter_=filter_, page_size=page_size,
                                                            attrlist=attr_list)
        result_list_count = len(result_list_count_tmp)
    result_list = parse_results(result_list_, attr_list)

    return render_json({'result': True, 'message': result_list, 'report_fields': report_fields_,
                        'result_list_count': result_list_count})


def generate_report_dataset(ldap_conn=None, basedn=None, filter_="", page_size=100, page=1, attrlist=None, cookie=""):
    for i in range(1, page+1):
        res = ldap_conn.search(basedn, filter_, attributes=attrlist, paged_size=page_size, paged_cookie=cookie)
        cookie_ = ldap_conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        if res:
            if cookie_:
                cookie = cookie_
            if i == page:
                return [json.loads(entry.entry_to_json()) for entry in ldap_conn.entries]
    return []


def generate_report_dataset_all(ldap_conn=None, basedn=None, filter_="", page_size=5000, attrlist=None, cookie=""):
    res_data_all = []
    while True:
        res = ldap_conn.search(basedn, filter_, attributes=attrlist, paged_size=page_size, paged_cookie=cookie)
        cookie_ = ldap_conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        if res:
            res_data_all += [json.loads(entry.entry_to_json()) for entry in ldap_conn.entries]
            if cookie_:
                cookie = cookie_
            else:
                return res_data_all


def parse_results(result_list_, attr_list):
    result_list = []
    for item in result_list_:
        item_ = dict()
        for field in attr_list:
            try:
                if field == "memberOf":
                    item_[field] = ";".join(item['attributes'][field])
                else:
                    item_[field] = item['attributes'][field][0]
            except Exception as e:
                print(item, field, e)
        result_list.append(item_)

    return result_list


def parse_results_all(result_list_, attr_list):
    """转成list"""
    header_list = []
    for attr in attr_list:
        for item in report_fields:
            if attr == item['name']:
                header_list.append(item['value'])
                break

    result_list_all =[header_list]
    for item in result_list_:
        line_list = []
        for key in attr_list:
            try:
                if key == "memberOf":
                    line_list.append(";".join(item['attributes'][key]))
                else:
                    line_list.append(item['attributes'][key][0])
            except Exception as e:
                print(item['attributes'], e)
        result_list_all.append(line_list)

    return result_list_all


def generate_filter_string(report_type, start_, end_):
    start = end = 0
    if start_ and end_ and report_type and report_type[1] in ['recent_create_user', 'recent_update_user', 'login_time']:
        if report_type[0] == 'normal_reports':
            GMT_FORMAT2 = '%Y-%m-%dT%H:%M:%S.000Z'
            GMT_FORMAT = '%Y%m%d%H%M%S.0Z'
            start = str(datetime.strptime(start_, GMT_FORMAT2).strftime(GMT_FORMAT))
            end = str(datetime.strptime(end_, GMT_FORMAT2).strftime(GMT_FORMAT))
        elif report_type[1] == 'login_time':
            GMT_FORMAT = '%Y-%m-%dT%H:%M:%S.000Z'
            start = int(time.mktime(time.strptime(str(datetime.strptime(start_, GMT_FORMAT)), "%Y-%m-%d %H:%M:%S")))
            end = int(time.mktime(time.strptime(str(datetime.strptime(end_, GMT_FORMAT)), "%Y-%m-%d %H:%M:%S")))
            start += 11644473600
            end += 11644473600

    filter_string_map = {
        'normal_reports': {  # 常规报表
            'all_user': '(sAMAccountType=805306368)',  # 所有用户的接口
            'many_groups_user': '(&(objectCategory=person)(objectClass=user)(memberOf=(cn=*,cn=*,*)))',  # 同时在多个组的用户,，条件存在异常
            # 'recent_delete_user': '',  # 最近删除的用户
            'recent_create_user': '(&(objectCategory=person)(objectClass=user)(whenCreated>={0})(whenCreated<={1}))'.format(start, end),  # 最近创建的用户
            'recent_update_user': '(&(objectCategory=person)(objectClass=user)(whenChanged>={0})(whenChanged<={1}))'.format(start, end),  # 最近更改的用户
        },
        'account_reports': {  # 账户状态报表
            'forbidden_user': '(&(objectCategory=person)(objectClass=user)'
                              '(userAccountControl:1.2.840.113556.1.4.803:=2))',  # 被禁用的用户
            'lock_user': '(&(objectCategory=person)(objectClass=user)(lockouttime>=1))',  # 被锁定的用户
            'expire_user': '(&(objectCategory=person)(objectClass=user)(accountExpires>=1))'
                           # '(accountExpires<=9223372036854775806))',  # 账户过期的用户
        },
        'login_reports': {  # 登录报表
            'sleep_user': '(&(objectCategory=person)(objectClass=user)'
                          '(userAccountControl:1.2.840.113556.1.4.803:=2))',  # 非活动/休眠用户
            # 'actual_login': '(&(objectCategory=person)(objectClass=user))',  # 实际最后登录
            # 'recent_login': '(&(objectCategory=person)(objectClass=user))',  # 最近登录的用户
            'login_time': '(&(objectCategory=person)(objectClass=user)'
                            '(lastLogonTimestamp>={0}0000000)(lastLogonTimestamp<={1}0000000))'.format(start, end),  # 基于登录时间的报表
            'start_user': '(&(objectCategory=person)(objectClass=user)'
                          '(!(userAccountControl:1.2.840.113556.1.4.803:=2)))',  # 已启用的用户
        },
    }
    return filter_string_map.get(report_type[0], None).get(report_type[1], None)


def get_ldap_connection(domain):
    domain_map = {
        "corp.gwm.cn": '10.255.18.4',
        "tech.gwm.cn": '10.255.18.101',
        "global.gwm.cn": '10.255.18.70',
    }
    server = Server(domain_map.get(domain, '10.255.18.4'), use_ssl=True, get_info=ALL)
    ldap_conn = Connection(server, 'GW00180422@corp.gwm.com', 'Purple123', auto_bind=True)

    return ldap_conn


def search_metric_value(domain, ldap_conn=None, metic=None):
    dc = domain.split('.')[0]
    basedn = "ou=sites,dc={0},dc=gwm,dc=com".format(dc)
    if metic == 7:
        basedn = "ou=Domain Controllers,dc={0},dc=gwm,dc=com".format(dc)
    filter_ = metric_map.get(metic, 0)
    page_size = 5000
    count = 0
    cookie = None
    while True:
        res = ldap_conn.search(basedn, filter_, attributes=['name', 'mail'], paged_size=page_size, paged_cookie=cookie)
        cookie_ = ldap_conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
        if res:
            if cookie_:
                count += page_size
                cookie = cookie_
            else:
                count += len(ldap_conn.entries)
                break
    return count


def search_fields(request):
    """查询不同报表对应字段"""
    print(settings.SITE_URL)
    report_type = json.loads(request.body)['report_type']
    is_show = False
    if report_type and report_type[1] in ['recent_create_user', 'recent_update_user', 'login_time']:
        is_show = True
    field_list = [item['value'] for item in report_fields]

    return render_json({'result': True, 'message': field_list, 'is_show': is_show, 'report_fields': report_fields})


def download_excel(request):
    condition = json.loads(request.body)['condition']
    domain = condition.get('domain', 'corp.gwm.cn')
    report_type = condition.get('report_type', ['account_reports', 'forbidden_user'])
    checked_attrs = condition.get('checkedAttrs', None)
    attr_list = []
    report_fields_ = []
    if checked_attrs is None:
        attr_list = condition.get('attr_list', ['displayName', 'name', 'mail', 'department', 'company', 'whenCreated'])
    else:
        for checkedAttr in checked_attrs:
            for item in report_fields:
                if checkedAttr == item['value']:
                    attr_list += [item['name']]
                    report_fields_.append(item)
    page_size = condition.get('page_size', 5000)
    ldap_conn = get_ldap_connection(domain)
    dc = domain.split('.')[0]
    basedn = "ou=sites,dc={0},dc=gwm,dc=com".format(dc)
    start_end_date = condition.get('start_end_date', None)
    if start_end_date:
        filter_ = generate_filter_string(report_type, start_end_date[0], start_end_date[1])
    else:
        filter_ = generate_filter_string(report_type, None, None)
    print(filter_)
    result_list_ = generate_report_dataset_all(ldap_conn, basedn, filter_=filter_, page_size=page_size, attrlist=attr_list)
    result_list_all = parse_results_all(result_list_, attr_list)
    sheet_name = report_name_map.get(report_type[0], '-') + '-' + report_name_map.get(report_type[1], '-')
    file_name = 'filename'
    book = Workbook()
    sheet = book.create_sheet(title=sheet_name, index=0)
    for data in result_list_all:
        sheet.append(data)

    response = HttpResponse(content=save_virtual_workbook(book), content_type='application/msexcel')
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename={}.xlsx'.format(file_name)

    return response


metric_map = {
    0: "(sAMAccountType=805306368)",  # 用户总数
    1: "(&(objectCategory=person)(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))",  # 被禁用的用户数
    2: "(&(objectCategory=person)(objectClass=user)(lockouttime>=1))",  # 被锁定的用户数
    3: "(&(objectCategory=person)(objectClass=user)(pwdlastset=0))",  # 密码已过期的用户数
    4: "(objectCategory=computer)",  # 计算机总数
    5: "(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=4098))",  # 被禁用的计算机数量
    6: "(&(objectCategory=computer)(operatingSystem=*server*))",  # 服务器的数量
    7: "(primaryGroupID=516)",  # 域控制器数量,这个的查询需要相关baseDN的OU：'Domain Controllers'
    8: "(&(objectCategory=person)(objectClass=user)(|(lastlogon=0)(!(lastlogon=*))))",  # 从未登录过的用户数
    9: "(&(objectCategory=person)(objectClass=user)(lastLogonTimestamp>={0}0000000))".format(int(time.time() - 30 * 24 * 60 * 60 + 11644473600)),  # 最近在30天内登录的用户
    10: "(&(objectCategory=person)(objectClass=user)(pwdLastSet>={0}0000000))".format(int(time.time() - 15 * 24 * 60 * 60 + 11644473600)),  # 30天内密码即将过期的用户
    11: "(objectCategory=group)",  # 组数量
    12: "(groupType:1.2.840.113556.1.4.803:=2147483648)",  # 安全组数量
    13: "(objectCategory=contact)",  # 通讯组的数量
    14: "(&(objectCategory=group)(!(member=*)))",  # 没有成员的组的数量
    15: "(objectCategory=organizationalUnit)",  # 组织单位的数量
}


report_fields = [
    {'name': 'cn', 'value': '公共名称'},
    {'name': 'sn', 'value': '姓'},
    {'name': 'title', 'value': '职务'},
    {'name': 'description', 'value': '描述'},
    {'name': 'physicalDeliveryOfficeName', 'value': '办公室'},
    {'name': 'givenName', 'value': '名'},
    {'name': 'whenCreated', 'value': '创建时间'},
    {'name': 'whenChanged', 'value': '修改时间'},
    {'name': 'displayName', 'value': '显示名称'},
    {'name': 'memberOf', 'value': '隶属于'},
    {'name': 'department', 'value': '部门'},
    {'name': 'company', 'value': '公司'},
    {'name': 'userAccountControl', 'value': '帐户行为控制标志'},
    {'name': 'countryCode', 'value': '国家/地区'},
    {'name': 'primaryGroupID', 'value': '所属组的ID'},
    {'name': 'accountExpires', 'value': '帐户到期日期'},
    {'name': 'sAMAccountName', 'value': '用户登录名1'},
    {'name': 'userPrincipalName', 'value': '用户登录名2'},
    {'name': 'mail', 'value': '电子邮件'}
]

report_name_map = {
    'normal_reports': '常规报表',
    'account_reports': '账户状态报表',
    'login_reports': '登录报表',
    'all_user': '所有用户',
    'many_groups_user': '同时在多个组的用户',
    'recent_create_user': '最近创建的用户',
    'recent_update_user': '最近更改的用户',
    'forbidden_user': '被禁用的用户',
    'lock_user': '被锁定的用户',
    'expire_user': '账户过期的用户',
    'sleep_user': '非活动-休眠用户',
    'login_time': '基于登录时间的报表',
    'start_user': '已启动的用户',
}