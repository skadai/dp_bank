# -*- coding: utf-8 -*-
import sys
from Models import load,save

class Counter(object):
    user_list = []

    @classmethod
    def all(cls):
        """
        all 方法(类里面的函数叫方法)使用 load 函数得到所有的 models
        """
        path = cls.db_path()
        return load(path)

    @classmethod
    def db_path(cls):
        """
        cls 是类名, 谁调用的类名就是谁的
        classmethod 有一个参数是 class(这里我们用 cls 这个名字)
        所以我们可以得到 class 的名字
        """
        classname = cls.__name__
        path = '{}.txt'.format(classname)
        return path

    @classmethod
    def new(cls,u_list):
        cls.user_list = u_list
        path = cls.db_path()
        save(cls.user_list,path)

    @classmethod
    def pay(cls):
        d = dict()
        for u in cls.user_list:
            d[u['username']] = u['share']-u['lastshare']
        return d

    @classmethod
    def update(cls, new_list):
        models = cls.all()
        for index, u in enumerate(new_list):
            models[index]['lastshare'] = models[index]['share']
            models[index]['share'] = u.get('share')
        cls.user_list = models

