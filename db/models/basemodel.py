# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import sys
import pymysql

sys.path.append(os.path.abspath('./db'))
from create_db import query

class Field:
    
    def __init__(self,
                 sql_content
    ):
        self.sql_content = sql_content
class basemodel:
    
    __tablename__ = ""
    
    id = Field("INTEGER PRIMARY KEY AUTO_INCREMENT")
    
    
    @staticmethod
    def __render_terms(
        dict_of_terms
    ):
        terms = ''
        for term, value in dict_of_terms.items():
            terms += '{term} = {item} AND '.format()
            #' AND '.join('{}={}'.format(item, value) for item, value in a.items())
    @classmethod
    def getFields(cls):
        fields = {}
        for f in dir(cls):
            if (not f.startswith('__')):
                fval = getattr(cls, f)
                
                if isinstance(fval, Field):
                    fields.update(({f : fval}))
                    
        return fields
    @classmethod
    def renderFields(cls,
                 fields_dict,
                 sep=" AND "
    ):
        cls_fields = cls.getFields()
        
        return sep.join(["{}='{}'".format(item, value)
                              for item, value in fields_dict.items()
                              if item in cls_fields
                              ]
                            )
    @classmethod
    def get(
        cls,
        fields_to_select = [],
        order_by = 1,
        limit = 20,
        offset = 0,
        
        **fields
    ):
        terms = cls.renderFields(fields)
        if not terms: terms = 'TRUE'
        
        f_to_select = ', ' + ', '.join(fields_to_select) if fields_to_select else ''
        
        res = query(
                """
                SELECT id{f_to_select}
                FROM {table}
                WHERE {terms} 
                ORDER BY '{o_by}'
                LIMIT {limit}
                OFFSET {offset};
                """
                .format(
                    f_to_select=f_to_select,
                    table=cls.__tablename__,
                    terms=terms,
                    o_by=order_by,
                    limit=limit,
                    offset=offset
                )
            )
        
        return res
    @classmethod
    def add(
        cls,
        with_id_return = False,
        **fields
    ):
        cls_fields = cls.getFields()
        cols = [f for f in fields.keys()
                   if f in cls_fields]
        
        vals = ["'%s'" % fields[k] for k in cols]
        
        return query(
            """
            INSERT INTO {table}({cols}) VALUES ({vals})
            """\
                .format(
                    table=cls.__tablename__,
                    cols=','.join(cols),
                    vals=','.join(vals)
                ), 
                with_id_return=with_id_return
        )
    @classmethod
    def update(
        cls,
        id, 
        updateDict
    ):
        set_col = cls.renderFields(updateDict, ', ')
        
        return query(
            """
            UPDATE {table}
            SET {set_col}
            WHERE id={id}
            """\
                .format(
                    table=cls.__tablename__,
                    set_col=set_col,
                    id=id
                )
        )
    
    