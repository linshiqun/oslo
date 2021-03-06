#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@Author: Youshumin
@Date: 2019-11-06 09:08:58
@LastEditors  : YouShumin
@LastEditTime : 2020-01-19 16:22:27
@Description: 
'''
import logging
from collections import defaultdict

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

LOG = logging.getLogger(__name__)


class DBPool(object):
    def __init__(self):
        self.subdb = defaultdict(list)

    def add(self, dbname, db):
        self.subdb[dbname].append(db)

    def remove(self, dbname, db):
        self.subdb[dbname].remove(db)

    def get(self, dbname):
        return self.subdb[dbname]


db_pool = DBPool()


class mysqlHanlder(object):
    def init(self, dbname=None, dburl=None, dbecho=False, pool_size=10):
        LOG.info("dbname: {}, dburl: {}".format(dbname, dburl))
        self.db_name = dbname
        self.db_url = dburl
        self.db_echo = dbecho
        self.db_pool_size = pool_size
        self._check_db_name()

    def _check_db_name(self):
        resp = db_pool.get(self.db_name)
        if not resp:
            self._init_engin()
            self._init_session()
            db_pool.add(self.db_name, [self.session, self.engin])

    def _init_engin(self):
        self.engin = create_engine(self.db_url,
                                   encoding="utf-8",
                                   echo=self.db_echo,
                                   pool_size=self.db_pool_size,
                                   pool_recycle=3600,
                                   pool_pre_ping=True)

    def _init_session(self):
        self.session = scoped_session(
            sessionmaker(bind=self.engin, expire_on_commit=False))

    def get_session(self, db_name):
        db_list = db_pool.get(db_name)
        if db_list:
            db = db_list[0][0]
            return db()
        else:
            LOG.error("get_db: {} faild".format(db_name))
        return ""

    def get_engin(self, db_name):
        db_list = db_pool.get(db_name)
        if db_list:
            db = db_list[0][1]
            return db
        else:
            LOG.error("get_db: {} faild".format(db_name))
        return ""
