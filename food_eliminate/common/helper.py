# -*- coding: utf-8 -*-

import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import configparser
import logging

logger = logging.getLogger(__name__)
conf = configparser.ConfigParser()
conf.read("config/mysql.conf")


class DB(object):
    def get_pool(self):
        pool = PooledDB(
            creator=pymysql,
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            host=conf.get("mySQLDB", "host"),
            port=int(conf.get("mySQLDB", "port")),
            db=conf.get("mySQLDB", "name"),
            user=conf.get("mySQLDB", "user"),
            password=conf.get("mySQLDB", "password"),
            charset="utf8",
        )
        return pool

    def connect(self):
        pool = self.get_pool()
        conn = pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 以 字典的方式 显示
        return conn, cursor

    def connect_close(self, conn, cursor):
        cursor.close()
        conn.close()

    def fetch_all(self, sql):
        logger.info("fetch all sql: %s" % sql)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            record_list = cursor.fetchall()
            return record_list
        except Exception as e:
            logger.error("error: %s" % e)
            conn.rollback()
        finally:
            self.connect_close(conn, cursor)

    def fetch_one(self, sql):
        logger.info("fetch one sql: %s" % sql)
        conn, cursor = self.connect()
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except Exception as e:
            logger.error("error: %s" % e)
            conn.rollback()
        finally:
            self.connect_close(conn, cursor)

    def insert(self, sql):
        logger.info("insert sql: %s" % sql)
        conn, cursor = self.connect()
        try:
            row = cursor.execute(sql)
            conn.commit()
            return row
        except Exception as e:
            logger.error("error: %s" % e)
        finally:
            self.connect_close(conn, cursor)

    def insert_many(self, sql, data_list):
        logger.info("insert many sql: %s" % sql)
        conn, cursor = self.connect()
        try:
            row = cursor.executemany(sql, data_list)
            conn.commit()
            return row
        except Exception as e:
            logger.error("error: %s" % e)
        finally:
            self.connect_close(conn, cursor)
