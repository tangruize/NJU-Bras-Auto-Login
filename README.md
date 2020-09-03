# 自动登录校园网脚本

这个脚本可以自动登录南京大学校园网, 使用了系统的用户凭据存储服务, 发送哈希后的密码, 可以设定保活选项, 安全便捷.

尽管校园网推出了["无感知认证"](https://itsc.nju.edu.cn/21611/listm.htm)服务, 但该服务只能在设备连入校园网时登录一次, 有掉线的可能, 在一些场景下不可靠, 如使用反向SSH隧道与一台公网服务器保持连接.

登录和登出简单的curl命令 (不推荐):

```bash
curl http://p.nju.edu.cn/portal_io/login -d username=USERNAME -d password=PASSWORD  # 登录, 直接发送明文密码, 不安全
curl http://p.nju.edu.cn/portal_io/logout  # 登出
```

## 如何使用

python脚本需要 [python3](https://www.python.org/downloads/) 运行环境. 使用了 [Python keyring library](https://pypi.org/project/keyring/), 它可以跨平台地获取系统的凭据存储服务. 安装依赖:

```bash
pip install requests keyring
```

运行python脚本:

```bash
python bras.py  # 会提示输入用户名和密码 (如果keyring中没有密码)
python bras.py USERNAME  # 不会提示输入用户名
python bras.py USERNAME -k  # 保持连接, 5分钟登录一次
python bras.py -o  # 退出登录
```

脚本从 keyring 获取密码, 只需要输入一次, 密码就会记住. keyring 在电脑用户登录时自动解锁.

脚本登录时不会直接 post 用户名密码, 而是先判断是否已经登录, 如果已经登录, 则不再登录. 否则使用询问握手认证协议 (Challenge-Handshake Authentication Protocol，CHAP) 发送哈希后的密码.

运行shell脚本:

```bash
./bras.sh  # 会提示输入用户名和密码
./bras.sh USERNAME PASSWORD  # 登录
./bras.sh -o  # 退出登录
```

shell脚本不使用keyring获取密码, 可以手动在脚本3,4行写入用户名密码 (或者获取密码的命令), 如:

```bash
USERNAME="dz1234567"
PASSWORD="$(echo ZHoxMjM0NTY3Cg== | base64 -d)"  # 用base64编码
PASSWORD="$(keyring get nju_bras dz1234567)"  # 从keyring获取
```

### 命令行选项 (python脚本)

```txt
usage: bras.py [-h] [-o] [-k] [-p seconds] [-l filename] [-n] [--no-keyring] [--password password] [username]

自动登录南大校园网

positional arguments:
  username              用户名称

optional arguments:
  -h, --help            show this help message and exit
  -o, --out             退出登录
  -k, --keep-alive      保持登录(5分钟登录一次)
  -p seconds, --period seconds
                        保持登录并设置间隔时间
  -l filename, --log filename
                        输出记录到文件
  -n, --non-interactive
                        不询问用户名密码
  --no-keyring          不使用keyring
  --password password   用户密码
```
