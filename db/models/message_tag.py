from .basemodel import basemodel, Field, query

class message_tag(basemodel):
    __tablename__ = 'message_tag'
    
    id = None
    
    message_id = Field('INT NOT NULL')
    tag_id = Field('INT NOT NULL')
    
    _message_id_fk = Field('FOREIGN KEY(message_id) REFERENCES messages(id) ON DELETE CASCADE ON UPDATE CASCADE')
    _tag_id_fk = Field('FOREIGN KEY(tag_id) REFERENCES tags(id) ON DELETE CASCADE ON UPDATE CASCADE')
    
    _message_tag_pk = Field('PRIMARY KEY(message_id, tag_id)')