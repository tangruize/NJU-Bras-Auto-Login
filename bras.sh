#!/bin/sh

USERNAME="$1"
PASSWORD="$2"

if test "$1" = "out" -o "$1" = "-o" -o "$1" = "--out"; then
    curl -m 5 -sS http://p.nju.edu.cn/portal_io/logout
    exit
fi

set -e

INFO=$(curl -m 5 -sS http://p.nju.edu.cn/portal_io/getinfo)
if echo "$INFO" | grep -q '"reply_code":0'; then
    echo "$INFO"
    exit
fi

if test -z "$USERNAME"; then
    read -p 'USERNAME: ' USERNAME
fi

if test -z "$PASSWORD"; then
    read -s -p 'PASSWORD: ' PASSWORD
    echo
fi

#CHALLENGE=$(curl -m 5 -sS http://p.nju.edu.cn/portal_io/getchallenge | cut -d'"' -f10)
#ID=$(dd if=/dev/urandom count=1 ibs=1 2>/dev/null | xxd -ps)
#PASSWORD=${ID}$(echo -n "$PASSWORD" | xxd -ps)${CHALLENGE}
#PASSWORD=${ID}$(echo -n "$PASSWORD" | xxd -ps -r | md5sum | cut -d' ' -f1)

INFO=$(curl -m 5 -sS http://p.nju.edu.cn/portal_io/login -d username="$USERNAME" -d password="$PASSWORD" #-d challenge="$CHALLENGE"
      )
echo "$INFO"
if ! echo "$INFO" | grep -q '"reply_code":1'; then
    exit 1
fi
