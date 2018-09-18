# -*- coding: utf8 -*-

import os
import platform
import socket


def get_host_ip():
    """
    优雅的获取本机IP地址
    :return: ip
    """
    ip = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        pass

    return ip

ip = get_host_ip()

# 本地环境配置
test_sign = os.path.exists('/data/app/idc/idc.ini')
ENVIRONMENT = ''

# 开发环境
if platform.system() == 'Darwin' or platform.system() == 'Windows':
    from FMBusinessApp.config.config_local import *
    ENVIRONMENT = 'DEV'

# Docker测试环境配置
elif test_sign:
    from FMBusinessApp.config.config_test import *
    ENVIRONMENT = 'TEST_DOCKER'

# 测试环境
elif ip in ('10.74.100.16', ):
    from FMBusinessApp.config.config_test import *
    ENVIRONMENT = 'TEST'

# 生产环境
elif ip in ('10.74.105.9', '10.74.105.14'):
    from FMBusinessApp.config.config import *
    ENVIRONMENT = 'PRODUCT'

else:
    from FMBusinessApp.config.config_local import *
    ENVIRONMENT = 'DEV'

