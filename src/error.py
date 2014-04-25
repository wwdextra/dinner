# coding=utf-8
__author__ = 'Michael Fan'

enum_error_info = {
  u'正确': 0, # no error
  u'密码错误': 1,
  u'未知错误': 9999
}

# reverse from `enum_error_info`
enum_error_code = { str(v): k for k,v in enum_error_info.items() }

