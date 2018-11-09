# -*- coding: utf-8 -*-

import pymysql
from DBUtils.PooledDB import PooledDB, SharedDBConnection
import configparser

conf = configparser.ConfigParser()
conf.read("common/config.conf")


class DB(object):
    def get_pool(self, env):
        pool = PooledDB(
            creator=pymysql,
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            host=conf.get(env, "dbhost"),
            port=int(conf.get(env, "dbport")),
            db=conf.get(env, "dbname"),
            user=conf.get(env, "dbuser"),
            password=conf.get(env, "dbpassword"),
            charset="utf8",
        )
        return pool

    def connect(self, env):
        pool = self.get_pool(env)
        conn = pool.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 以 字典的方式 显示
        return conn, cursor

    def connect_close(self, conn, cursor):
        cursor.close()
        conn.close()

    def fetch_all(self, env, sql):
        print("fetch all sql: ", sql)
        conn, cursor = self.connect(env)
        try:
            cursor.execute(sql)
            record_list = cursor.fetchall()
            return record_list
        except Exception as e:
            print('error: ', e)
            conn.rollback()
        finally:
            self.connect_close(conn, cursor)

    def fetch_one(self, env, sql):
        print("fetch one sql: ", sql)
        conn, cursor = self.connect(env)
        try:
            cursor.execute(sql)
            result = cursor.fetchone()
            return result
        except Exception as e:
            print('error: ', e)
            conn.rollback()
        finally:
            self.connect_close(conn, cursor)

    def insert(self, env, sql):
        print("insert sql: ", sql)
        conn, cursor = self.connect(env)
        try:
            row = cursor.execute(sql)
            conn.commit()
            return row
        except Exception as e:
            print('error: ', e)
        finally:
            self.connect_close(conn, cursor)

    def insert_many(self, env, sql, data_list):
        print("insert sql: ", sql)
        conn, cursor = self.connect(env)
        try:
            row = cursor.executemany(sql, data_list)
            conn.commit()
            return row
        except Exception as e:
            print('error: ', e)
        finally:
            self.connect_close(conn, cursor)
