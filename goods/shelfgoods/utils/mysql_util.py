#!/usr/bin/python3

import pymysql
import sys
import traceback
import set_config as config

import logging
logger = logging.getLogger("django")

class MysqlUtil:
    connect = None
    def __init__(self,mysql_info_name):
        host = config.mysql_info[mysql_info_name]['host']
        user = config.mysql_info[mysql_info_name]['user']
        password = config.mysql_info[mysql_info_name]['password']
        port = config.mysql_info[mysql_info_name]['port']
        db = config.mysql_info[mysql_info_name]['db']
        try:
            self.connect = pymysql.connect(host=host, port=port, user=user, passwd=password, db=db,charset='utf8')
        except Exception:
            logger.error("mysql connect failed , host="+str(host))
            sys.exit()

    def close(self):
        self.connect.close()

    def selectAll(self,sql):
        cursor = self.connect.cursor(sql)
        cursor.execute(sql)
         # 获取所有记录列表
        results = cursor.fetchall()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return results

    def selectOne(self,sql):
        cursor = self.connect.cursor(sql)
        cursor.execute(sql)
         # 获取所有记录列表
        result = cursor.fetchone()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return result

    def insertOne(self,sql,params_dict):
        cursor = self.connect.cursor()
        try:
            cursor.execute(sql)
            self.connect.commit()
        except:
            # Rollback in case there is any error
            self.connect.rollback()
            traceback.print_exc()
