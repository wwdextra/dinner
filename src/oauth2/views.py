#coding=utf-8
__author__ = 'laonan, http://laonan.net'

'''
调用weibo api例子, 将API的“/”变为“__”，并传入关键字参数，但不包括source和access_token参数：
client.get.statuses__user_timeline()

client.post.statuses__update(status=u'测试OAuth 2.0发微博')

f = open('/Users/Alan/Workspace/dongting/static/images/player_bg.png')
client.upload.statuses__upload(status=u'测试OAuth 2.0带图片发微博', pic=f)
f.close()
'''

import json

from django.core.urlresolvers import reverse

from django.contrib.auth import authenticate, login as auth_login

from sns_api.models import WeiboUser, QQUser
from django.contrib.auth.models import User,Group
from account.models import Company, UserProfile, GroupUserMenu, UserMenu, RegisterSurvey, MobileValidation, AuthTokenInfo
from credit.models import LevelRule
from credit.views import update_user_points
from utils.key_helper import gen_random, generate_key, format_baosteel_ip
from django.contrib.auth.views import login as auth_login_view
from django.contrib.sites.models import get_current_site
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from weibo import APIClient
from qq import OauthVars, OauthClient
from utils.apis import is_captcha_match


# production env config: baostar@sina.cn
#APP_KEY = '1064269280' # app key
#APP_SECRET = 'd8649d60c61ee42bd397537caad25343' # app secret

# test config:wyg5307@gmail.com
APP_KEY = '3727112766' # app key
APP_SECRET = 'cd1ce0ba3ce8c7e463019c976533af60' # app secret

def weibo_login(request):
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    url = client.get_authorize_url()
    return HttpResponseRedirect(url)

def weibo_auth(request):

    # 获取URL参数code:
    code = request.GET.get('code')

    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    token_obj = client.request_access_token(code)
    client.set_access_token(token_obj.access_token, token_obj.expires_in)

    if request.session.has_key('oauth_access_token'):
        del request.session['oauth_access_token']

    request.session['oauth_access_token'] = { 'uid' : token_obj.uid, 'access_token' : token_obj.access_token, 'expires_in' :  token_obj.expires_in}

    oauth_access_token = request.session.get('oauth_access_token', None)
    #跳转到首页
    back_to_url = reverse('home.views.index')

    if token_obj:
        try:
            w_user = WeiboUser.objects.get(weibo_user_id=oauth_access_token['uid'])
            user = authenticate(weibo_username=w_user.user.username)
            if user and user.is_active:
                auth_login(request,user)
        except WeiboUser.DoesNotExist:
            back_to_url = reverse('sns_api.views.bind_weibo_user')

    return HttpResponseRedirect(back_to_url)

def bind_weibo_user(request):

    oauth_access_token = request.session.get('oauth_access_token', None)
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])
    weibo_user = client.get.users__show(uid=oauth_access_token['uid'])
    weibo_username = weibo_user.screen_name

    template_var = dict()
    template_var['weibo_username'] = weibo_username

    def auth_user():
        #为其授权到登录状态
        w_user = WeiboUser.objects.get(weibo_user_id=oauth_access_token['uid'])
        user = authenticate(weibo_username=w_user.user.username)
        if user and user.is_active: auth_login(request,user)
        #发条微博====> ok
        if bao_msg: client.post.statuses__update(status=bao_msg[0:140])
        result['uname'] = weibo_username if weibo_username else None
        result['binded'] = 1

    if request.method == 'POST':
        result = dict()
        bao_id = request.POST.get('wbind_id', None) #宝时达用户名或注册邮箱
        bao_pwd = request.POST.get('wbind_pwd', None)
        bao_msg = request.POST.get('wbind_msg', None)
        if bao_id:
            try:
                w_user = WeiboUser.objects.get(weibo_username=weibo_username)
                if w_user and (w_user.user.username == bao_id or w_user.user.email == bao_id):
                    result['rebind'] = 1
                    #授权进入
                    w_user = WeiboUser.objects.get(weibo_user_id=oauth_access_token['uid'])
                    user = authenticate(weibo_username=w_user.user.username)
                    if user and user.is_active: auth_login(request,user)
            except WeiboUser.DoesNotExist:
                try:
                    user = User.objects.get(email=bao_id)
                    result['wbind_id'] = 1
                    result['wbind_pwd'] = (1 if authenticate(username=bao_id, password=bao_pwd) or authenticate(email=bao_id, password=bao_pwd) else 0)
                    #bind
                    if result['wbind_id'] and result['wbind_pwd']:
                        WeiboUser(
                            user = user,
                            weibo_user_id = oauth_access_token['uid'],
                            weibo_username = weibo_username,
                            oauth_access_token = oauth_access_token['access_token']
                        ).save()
                        auth_user() #授权登录
                except User.DoesNotExist:
                    user = User.objects.get(username=bao_id)
                    result['wbind_id'] = 1
                    result['wbind_pwd'] = (1 if authenticate(username=bao_id, password=bao_pwd) or authenticate(email=bao_id, password=bao_pwd) else 0)
                    #bind
                    if result['wbind_id'] and result['wbind_pwd']:
                        WeiboUser(
                            user = user,
                            weibo_user_id = oauth_access_token['uid'],
                            weibo_username = weibo_username,
                            oauth_access_token = oauth_access_token['access_token']
                        ).save()
                        auth_user() #为其授权登录
                except User.DoesNotExist:
                    result['wbind_id'] = 0 #id不存在
                    result['wbind_pwd'] = None #json解析为null值，不显示密码提示
        else:
            result['wbind_id'] = None

        if not bao_pwd:
            result['wbind_pwd'] = None
        result['wbind_msg'] = 1 if bao_msg else None

        return HttpResponse(json.dumps(result), 'application/json')
    else:
        return auth_login_view(request, template_name='sns/bind_weibo_user.html', extra_context=template_var)

def create_user_from_weibo(request, template_name='sns/create_user_from_weibo.html'):

    oauth_access_token = request.session.get('oauth_access_token', None)
    client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
    client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])
    weibo_user = client.get.users__show(uid=oauth_access_token['uid'])
    weibo_username = weibo_user.screen_name

    json_result = dict()
    template_var = dict()
    template_var['weibo_username'] = weibo_username

    if request.user.is_authenticated() or oauth_access_token is None:
        return HttpResponseRedirect(reverse('home.views.index'))

    try:
        w_user = WeiboUser.objects.get(weibo_username=weibo_username)
        if w_user:
            json_result['wuser_existed'] = '您已经注册了宝时达帐号并绑定到微博，请直接登录'
    except WeiboUser.DoesNotExist:
        if request.method == 'POST':
            get = lambda fieldId: request.POST.get(fieldId, None)
            reg_email = get('reg_email')
            reg_password = get('reg_password')
            reg_re_password = get('reg_re_password')
            reg_company = get('reg_company')
            reg_tax_code = get('reg_tax_code')
            reg_contact_man = get('reg_contact_man')
            reg_mobile = get('reg_mobile')
            reg_survey = get('reg_survey')
            reg_survey_affix = get('reg_survey_affix')
            reg_input_captcha = get('reg_input_captcha')

            if reg_email: json_result['reg_email'] = not User.objects.filter(email = reg_email).count()
            if reg_password and reg_re_password: json_result['reg_re_password'] = True if reg_re_password == reg_password else False
            if reg_company: json_result['reg_company'] = not Company.objects.filter(name = reg_company).count()
            if reg_tax_code: json_result['reg_tax_code'] = True
            if reg_contact_man: json_result['reg_contact_man'] = True
            if reg_mobile: json_result['reg_mobile'] = True
            if reg_survey: json_result['reg_survey'] = True
            if reg_survey_affix: json_result['reg_survey_affix'] = True
            if reg_input_captcha: json_result['reg_input_captcha'] = (is_captcha_match(reg_input_captcha, request.session.get('captcha', None)))

            calculate = 0 #初始化计算器
            for i in json_result.values():
                calculate += i
            if calculate >= 8:
                if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                    ip =  format_baosteel_ip(request.META['HTTP_X_FORWARDED_FOR'])
                else:
                    ip = request.META['REMOTE_ADDR']

                username = 'GM_' + gen_random(4,'mix')
                user = User.objects.create_user(username=username, email=reg_email, password=reg_password)
                user.is_active = True
                user.save()

                company = Company(name=reg_company, organization_code='0000000000', code='111111111', contact=user,
                    corporation_tax=reg_tax_code)
                company.save()

                user_profile = UserProfile(user=user, company=company, mobile=reg_mobile, register_ip=ip, latest_login_ip=ip)
                user_profile.save()

                #init company level & level_name ===>ok
                update_user_points(request,user_id=user.id, code='init')

                reg_survey = RegisterSurvey(user=user, source_code=reg_survey, source_desc=reg_survey_affix)
                reg_survey.save()

                g = Group.objects.get(name='menu_buyer_default')
                g.user_set.add(user)
                #绑定微博
                WeiboUser(
                    user = user,
                    weibo_user_id = oauth_access_token['uid'],
                    weibo_username = weibo_username,
                    oauth_access_token = oauth_access_token['access_token']
                ).save()
                #为其授权到登录状态
                w_user = WeiboUser.objects.get(weibo_user_id=oauth_access_token['uid'])
                user = authenticate(weibo_username=w_user.user.username)
                if user and user.is_active:
                    auth_login(request,user)

                json_result['reg_user_id'] = user.id

            return HttpResponse(json.dumps(json_result), 'application/json')

    return render_to_response(template_name, template_var, context_instance=RequestContext(request))

def _post_weibo(request, msg, url=None):
    oauth_access_token = request.session.get('oauth_access_token', None)
    if oauth_access_token:
        client = APIClient(app_key=APP_KEY, app_secret=APP_SECRET, redirect_uri=_get_weibo_callback_url(request))
        client.set_access_token(oauth_access_token['access_token'], oauth_access_token['expires_in'])
        if url:
            short_url = client.get.short_url__shorten(url_long=url)['urls'][0]['url_short']
        else:
            short_url = ''

        message = msg + short_url
        if len(message) > 140:
            msg_count = 140 - len(short_url)
            message = msg[0:msg_count] + short_url

        client.post.statuses__update(status=message)

# call back url
def _get_weibo_callback_url(request):
    current_site = get_current_site(request)
    domain = current_site.domain
    url = 'http://%s%s' %(domain, reverse('sns_weibo_login_done'))

    return url

# ======================= qq =====================
def qq_login(request):
    client = OauthClient()
    csrf = client.gen_csrf()
    url = client.get_authorize_url(csrf)
    return HttpResponseRedirect(url)

def qq_auth(request):
    code = request.GET.get('code')  # 获取URL参数code
    client = OauthClient()
    token = client.request_token(code) #request_token() => dict
    openid = client.request_openid()   #qq用户openid

    if request.session.has_key('qq_oauth'): del request.session['qq_oauth']
    request.session['qq_oauth'] = {'openid': openid, 'access_token': token['access_token'], 'expires_in': token['expires_in']}

    qq_oauth = request.session.get('qq_oauth', None)
    back_to_url = reverse('home.views.index')

    if token:
        try:
            q_user = QQUser.objects.get(qq_user_id=qq_oauth['openid'])
            user = authenticate(qq_nickname=q_user.user.username)
            if user and user.is_active: auth_login(request,user)
        except QQUser.DoesNotExist:
            back_to_url = reverse('sns_api.views.bind_qq_user')#www.baostar.com:8000/account/login/qq/user/bind/

    return HttpResponseRedirect(back_to_url)

def bind_qq_user(request, template_name):
    template_var = dict()
    result = dict()
    token = request.session.get('qq_oauth', None)['access_token']
    openid = request.session.get('qq_oauth', None)['openid']

    client = OauthClient(token,openid)
    client.init_openapi_url(token=token, openid=openid)
    qq_user = client.request_openapi(api_path_str='user/get_user_info')

    qq_nickname = qq_user['nickname']
    template_var['qq_nickname'] = qq_nickname

    def insert_qq_user(user,openid,qq_nickname, token):
        QQUser( user = user,
            qq_user_id = openid,
            qq_nickname = qq_nickname,
            oauth_access_token = token
        ).save()
        #为其授权到登录状态
        q_user = QQUser.objects.get(qq_user_id=openid)
        user = authenticate(qq_nickname=q_user.user.username)
        if user and user.is_active: auth_login(request,user)
        result['binded'] = 1    #ajax插入user成功，回调跳转条件

    if request.method == 'POST':
        bao_id = request.POST.get('qbind_id', None) #宝时达用户名或注册邮箱
        bao_pwd = request.POST.get('qbind_pwd', None)

        if bao_id:
            try:
                q_user = QQUser.objects.get(qq_nickname=qq_nickname)
                if q_user and (q_user.user.username == bao_id or q_user.user.email == bao_id):
                    result['rebind'] = 1
                    insert_qq_user(q_user.user, openid, qq_nickname, token)
            except QQUser.DoesNotExist:
                try:
                    user = User.objects.get(email=bao_id)
                    result['qbind_id'] = 1
                    result['qbind_pwd'] = (1 if authenticate(username=bao_id, password=bao_pwd) or authenticate(email=bao_id, password=bao_pwd) else 0)
                    if result['qbind_id'] and result['qbind_pwd']:
                        insert_qq_user(user,openid,qq_nickname, token)
                except User.DoesNotExist:
                    try:
                        user = User.objects.get(username=bao_id)
                        result['qbind_id'] = 1
                        result['qbind_pwd'] = (1 if authenticate(username=bao_id, password=bao_pwd) or authenticate(email=bao_id, password=bao_pwd) else 0)
                        if result['qbind_id'] and result['qbind_pwd']:
                            insert_qq_user(user,openid,qq_nickname, token)
                    except User.DoesNotExist:
                        result['qbind_id'] = 0 #id不存在
                        result['qbind_pwd'] = None #json解析为null值，不显示密码提示
        else:
            result['qbind_id'] = None

        if not bao_pwd: result['qbind_pwd'] = None

        return HttpResponse(json.dumps(result), 'application/json')

    return auth_login_view(request, template_name, extra_context=template_var)

def create_user_from_qq(request,template_name):
    template_var = dict()
    json_result = dict()
    qq_oauth = request.session.get('qq_oauth', None)
    token = qq_oauth['access_token']
    openid = qq_oauth['openid']

    client = OauthClient(token,openid)
    client.init_openapi_url(token=token, openid=openid)
    qq_user = client.request_openapi(api_path_str='user/get_user_info')

    qq_nickname = qq_user['nickname']
    template_var['qq_nickname'] = qq_nickname

    if request.user.is_authenticated() or qq_oauth is None:
        return HttpResponseRedirect(reverse('home.views.index'))

    try:
        q_user = QQUser.objects.get(qq_nickname=qq_nickname)
        if q_user: json_result['wuser_existed'] = '您已经注册了宝时达帐号并绑定到微博，请直接登录'
    except QQUser.DoesNotExist:
        if request.method == 'POST':
            get = lambda fieldId: request.POST.get(fieldId, None)
            reg_email = get('reg_email')
            reg_password = get('reg_password')
            reg_re_password = get('reg_re_password')
            reg_company = get('reg_company')
            reg_tax_code = get('reg_tax_code')
            reg_contact_man = get('reg_contact_man')
            reg_mobile = get('reg_mobile')
            reg_survey = get('reg_survey')
            reg_survey_affix = get('reg_survey_affix')
            reg_input_captcha = get('reg_input_captcha')

            if reg_email: json_result['reg_email'] = not User.objects.filter(email = reg_email).count()
            if reg_password and reg_re_password: json_result['reg_re_password'] = True if reg_re_password == reg_password else False
            if reg_company: json_result['reg_company'] = not Company.objects.filter(name = reg_company).count()
            if reg_tax_code: json_result['reg_tax_code'] = True
            if reg_contact_man: json_result['reg_contact_man'] = True
            if reg_mobile: json_result['reg_mobile'] = True
            if reg_survey: json_result['reg_survey'] = True
            if reg_survey_affix: json_result['reg_survey_affix'] = True
            if reg_input_captcha: json_result['reg_input_captcha'] = (is_captcha_match(reg_input_captcha, request.session.get('captcha', None)))

            calculate = 0 #初始化计算器
            for i in json_result.values():
                calculate += i
            if calculate >= 8:
                if request.META.has_key('HTTP_X_FORWARDED_FOR'):
                    ip =  format_baosteel_ip(request.META['HTTP_X_FORWARDED_FOR'])
                else:
                    ip = request.META['REMOTE_ADDR']

                username = 'GM_' + gen_random(4,'mix')
                user = User.objects.create_user(username=username, email=reg_email, password=reg_password)
                user.is_active = True
                user.save()

                company = Company(name=reg_company, organization_code='0000000000', code='111111111', contact=user,
                    corporation_tax=reg_tax_code)
                company.save()

                user_profile = UserProfile(user=user, company=company, mobile=reg_mobile, register_ip=ip, latest_login_ip=ip)
                user_profile.save()

                #init company level & level_name ===>ok
                update_user_points(request,user_id=user.id, code='init')

                reg_survey = RegisterSurvey(user=user, source_code=reg_survey, source_desc=reg_survey_affix)
                reg_survey.save()

                g = Group.objects.get(name='menu_buyer_default')
                g.user_set.add(user)
                #绑定微博
                QQUser(
                    user = user,
                    qq_user_id = openid,
                    qq_nickname = qq_nickname,
                    oauth_access_token = token
                ).save()
                #为其授权到登录状态
                q_user = QQUser.objects.get(qq_user_id=openid)
                user = authenticate(qq_nickname=q_user.user.username)
                if user and user.is_active:
                    auth_login(request,user)

                json_result['reg_user_id'] = user.id

            return HttpResponse(json.dumps(json_result), 'application/json')
    return auth_login_view(request, template_name, extra_context=template_var)