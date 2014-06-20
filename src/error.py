# coding=utf-8
__author__ = 'Michael Fan'

error_info = {
  u'正确': 0, # no error
  u'错误': 1,
  u'密码错误': 2,
  u'未知错误': 9999
}

# reverse from `enum_error_info`
error_code = { str(v): k for k,v in error_info.items() }

