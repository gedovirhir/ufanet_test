from .basemodel import basemodel, Field, query
from .users import user
from .message_tag import message_tag

class message(basemodel):
    __tablename__ = 'messages'
    
    user_id = Field('INT NOT NULL')
    content = Field('TEXT NOT NULL')
    timestamp = Field('TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
    
    _user_id_fk = Field('FOREIGN KEY (user_id) REFERENCES users(id) ON UPDATE CASCADE')
    
    @classmethod
    def add_tags(cls,
                 message_id,
                 tag_id_list
    ):
        for tid in tag_id_list:
            message_tag.add(
                message_id = message_id,
                tag_id = tid
            )
        
    @classmethod
    def u_lastmessage(cls, user_id):
        mesg = cls.get(
            fields_to_select=['user_id, content, timestamp'],
            user_id=user_id,
            order_by="timestamp DESC, id DESC",
            limit=1
        )
        
        return dict(
                    zip(
                        ('id', 'user_id', 'content', 'timestamp'),
                        mesg[0]
                    )
                )

    @classmethod
    def u_message_with_tag(
        cls,
        user_id,
        tags
    ):
        t = '('+ ','.join(["'%s'" % i for i  in tags]) +')'
        
        res = query(
            """
            SELECT id FROM(
                SELECT m.id, count(*) cnt, max(count(*)) OVER () mx 
                FROM messages m
                INNER JOIN message_tag m_t ON m.id = m_t.message_id
                INNER JOIN tags t ON m_t.tag_id = t.id
                WHERE m.user_id = {user_id} AND 
                      t.title IN {tags}
                GROUP BY m.id
                ) s WHERE s.cnt = s.mx
                    ORDER BY 1;
            
            """\
                .format(
                    user_id=user_id,
                    tags=t
                )
        )
        return res
    
    
