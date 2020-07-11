# 自动登录校园网脚本

这个脚本可以自动登录南京大学校园网, 使用了系统的用户凭据存储服务, 可以设定保活选项, 安全便捷.

尽管校园网推出了["无感知认证"](https://itsc.nju.edu.cn/21611/listm.htm)服务, 但该服务只能在设备连入校园网时登录一次, 有掉线的可能, 在一些场景下不可靠, 如使用反向SSH隧道与一台公网服务器保持连接.

登录和登出原理:

```bash
curl http://p.nju.edu.cn/portal_io/login -d username=USERNAME -d password=PASSWORD  # 登录
curl http://p.nju.edu.cn/portal_io/logout  # 登出
```

## 如何使用

脚本需要 [python3](https://www.python.org/downloads/) 运行环境. 使用了 [Python keyring library](https://pypi.org/project/keyring/), 它可以跨平台地获取系统的凭据存储服务. 安装依赖:

```bash
pip install requests keyring
```

运行:

```bash
python bras.py  # 会提示输入用户名和密码(如果keyring中没有密码)
python bras.py USERNAME  # 不会提示输入用户名
python bras.py USERNAME -k  # 保持连接, 5分钟登录一次
```

脚本从 keyring 获取密码, 只需要输入一次, 密码就会记住. keyring 在电脑用户登录时自动解锁.

脚本登录时不会直接 post 用户名密码, 而是随便发点数据判断是否已经登录, 如果已经登录, 则不再登录. 因为不停在网络中用明文发送密码会增加被盗取的可能性.

### 命令行选项

```txt
usage: bras.py [-h] [-o] [-k] [-p seconds] [-n] [-l filename] [--no-keyring]
               [--password password]
               [username]

自动登录南大校园

positional arguments:
  username              用户名称

optional arguments:
  -h, --help            show this help message and exit
  -o, --out             退出登录
  -k, --keep-alive      保持登录(5分钟登录一次)
  -p seconds, --period seconds
                        保持登录并设置间隔时间
  -n, --non-interactive
                        不询问用户名密码
  -l filename, --log filename
                        输出记录到文件
  --no-keyring          不使用keyring
  --password password   用户密码
```
