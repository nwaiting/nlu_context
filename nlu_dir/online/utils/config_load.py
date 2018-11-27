#!/usr/bin/env python3
# -*- coding:utf8 -*-


"""
从配置文件读取参数
"""

import configparser
import os
import platform
from os.path import dirname

import redis


def get_config(mode, section, config_key):
    dir_name = dirname(dirname(dirname(os.path.realpath(__file__))))
    if mode == "local":
        file_path = dir_name + os.sep + "config/local-config.conf"
    elif mode == "test":
        file_path = dir_name + os.sep + "config/test-config.conf"
    elif mode == "online":
        file_path = dir_name + os.sep + "config/config.conf"
    else:
        return
    # print(file_path)
    conf = configparser.ConfigParser()
    conf.read(file_path)
    config_value = conf.get(section, config_key)
    return config_value


def get_log_path(mode):
    return get_config(mode, "path", "log_path")


def get_redis_pool():
    if platform.node() == 'JRA1PF18UCM8':
        pool = redis.ConnectionPool(host='localhost', port=6379, password='123456')
        # rds = redis.Redis(connection_pool=pool)
    else:
        pool = redis.ConnectionPool(host='xxx', port=6379,
                                    password='xxx')

    return pool


# logging_configged=logging.config.fileConfig(open(PathUtil().get_logging_config, encoding='utf-8'))


if __name__ == '__main__':
    print(get_config("local", "path", "log_path"))
    print(get_log_path("local"))
