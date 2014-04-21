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

path = os.path.dirname(__file__)

## TODO: multiy database string make up
# http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html
eg = create_engine("sqlite:///%s/dev.db" % path, echo=True)

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
  holiday_code = Column(String(2)) # if {null}, that day is a holiday

  def __repr__(self):
    if holiday_code:
      return "<User('%s-%s-%s', holiday_code='%s')>" % (
        self.year, self.month, self.day, self.holiday_code)
    else:
      return "<User('%s-%s-%s')>" % (
        self.year, self.month, self.day)


class Department(Base):
  __tablename__ = 'dpt'
  id = Column(Integer, Sequence('seq_dpt_id'), primary_key=True)
  name = Column(String(30)) # 称名
  code = Column(String(30)) # 代码

  parent_dpt_id = Column(Integer, ForeignKey('dpt.id')) # Father department id
  manager_id = Column(Integer, ForeignKey('user.id')) # Foreign key to user
  sub_dpts = relationship("Department") # All sub departments
  

class Mail(Base):
  """Iner site mail, notifications"""
  __tablename__ = 'mail'
  id = Column(Integer, Sequence('seq_mail_id'), primary_key=True)
  from_user_id = Column(Integer)
  to_user_id = Column(Integer)
  status = Column(Integer) # -10=drafts 0=unchecked, 10=checked, 20=droped
  content = Column(String(1000))
  can_reply = Column(Integer) # 


class Holiday(Base):
  __tablename__ = 'holiday'
  id = Column(Integer, Sequence('seq_holiday_id'), primary_key=True)
  code = Column(Integer) # 假日编码
  desc = Column(String(30))

  def __repr__(self):
    return "<Holiday(type='%s', desc='%s')>" % (
      self.code, self.desc)    


class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, Sequence('seq_user_id'), primary_key=True)
  username = Column(String(30)) # Login username
  password = Column(String(50)) # Default {null} is allowed

  worker_code = Column(String(30)) # 工号
  cn_name = Column(String(30)) # 姓名
  first_name = Column(String(30)) # English given name
  last_name = Column(String(30)) # English family name
  nick = Column(String(50))
  mobile = Column(String(50))
  email = Column(String(50))
  imqq = Column(String(50)) # Tencent im tool QQ number
  dpt_id = Column(Integer) # Department id
  joined_date = Column(DateTime(), default=datetime.datetime.now())
  last_login_date = Column(DateTime(), default=datetime.datetime.now())
  last_lgoin_ip = Column(Integer) 
  is_root = Column(Integer, default=0) # system root admin

  # mail = relationship("Mail")

  def __repr__(self):
    return "<User(name='%s', fullname='%s', password='%s')>" % (
      self.name, self.fullname, self.password)


if __name__ == '__main__':
  """Create tables by run it"""
  Base.metadata.drop_all(eg)
  Base.metadata.create_all(eg)
