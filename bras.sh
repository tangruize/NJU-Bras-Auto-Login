#!/bin/bash

USERNAME="$1"
PASSWORD="$2"

if test "$1" = "out" -o "$1" = "-o"; then
    curl -m 5 -s http://p.nju.edu.cn/portal_io/logout
    exit
fi

set -euo pipefail

INFO=$(curl -m 5 -s http://p.nju.edu.cn/portal_io/getinfo)
if grep -q '"reply_code":0' <<< "$INFO"; then
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


CHALLENGE=$(curl -m 5 -s http://p.nju.edu.cn/portal_io/getchallenge | cut -d'"' -f10)
ID=$(printf '%02x' $((RANDOM%256)))
PASSWORD="$(xxd -ps -r <<< $ID)${PASSWORD}$(xxd -ps -r <<< $CHALLENGE)"
PASSWORD=${ID}$(echo -n "$PASSWORD" | md5sum | cut -d' ' -f1)

curl -m 5 -s http://p.nju.edu.cn/portal_io/login -d username="$USERNAME" -d password="$PASSWORD" -d challenge="$CHALLENGE"
