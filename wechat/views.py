# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime 
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding('utf-8') 
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from wechat_sdk.messages import TextMessage, VoiceMessage, ImageMessage, VideoMessage, LinkMessage, LocationMessage, \
    EventMessage


wechat_instance = WechatBasic(
    token='hahaha',
    appid='wx776dcc9b30d2def9  ',
    appsecret='992ce245e92def32471427cb65c54d3d'
)

support_product_list =['m5','C5400','C3150','C9','C2300','2300','5400','3150','c9']
file_full_path = '/home/ubuntu/'


pattern_list = []

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
        # 当前会话内容
        content = message.content.strip(' ')  
        try:    
            product_name,day  = content.split(',') 
            
        except:
            product_name = content
            day = 30
        if product_name not in support_product_list:
            reply_text = (
                '该型号产品不支持!!使用说明：输入：产品,期限(如m5,19)  返回给定期限(默认30天)内的亚马逊所有差评(评分<=3)情况;\n\
                 当前支持的产品是C9,C2300,C3150,C5400,m5..... '
            )
        elif  int(day) < 0 :
            reply_text = (
                '请输入合理的期限(0-100)!!使用说明：输入：产品,期限(如m5,19)   返回给定期限(默认30天)内的亚马逊所有差评(评分<=3)情况;\n\
                 当前支持的产品是C9,C2300,C3150,C5400,m5.....'
            )
        else: 
            
            generate_report(product_name,int(day))
            reply_text = get_bad_reviews(file_full_path+'bad_news_%s'%product_name)
    elif isinstance(message, VoiceMessage):
        reply_text = '语音信息我听不懂/:P-(/:P-(/:P-('
    elif isinstance(message, ImageMessage):
        reply_text = '图片信息我也看不懂/:P-(/:P-(/:P-('
    elif isinstance(message, VideoMessage):
        reply_text = '视频我不会看/:P-('
    elif isinstance(message, LinkMessage):
        reply_text = '链接信息'
    elif isinstance(message, LocationMessage):
        reply_text = '地理位置信息'
    else:
        reply_text = '功能还没有实现'

    response = wechat_instance.response_text(content=reply_text)
    return HttpResponse(response, content_type="application/xml")
    
    
def generate_report(product_name='m5',day=30):
    
    target_day = datetime.datetime.now()-datetime.timedelta(day) 
    dt= pd.read_excel(file_full_path+'%s.xls'%product_name)
    max_char = 1800
    cur_review =dt.loc[:,['star','content','title','date']]
    cur_review = cur_review.loc[cur_review['date']>=target_day.strftime('%Y-%m-%d')]
    total_reviews = cur_review['star'].count()
    bad_reviews = cur_review[cur_review.star<4]['star'].count()
    
    file_length=0
    with open(file_full_path+'bad_news_%s'%product_name,'w') as cc:
        cc.write('there are %s bad of %s total news about %s during the last %s day(s) ...\n'%(bad_reviews,total_reviews,product_name,day))
        
        for index,item in enumerate(cur_review[cur_review.star<4]['content']):
            try:
                file_length+=len(item)
                if file_length>max_char:
                    cc.write('[%s]:%s \n' %(index,item[:(max_char-file_length)]))
                    cc.write('msg is too loooooooong,')
                    break
                else:
                    cc.write('[%s]:%s \n' %(index,item))
            except Exception,e:
                print e
                cc.write('sth wrong of this line:%s,skip...\n'%e)
        cc.write('更多信息请邮件给 skchang1587@gmail.com获取\n\n')
    cc.close() 
    
    
def get_bad_reviews(file_name):
    with open(file_name) as cc:
        data = cc.read()
    cc.close()
    return data
