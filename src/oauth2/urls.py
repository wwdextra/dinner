__author__ = 'micfan'

from django.conf.urls import patterns, url

urlpatterns = patterns('sns_api.views',
    url(r'^weibo/login/$', 'weibo_login'),
    url(r'^weibo/login/done/', 'weibo_auth', name='sns_weibo_login_done'),
    url(r'^weibo/user/bind/', 'bind_weibo_user', name='bind_weibo_user'),
    url(r'^weibo/user/create/', 'create_user_from_weibo', name='create_user_from_weibo'),
)

urlpatterns += patterns('sns_api.views',
    url(r'^qq/login/$', 'qq_login', name='sns_qq_login'),
    url(r'^qq/login/done/', 'qq_auth', name='sns_qq_login_done'),
    url(r'^qq/user/bind/', 'bind_qq_user', {'template_name':'sns/bind_qq_user.html'}, name='bind_qq_user'),
    url(r'^qq/user/create/', 'create_user_from_qq', {'template_name':'sns/cteate_user_from_qq.html'}, name='sns_create_user_from_qq'),

)