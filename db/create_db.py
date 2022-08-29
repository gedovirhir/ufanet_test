# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import pymysql

sys.path.append(os.path.abspath('./config'))
from conf import (MYSQL_DB,
                  MYSQL_USER,
                  MYSQL_PASSWORD,
                  MYSQL_HOST,
                  MYSQL_PORT
                  )


_db_name = MYSQL_DB
_user_name = MYSQL_USER
_password = MYSQL_PASSWORD
_host = MYSQL_HOST
_port = MYSQL_PORT

def connection():
    conn = pymysql.connect(
        host=_host, 
        user=_user_name,
        password=_password,
        database=_db_name,
        port=_port,
        charset='utf8'
    )
    return conn
def query(
    sql_query, 
    with_id_return = False
):
    conn = connection()
    c = conn.cursor()
    
    c.execute(
        sql_query
    )

    res = c.lastrowid if with_id_return else c.fetchall()
    conn.commit()
    conn.close()
    
    return res
def _create_tables(models, with_drop = False):
    for m in models:
        fields = ', '.join(
            [
                '{} {}'.format(k,v.sql_content)
                if not k.startswith('_')
                else '{}'.format(v.sql_content)
                for k, v in m.getFields().items()
            ]
        )
        query(
            """
            CREATE TABLE IF NOT EXISTS {tablename}(
                {fields}
            );
            """\
                .format(
                    tablename=m.__tablename__,
                    fields=fields
                )
        )
def _configure_db():
    query('SET NAMES utf8;')
    query('SET CHARACTER SET utf8;')
    query('SET character_set_connection=utf8;')
def create_db(models):
    _configure_db()
    _create_tables(models)

