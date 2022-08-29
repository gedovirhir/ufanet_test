# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .models import (user,
                    tag,
                    message,
                    message_tag)

from create_db import query, create_db, _db_name

ALL_MODELS = [
    user,
    tag,
    message,
    message_tag,
]

def check_existing():
    exist = True
    for m in ALL_MODELS:
        q = query(
            """
            SHOW TABLES FROM `{db_name}` like '{table}';
            """\
                .format(
                    db_name=_db_name,
                    table=m.__tablename__
                )
        )
        if not q: 
            exist = False
            break
    return exist

def create_tables_if_not_exist():
    if not check_existing():
        create_db(
            [user,tag,message,message_tag]
        )