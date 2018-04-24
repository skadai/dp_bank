# coding: utf-8
## python2.7环境
import os
import json
import sys

from utils import log


reload(sys)
sys.setdefaultencoding('utf8')


def save(data, path):
    """
    本函数把一个 dict 或者 list 写入文件
    data 是 dict 或者 list
    path 是保存文件的路径
    """
    # json 是一个序列化/反序列化(上课会讲这两个名词) list/dict 的库
    # indent 是缩进
    # ensure_ascii=False 用于保存中文
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open('wechat/'+path, 'w+',) as f:
        # log('save', path, s, data)
        f.write(s)


def load(path):
    """
    本函数从一个文件中载入数据并转化为 dict 或者 list
    path 是保存文件的路径
    """
    with open('wechat/'+path, 'r', ) as f:
        s = f.read()
        # log('load', s)
        if len(s) > 0:
            return json.loads(s)
        else:
            return []


class Model(object):
    # Model 是用于存储数据的基类
    # @classmethod 说明这是一个 类方法
    # 类方法的调用方式是  类名.类方法()
    id = None

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
    def new(cls, form):
        # cls(form) 相当于 User(form)
        m = cls(form)
        m.id = form.get('id', None)
        return m

    @classmethod
    def all(cls):
        """
        all 方法(类里面的函数叫方法)使用 load 函数得到所有的 models
        """
        path = cls.db_path()
        models = load(path)
        ms = [cls.new(m) for m in models]
        return ms

    @classmethod
    def find_by(cls, **kwargs):
        ms = cls.all()
        for m in ms:
            for key in kwargs.keys():
                if getattr(m, key, None) != kwargs[key]:
                        break
                else:
                    pass
            else:
                return m
        return None

    @classmethod
    def find_all(cls, **kwargs):
        ms = cls.all()
        result = []
        for m in ms:
            for key in kwargs.keys():
                if getattr(m, key, None) != kwargs[key]:
                        break
                else:
                    pass
            else:
                result.append(m)
        return result

    def save(self):
        """
        用 all 方法读取文件中的所有 model 并生成一个 list
        把 self 添加进去并且保存进文件
        """
        # self.__class__.all()
        models = self.all()
        # log('models', models)
        # __dict__ 是包含了对象所有属性和值的字典
        l = [m.__dict__ for m in models]
        if self.id is None:
            print('这个USER的ID是空的')
            if l:
                self.id = l[-1]["id"] + 1
            else:
                self.id = 1
            models.append(self)
        else:
            m = self.find_by(id=self.id)
            print('发现了你的ID')
            if m:
                # models[m.id-1].__dict__.update(self.__dict__)
                models[m.id-1].__dict__.update(self.__dict__)
                print self.__dict__
            else:
                log('你的id非法')
                self.id = None
                self.save()
                return
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    def __repr__(self):
        """
        __repr__ 是一个魔法方法
        简单来说, 它的作用是得到类的 字符串表达 形式
        比如 print(u) 实际上是 print(u.__repr__())
        不明白就看书或者 搜
        """
        classname = self.__class__.__name__
        properties = ['{}: ({})'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)


class User(Model):
    def __init__(self, form):
        self.username = form.get('username', '')
        self.openid = form.get('openid', '')
        self.share = form.get('share',0)
        self.lastshare = form.get('lastshare',0)
        self.bonus = form.get('bonus',0)
        self.block = form.get('block',0)

    def add_share(self,share):
        self.lastshare = self.share
        self.share = round(self.share + share,2)
        self.save()

    def operate_share(self, share):
        self.lastshare = self.share
        self.share = round(share + self.share,2)

    def operate_bonus(self, bonus):
        # 限制bonus只能为正，这样余额只能减少不能增加
        self.bonus -= round(abs(bonus),2)
        self.save()

    @classmethod
    def current_bill(cls):
        users = cls.all()
        result=[]
        for u in users:
            message = dict()
            message.update(u.__dict__)
            message.pop('id')
            message.pop('openid')
            # if u.username != self.username:
            #     message.pop('lastshare')
            result.append(message)
        return result

    @classmethod
    def sum_bill(cls):
        users = cls.all()
        total = 0
        for u in users:
            total += u.share
        return dict(total = total, best_share = cls.best_share().username)

    @classmethod
    def best_share(cls):
        share_list = [u.share for u in cls.all()]
        return cls.find_by(share=max(share_list))

    def add_bonus(self, count):
        # if self.username == 'csk':
        for u in self.all():
            if u.block == 0:
                u.bonus += (round(float(count)/(self.active_number()),2))
                # log('spend_bill',u)
                u.save()

    @classmethod
    def active_number(cls):
        number = 0
        for u in cls.all():
            if u.block == 0:
                number += 1
        return number

    def quit(self):
        self.block = 1
        self.save()
        return '{}暂时退出'.format(self.username)

    def restart(self):
        self.block = 0
        self.save()
        return '{}又回来了'.format(self.username)

def test_func():
    with open(User.db_path(), 'w') as f:
        f.write('[]')
    csk = User(dict(username='csk'))
    csk.save()
    xiao = User(dict(username='xiao'))
    xiao.save()
    jing = User(dict(username='jing'))
    jing.save()
    csk.add_share(100)
    log('current_bill:{}\n'.format(User.current_bill()))
    # csk.spend_share(200)
    # log('current_bill:{}\n'.format(User.current_bill()))
    xiao.add_share(1000)
    log('current_bill:{}\n'.format(User.current_bill()))
    # xiao.add_share(20)
    csk.spend_share(2000)
    log('current_bill:{}\n'.format(User.current_bill()))
    csk.add_share(1000)

if __name__ == '__main__':
    test_func()

