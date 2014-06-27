#! /usr/bin/python
# coding=utf-8

__author__ = 'Michael Fan'

import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Sequence, ForeignKey, DateTime
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
import os
import tornado

path = os.path.dirname(__file__)

# http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
# db_connect_string = 'mysql+mysqldb://root:admin@localhost/?charset=utf8'
db_connect_string = 'mysql+mysqldb://root:root@localhost/life?charset=utf8'
# eg = create_engine("sqlite:///%s/../db/dev.db" % path, echo=True)
eg = create_engine(db_connect_string, echo=True)

# The "Session" class
DbSession = sessionmaker(bind=eg)

Base = declarative_base()


class Calendar(Base):
  """日历"""
  __tablename__ = 'calendar'
  id = Column(Integer, Sequence('seq_calendar_id'), primary_key=True)
  year = Column(Integer)
  month = Column(Integer)
  day = Column(Integer)
  holiday_code = Column(String(10)) # if {null}, that day is a holiday
  dinner_type = Column(Integer) # 1=inner strore || 2=take-away


  def __repr__(self):
    if self.holiday_code:
      return "<date('%s-%s-%s', holiday_code='%s')>" % (
        self.year, self.month, self.day, self.holiday_code)
    else:
      return "<User('%s-%s-%s')>" % (
        self.year, self.month, self.day)
  

class Holiday(Base):
  __tablename__ = 'holiday'
  id = Column(Integer, Sequence('seq_holiday_id'), primary_key=True)
  code = Column(Integer) # 假日编码
  desc = Column(String(30))

  def __repr__(self):
    return "<Holiday(type='%s', desc='%s')>" % (
      self.code, self.desc)


class Mail(Base):
  """Iner site mail, notifications"""
  __tablename__ = 'mail'
  id = Column(Integer, Sequence('seq_mail_id'), primary_key=True)
  from_user_id = Column(Integer)
  to_user_id = Column(Integer)
  status = Column(Integer) # -10=drafts 0=unchecked, 10=checked, 20=droped
  content = Column(String(1000))
  can_reply = Column(Integer)


class Session(Base):
  """User session"""
  __tablename__ = 'session'
  id = Column(Integer, Sequence('seq_mail_id'), primary_key=True)
  session_id = Column(String(80)) # Session id(eq cookie.sid)
  user_id = Column(String(80)) # user id
  data = Column(String(80)) # data
  expire_date = Column(String(80)) # session id

  def __repr__(self):
    return '%s' % self.id

class Site(Base):
  """Site"""
  __tablename__ = 'site'
  id = Column(Integer, primary_key=True)
  name = Column(String(80)) # site name
  domain = Column(String(80)) # site domain 
  desc = Column(String(80)) # Description
   

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
  dpt_id = Column(Integer, ForeignKey('dpt.id')) # Department id
  dpt = relationship("Department", backref=backref("user", order_by=id))

  username = Column(String(30)) # Login username
  email = Column(String(50))
  password = Column(String(50)) # Default {null} is allowed

  cn_name = Column(String(30)) # 姓名
  worker_code = Column(String(30)) # 工号
  first_name = Column(String(30)) # English given name
  last_name = Column(String(30)) # English family name
  nick = Column(String(50))
  mobile = Column(String(50))
  imqq = Column(String(50)) # Tencent im tool QQ number

  joined_date = Column(DateTime(), default=datetime.datetime.now())
  last_active_date = Column(DateTime())
  last_login_date = Column(DateTime())
  last_lgoin_ip = Column(Integer)

  is_root = Column(Integer, default=0) # system root admin

  def __repr__(self):
    """Show in front page"""
    _show_name = ''
    if self.username:
      _show_name = self.username
    else:
      _show_name = self.email

    return tornado.escape.xhtml_escape(_show_name)


class Department(Base):
  __tablename__ = 'dpt'
  id = Column(Integer, Sequence('seq_dpt_id'), primary_key=True)
  parent_dpt_id = Column(Integer, ForeignKey('dpt.id')) # Father department id
  # user_id = Column(Integer, ForeignKey('user.id')) # user.id
  manager_id = Column(Integer) #, ForeignKey('user.id')) # user.id
  # manager = relationship("User", backref=backref("dpt", order_by=id))

  name = Column(String(30)) # 称名
  code = Column(String(30)) # 代码
  sub_dpts = relationship("Department") # All sub departments

  def __repr__(self):
    """Show in page"""
    return self.name

class DinnerBook(object):
  """docstring for UserDinner"""
  __tablename__ = 'dinner_book'
  id = Column(Integer, Sequence('seq_dinner_id'), primary_key=True)
  user_id = Column(Integer, ForeignKey('user.id')) # Father department id
  calendar_id = Column(Integer, ForeignKey('calendar.id')) # Father department id
  is_take_away = Column(Integer) # 我要外带 
    


if __name__ == '__main__':
  # Create database before init tables:
  # mysql> create database life DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
  # Base.metadata.drop_all(eg)
  Base.metadata.create_all(eg)
