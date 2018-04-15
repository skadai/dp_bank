# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime 
import pandas as pd
import yaml as yy
from Counter import Counter
import sys

reload(sys)
sys.setdefaultencoding('utf-8') 
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, \
    EventMessage
from Models import *

wechat_instance = WechatBasic(
    token='hahaha',
    appid='wx776dcc9b30d2def9  ',
    appsecret='992ce245e92def32471427cb65c54d3d'
)

support_product_list =['m5','C5400','C3150','C9','C2300','C7']
file_full_path = '/home/ubuntu/'
user_dict=dict(a=['笑搜', 38.6, 1], b=['长官',2.2,2], c=['偶像',34.4,3],d=['小凯',0,4])
num_list = [str(x) for x in range(10)] + ['.' , '-']
cur = dict()

# help_text='输入:产品.期限(如m5.19)  \n返回:给定期限(默认30天)内的us.amazon所有评分<=3 review\n当前支持的产品包括\nC9\nC2300\nC3150\nC5400\nm5'
help_text = '输入000查看当前基金池\n' \
            '输入999查看可支配余额\n' \
            '输入数字进行配送\n'

name_text = '请输入字母确认你的昵称：\na: 笑搜\nb: 长官\nc: 偶像\nd：小凯'

@csrf_exempt
def wechat(request):
    if request.method == 'GET':
        # 检验合法性
        # 从 request 中提取基本信息 (signature, timestamp, nonce, xml)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')

        if not wechat_instance.check_signature(
                signature=signature, timestamp=timestamp, nonce=nonce):
            return HttpResponseBadRequest('Verify Failed')

        return HttpResponse(
            request.GET.get('echostr', ''), content_type="text/plain")

    # 解析本次请求的 XML 数据
    try:
        wechat_instance.parse_data(data=request.body)
    except ParseError:
        return HttpResponseBadRequest('Invalid XML Data')

    # 获取解析好的微信请求信息
    message = wechat_instance.get_message()

    if isinstance(message, TextMessage):
        openid = message.source
        content = message.content.strip(' ')
        user_tag = content.lower()
        if user_tag in user_dict and not User.find_by(id=user_dict[user_tag][-1]):
            username = user_dict[content.lower()][0]
            share = user_dict[content.lower()][1]
            u = User.new(dict(username=username, openid=openid, share=share))
            if not User.find_by(openid=openid):
                u.save()
                reply_text = '你好{}, 绑定成功了\n'.format(username) + help_text
            else:
                reply_text = '此人已经被绑定过了，重新输入字母:  '

        elif content == '开局':
            Counter.new(User.current_bill())
            reply_text = '**************'+content+'**************'

        elif content == '结账':
            print Counter.user_list
            Counter.update(User.current_bill())
            d = Counter.pay()
            reply_text = '**************'+content+'**************\n'
            for key in d.keys():
                reply_text += key +'支付 '+ str(d[key])+'元\n'

        elif content == '000':
            u = User.find_by(openid= openid)
            reply_text = current_report(u)
        elif content == '999':
            u = User.find_by(openid= openid)
            reply_text = current_bonus_report(u)
        # 消费接口
        elif content.startswith("大葫芦"):
            r = content.split(' ')
            count = float(r[-1])
            # 大葫芦 id value 表示定向操作
            if len(r) > 2:
                u = User.find_by(id=int(r[-2]))
            # 大葫芦 value 表示 自操作
            else:
                u = User.find_by(openid=openid)
            reply_text = bill_spend(u, count)

        # 配送接口
        elif False not in [x in num_list for x in content]:
            u = User.find_by(openid=openid)
            count = float(content)
            if abs(count) > 300:
                count = round(count/1000,2)
            reply_text = count_add(u, count)
        else:
            reply_text = help_text

        # # 当前会话内容
        # content = message.content.strip(' ')
        # try:
        #     product_name,day  = content.split('.')
        #
        # except:
        #     product_name = content
        #     day = 30
        # if product_name not in support_product_list and product_name.upper() not in support_product_list:
        #     reply_text = (
        #         '该型号产品不支持/:bye/:bye/:bye \n'+help_text
        #     )
        # elif  int(day) < 0 or int(day) >100:
        #     reply_text = (
        #         '请输入合理的期限(0-100)/:bye/:bye/:bye\n'+help_text
        #     )
        # elif product_name == 'm5':
        #     reply_text = generate_report(product_name,int(day))
        # else:
        #     reply_text = generate_report(product_name.upper(),int(day))
    elif isinstance(message, VoiceMessage):
        reply_text = '风太大听不见/:bye/:bye/:bye'
    elif isinstance(message, ImageMessage):
        reply_text = '发图都是辣鸡/:bye/:bye/:bye'
    elif isinstance(message, VideoMessage):
        reply_text = '发视频都是辣鸡/:bye/:bye/:bye'
    elif isinstance(message, LinkMessage):
        reply_text = '链接信息'
    elif isinstance(message, LocationMessage):
        reply_text = '地理位置信息'
    elif isinstance(message, EventMessage):
        if message.type == 'subscribe':
            response = wechat_instance.response_text(content='你可算来了/:eat\n' + name_text)
            return HttpResponse(response, content_type="application/xml")
        else: reply_text = '功能还没有实现'
    else:
        reply_text = '功能还没有实现'

    response = wechat_instance.response_text(content=reply_text)
    return HttpResponse(response, content_type="application/xml")


def count_add(u, count):
    u.add_share(count)
    u.add_bonus(count)
    reply_text = '{} 配送了 {}元\n'.format(u.username, count)
    reply_text += current_report(u) + current_bonus_report(u)
    return reply_text


def bill_spend(u, count):
    u.operate_bonus(count)
    return current_bonus_report(u)


def current_report(u):
    reply_text = '当前的基金：\n'
    reply_text += '/:eat/:eat/:eat/:eat/:eat/:eat\n'
    result = User.current_bill()
    for item in result:
        reply_text += '/:eat{}：'.format(item['username'])
        reply_text += str(item['share'])
        delta = item['share']-item['lastshare']
        if delta > 0:
            reply_text += '/::<{}\n'.format(delta)
        elif delta == 0:
            reply_text+='/::)\n'
        else:
            reply_text += '/:X-){}\n'.format(delta)

    reply_text += '/:eat/:eat/:eat/:eat/:eat/:eat\n'
    sum_info = u.sum_bill()
    reply_text += '/:eat {}\n'.format(sum_info['total'])
    reply_text += '/:heart理事长: {}/:heart\n'.format(sum_info['best_share'])
    return reply_text


def current_bonus_report(u):
    reply_text = '当前的余额：\n'
    reply_text += '/:eat/:eat/:eat/:eat/:eat/:eat\n'
    result = User.current_bill()
    for item in result:
        reply_text += '/:eat{}：'.format(item['username'])
        reply_text += str(item['bonus']) + '\n'
    reply_text += '/:eat/:eat/:eat/:eat/:eat/:eat\n'
    return reply_text

# for tp-link product only
def generate_report(product_name='m5',day=30):
    
    target_day = datetime.datetime.now()-datetime.timedelta(day) 
    dt= pd.read_excel(file_full_path+'%s.xls'%product_name)
    max_char = 1800
    cur_review =dt.loc[:,['star','content','title','date']]
    cur_review = cur_review.loc[cur_review['date']>=target_day.strftime('%Y-%m-%d')]
    total_reviews = cur_review['star'].count()
    bad_reviews = cur_review[cur_review.star<4]['star'].count()
  
    with open(file_full_path+'config.yml') as cc:
        data = yy.load(cc.read())
        star= data[product_name]['last_review']
    cc.close()
  
    file_length=0
    reply_text = ''

    reply_text += 'Current Star %s.\n There are %s bad of %s total news about %s during the last %s day(s) ...\n'%(star,bad_reviews,total_reviews,product_name,day)
    for index,item in enumerate(cur_review[cur_review.star<4]['content']):
        try:
            file_length+=len(item)
            if file_length>max_char:
                reply_text += '[%s]:%s \n' %(index,item[:(max_char-file_length)])
                reply_text += 'msg is too loooooooong,'
                break
            else:                    
                reply_text += '[%s]:%s \n' %(index,item)
        except Exception,e:
            print e
            reply_text+='sth wrong of this line:%s,skip...\n'               
    reply_text += 'pls mail to 919127001@qq.com for detailed information\n\n'
    return reply_text


# for tp-link product only
def get_bad_reviews(file_name):
    with open(file_name) as cc:
        data = cc.read()
    cc.close()
    return data

