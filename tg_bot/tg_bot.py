# -*- coding: utf-8 -*-

from re import M
import sys
import os
from datetime import datetime
import re

sys.path.append(os.path.abspath('./config'))
from conf import TOKEN
from tg_bot_api import tgbot

sys.path.append(os.path.abspath('./'))
from db.db_api import (user,
                       message as msg, 
                       message_tag,
                       tag,
                       query,
                       create_tables_if_not_exist)



bot = tgbot(
    TOKEN
)

TAG_REG = r'#[^_]\w[\w-]*[^_\W]'

def db_user_id(message):
    return user.get(user_tg_id=message['from']['id'])[0][0]

def note_render(id, text, datetime):
    return "Заметка id {id}: {datetime}\n{text}".format(
            id=id,
            text=text,
            datetime=str(datetime)
        )
def tag_render(title, desc):
    return "Тэг: #{title}\nОписание: {desc}".format(
        title=title,
        desc=desc
    )
def find_tags(text):
    tags = re.findall(TAG_REG, text)
    tags = list(
        map(
            lambda t: t[1:],
            tags
        )
    )
    return tags

@bot.message_handler("/start")
def start_handler(message):
    uid = message['from']['id']
    
    if not user.get(user_tg_id=uid):
        user.add(
            user_tg_id=uid,
            username=message['from']['username']
        )

        return "Вы успешно зарегистрированы в системе"
    return "Вы уже зарегистрированы "

@bot.message_handler('/write')
def write_handler(message):
    bot.set_next_user_step(message,
                           write_handler_message_await)
    
    return "Напишите заметку. Для отмены введите /cancel"
def write_handler_message_await(message):
    if message['text'] != '/cancel':
        uid = db_user_id(message)
        msgid = msg.add(
            with_id_return=True,
            user_id=uid,
            content=message['text'],
            timestamp=datetime.fromtimestamp(message['date'])
        )
        
        tags_id = []
        for t in find_tags(message['text']):
            tg = tag.get(title=t)
            if tg: tags_id.append(tg[0][0])
            else:
                tags_id.append(tag.add(with_id_return=True, 
                              title=t))
        
        msg.add_tags(msgid,tags_id)
            
        
        return "Заметка успешно добавлена"
    return "Отмена."

@bot.message_handler('/read_last')
def read_last_handler(message):
    uid = db_user_id(message)
    
    m = msg.u_lastmessage(
        uid
    )
    
    return note_render(
        id=m['id'],
        text=m['content'],
        datetime=m['timestamp']
    )

@bot.message_handler('/read')
def read_handler(message):
    try:
        mid = message['text'].split(' ')[1]
        mid = int(mid)

        mesg = msg.get(id=mid,
                       fields_to_select=['user_id','content', 'timestamp'])

        if not mesg: return "Заметка {id} не найдена".format(id=mid)
        mesg = mesg[0]

        mesg_user = user.get(id=mesg[1],
                             fields_to_select=['user_tg_id'])[0]

        if mesg_user[1] != message['from']['id']: return "Заметка {id} принадлежит другому пользователю".format(id=mid)

        return note_render(
            id=mesg[0],
            text=mesg[2],
            datetime=mesg[3]
        )
    except Exception as ex:
        return "Некорректный запрос"
@bot.message_handler('/read_all')
def read_all_handler(message):
    uid = db_user_id(message)
    
    all_notes = msg.get(user_id=uid,
                        order_by='datetime',
                        fields_to_select=['content', 'timestamp'])
    
    for note in all_notes:
        bot.send_message(
            message['chat']['id'],
            note_render(
                note[0],
                note[1],
                note[2]
            )
        )
@bot.message_handler('/read_tag')
def read_tag_handler(message):
    try:
        tags = message['text'].split(' ')[1:]
        if not tags: raise
        
        tags = list(map(
            lambda t: t[1:] if t.startswith('#') else t,
            tags
        ))
        
        uid = db_user_id(message)
        
        all_tagged_mesg = msg.u_message_with_tag(
            uid,
            tags
        )
        if not all_tagged_mesg: return "Не найдено заметок"
        
        for note in all_tagged_mesg:
            note = msg.get(id=note[0],
                    fields_to_select=['content', 'timestamp'])[0]
            bot.send_message(
                message['chat']['id'],
                note_render(
                    note[0],
                    note[1],
                    note[2]
                )
            )
    except Exception as ex:
        return "Некорректный запрос"

@bot.message_handler('/write_tag')
def write_tag_handler(message):
    try:
        tag_name, desc = message['text'].split(' ', 2)[1:]
        
        tg = tag.get(title=tag_name)
        if tg:
            tag.update(tg[0][0],
                       {'description' : desc})
            return "Описание тэга обновлено"
        else:
            tag.add(
                title=tag_name,
                description=desc
            )
            return "Тэг успешно добавлен"
    except Exception as ex:
        return "Некорректный запрос"

@bot.message_handler('/tag')
def tag_handler(message):
    try:
        tags = message['text'].split(' ')[1:]
        if not tags: raise
    
        for tg in tags:
            db_tg = tag.get(title=tg,
                            fields_to_select=['title', 'description'])[0]
            
            bot.send_message(
                message['chat']['id'],
                tag_render(
                    title=db_tg[1],
                    desc=db_tg[2]
                )
            )
        
    except Exception as ex:
        return "Некорректный запрос"

@bot.message_handler('/tag_all')
def tag_all_handler(message):
    all_tags = tag.get(fields_to_select=['title', 'description'])
    
    for tg in all_tags:
        bot.send_message(
            message['chat']['id'],
            tag_render(
                tg[1],
                tg[2]
            )
        )

if __name__ == '__main__':
    create_tables_if_not_exist()
    bot.start_pooling()
