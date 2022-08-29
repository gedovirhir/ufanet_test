from .basemodel import basemodel, Field, query

class user(basemodel):
    __tablename__ = 'users'
    
    user_tg_id = Field('INT NOT NULL UNIQUE')
    username = Field('VARCHAR(255) NOT NULL')