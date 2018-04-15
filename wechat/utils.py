# coding: utf-8
import time


def log(*args, **kwargs):
    # time.time() 返回 unix time
    # 如何把 unix time 转换为普通人类可以看懂的格式呢？
    time_format = '%Y/%m/%d %H:%M:%S'
    value = time.localtime(int(time.time()))
    dt = time.strftime(time_format, value)
    print(dt)
    for arg in args:
        print(arg)
    for key in kwargs.keys():
        print(key+': '+kwargs[key])