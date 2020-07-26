#!/usr/bin/python3

# Usage: python3 bras.py username

import datetime
import ipaddress
import sys
import time
import getpass
import requests
import argparse
import json
from collections import OrderedDict


def get_password(d, no_keyring=False, non_interactive=False):
    if not d:
        return
    save_password = True if d['password'] else False
    if not d['username'] and not non_interactive:
        d['username'] = input('Username: ')
    if not d['password'] and not no_keyring:
        d['password'] = keyring.get_password('nju_bras', d['username'])
    if not d['password'] and not non_interactive:
        d['password'] = getpass.getpass('Password: ')
        save_password = True
    if save_password and not no_keyring:
        keyring.set_password('nju_bras', d['username'], d['password'])


def del_password(d):
    if d:
        del_password(keyring.delete_password('nju_bras', d['username']))


def my_print(*args, **kwargs):
    global log_file
    if log_file is None:
        print(*args, **kwargs)
    else:
        print(*args, **kwargs, file=log_file)
        log_file.flush()


def print_response(r):
    if 'request_time' in r:
        r['request_time'] = str(datetime.datetime.fromtimestamp(r['request_time']))
    if 'userinfo' in r:
        r['userinfo']['acctstarttime'] = str(datetime.datetime.fromtimestamp(r['userinfo']['acctstarttime']))
        r['userinfo']['balance'] = r['userinfo']['balance'] / 100
        r['userinfo']['portal_server_ip'] = str(ipaddress.IPv4Address(r['userinfo']['portal_server_ip']))
        r['userinfo']['useripv4'] = str(ipaddress.IPv4Address(r['userinfo']['useripv4']))
    my_print(json.dumps(r, ensure_ascii=False))


def bras(d=None):
    try:
        my_print('[{}]'.format(datetime.datetime.now()), end=' ')
        if d:  # 登录
            url = 'http://p.nju.edu.cn/portal_io/login'
            response = requests.post(url=url, data={'username': '123', 'password': 'abc'}, timeout=10)
            if response.json()['reply_code'] != 6:  # 6: 已登录
                response = requests.post(url=url, data=d, timeout=10)
        else:  # 退出
            response = requests.post(url='http://p.nju.edu.cn/portal_io/logout', data=d, timeout=10)
        r = response.json(object_pairs_hook=OrderedDict)
    except ValueError:
        my_print(response.status_code, response.reason)
        return -1
    except requests.exceptions.ConnectTimeout:
        my_print({'reply_code': -1, 'reply_msg': '连接超时'})
        return -1
    except requests.exceptions.ConnectionError:
        my_print({'reply_code': -1, 'reply_msg': '网络错误'})
        return -1
    else:
        print_response(r)
        return r['reply_code']


if __name__ == '__main__':
    data = {'username': '', 'password': ''}
    log_file = None

    parser = argparse.ArgumentParser(description='自动登录南大校园网')
    parser.add_argument(dest='username', metavar='username', nargs='?', help='用户名称')
    parser.add_argument('-o', '--out', dest='logout', action='store_true', help='退出登录')
    parser.add_argument('-k', '--keep-alive', dest='keep', action='store_true', help='保持登录(5分钟登录一次)')
    parser.add_argument('-p', '--period', dest='period', metavar='seconds', default=0, type=int,
                        help='保持登录并设置间隔时间')
    parser.add_argument('-l', '--log', dest='log', metavar='filename', help='输出记录到文件')
    parser.add_argument('-n', '--non-interactive', dest='non_interactive', action='store_true', help='不询问用户名密码')
    parser.add_argument('--no-keyring', dest='no_keyring', action='store_true', help='不使用keyring')
    parser.add_argument('--password', dest='password', metavar='password', help='用户密码')
    arg = parser.parse_args()

    if not arg.no_keyring and not arg.logout:
        import keyring
    if arg.log:
        log_file = open(arg.log, 'a', encoding='utf-8')
    if arg.logout:
        data = None
    elif arg.username:
        data['username'] = arg.username
        if arg.password:
            data['password'] = arg.password

    get_password(data, no_keyring=arg.no_keyring, non_interactive=arg.non_interactive)

    if (arg.keep or arg.period) and not arg.logout:
        if arg.period <= 0:
            arg.period = 300
        while True:
            bras(data)
            time.sleep(arg.period)
    else:
        status = bras(data)
        if status == 3 and not arg.no_keyring:  # 3: 认证失败
            del_password(data)
        sys.exit(0 if status in [1, 6, 101] else 1)  # 1: 登录成功, 6: 已登录, 101: 下线成功
