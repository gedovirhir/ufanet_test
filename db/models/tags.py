#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymysql import IntegrityError

from .basemodel import basemodel, Field, query


class tag(basemodel):
    __tablename__ = 'tags'
    
    title = Field('VARCHAR(255) NOT NULL UNIQUE')
    description = Field('TEXT')
    
    """@classmethod
    def add(cls, **fields):
        id = cls.get(title=fields['title'])
        
        if id:
            cls.update(
                id=id,
                updateDict={'description' : fields['description']}
                )
        else:
            return super().add(with_id_return=True, **fields)"""

    
    