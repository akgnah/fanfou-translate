# fanfou-translate

![logo](https://setq.me/static/img/fanyi/title.png)

这里是饭否划词翻译（简称饭译）的源码，[饭译](<https://chrome.google.com/webstore/detail/%E9%A5%AD%E5%90%A6%E5%88%92%E8%AF%8D%E7%BF%BB%E8%AF%91/ncjehkbfoionmagghdkkphaimpdijjje>) 可在 Chrome 应用商店安装，详细说明见 <https://setq.me/fanyi> 。

其中 server 是服务端源码。在 Win10 上，Python2.7 和 3.7 测试通过，在 Ubuntu 18.04 上，Python3.6 测试通过。

``` shell
$ pip install -r server/requirements.txt  # 安装依赖
```

## 其他说明

[server/main.py](server/main.py) 提供 API 接口，[server/work.py](server/work.py) 推送词条，[server/account.py](server/account.py) 填写账号信息。

其中 [server/translate.py](server/translate.py) 使用了 <https://github.com/caspartse/python-translate> ，在此致谢。

感谢 Pornhub 提供 Logo 灵感，感谢 <https://logoly.pro> 提供 Logo 生成工具。