#!/usr/bin/python3

# Usage: python3 bras.py username

import datetime
import hashlib
import ipaddress
import random
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
        try:
            d['password'] = keyring.get_password('nju_bras', d['username'])
        except RuntimeError:
            print('Warning: failed to get password from keyring.', file=sys.stderr, flush=True)
            no_keyring = True
    if not d['password'] and not non_interactive:
        d['password'] = getpass.getpass('Password: ')
        save_password = True
    if save_password and not no_keyring:
        try:
            keyring.set_password('nju_bras', d['username'], d['password'])
        except RuntimeError:
            print('Warning: failed to save password to keyring.', file=sys.stderr, flush=True)


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


def try_post(url, d):
    try:
        response = requests.post(url=url, data=d, timeout=10)
    except requests.exceptions.RequestException as e:
        my_print({'reply_code': -1, 'reply_msg': str(e)})
        return None
    return response


def create_chap_password(url, d):
    """http://p.nju.edu.cn/portal/js/portal.js"""
    response = try_post(url, None)
    if response and response.json()['reply_code'] == 0:
        challenge = response.json()['challenge']
    else:
        return None
    rid = random.randint(0, 255)
    password = chr(rid) + d['password'] + ''.join([chr(int(challenge[i:i+2], 16)) for i in range(0, len(challenge), 2)])
    password = '{:02x}'.format(rid) + hashlib.md5(password.encode('latin-1')).hexdigest()
    chap_data = {'username': d['username'], 'password': password, 'challenge': challenge}
    return chap_data


def bras(d=None, hash=False):
    url_prefix = 'http://p.nju.edu.cn/portal_io/'
    my_print('[{}]'.format(datetime.datetime.now()), end=' ')
    if d:  # 登录
        response = try_post(url_prefix + 'getinfo', None)
        if response and response.json()['reply_code'] != 0:  # 0: 已登录
            if hash:
                chap_data = create_chap_password(url_prefix + 'getchallenge', d)
                response = try_post(url_prefix + 'login', chap_data)
            else:
                response = try_post(url_prefix + 'login', d)
    else:  # 退出
        response = try_post(url_prefix + 'logout', None)
    if response:
        r = response.json(object_pairs_hook=OrderedDict)
        print_response(r)
        return r['reply_code']
    else:
        return -1


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
    parser.add_argument('--hash-password', dest='hash_password', action='store_true', help='使用hash密码')
    parser.add_argument('--no-keyring', dest='no_keyring', action='store_true', help='不使用keyring')
    parser.add_argument('--password', dest='password', metavar='password', help='用户密码')
    arg = parser.parse_args()

    if not arg.no_keyring and not arg.logout:
        try:
            import keyring
        except ImportError:
            print('Warning: package "keyring" is not installed.', file=sys.stderr, flush=True)
            arg.no_keyring = True
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
            bras(data, hash=arg.hash_password)
            time.sleep(arg.period)
    else:
        status = bras(data, hash=arg.hash_password)
        if status == 3 and not arg.no_keyring:  # 3: 认证失败
            del_password(data)
        sys.exit(0 if status in [0, 1, 6, 101] else 1)  # 0: 操作成功, 1: 登录成功, 6: 已登录, 101: 下线成功
