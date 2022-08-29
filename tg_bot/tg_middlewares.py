# -*- coding: utf-8 -*-
from datetime import date, datetime
import sys
import os

sys.path.append(os.path.abspath('./'))
from db.db_api import (user,
                       query)


class _MiddlewareBase:
    def __init__(self, _get_response):
        self._get_response = _get_response
    
    def __call__(self, message):
        response = None
        if hasattr(self, "process_request"):
            response = self.process_request(message)
        response = response or self._get_response(message)
        if hasattr(self, "process_response"):
            response = self.process_response(message, response)
        return response

class FormatMiddleware(_MiddlewareBase):
    def process_request(self, message):
        if not message.get('text'): 
            return "Бот обрабатывает только текстовые сообщения"
        
class SecurityMiddleware(_MiddlewareBase):
    def process_request(self, message):
        if message['chat']['type'] != 'private':
            return "Неподходящий для общения тип чата"
        u = user.get(user_tg_id=message['from']['id'])
        if not u and message['text'].strip() != '/start':
            return "Вы не зарегистрированы. Вызовите команду /start"
        
class NextStepMiddleware(_MiddlewareBase):
    
    users_next_steps = {
        
    }

    def process_request(self, message):
        uid = message['chat']['id']
        
        if uid in self.users_next_steps:
            r = self.users_next_steps[uid](message)
            self.users_next_steps.pop(uid)
            
            return r
    @classmethod
    def registrate_next_step(cls, chat_id, func):
        cls.users_next_steps.update(
            {chat_id : func}
        )
    @classmethod
    def remove_next_step(cls, chat_id):
        cls.users_next_steps.pop(chat_id)

class LoggingMiddleware(_MiddlewareBase):
    path_to_log_file = './logs/message_logs.txt'
    
    def process_request(self, message):
        with open(self.path_to_log_file, 'a') as f:
            f.write(
                """
                {datetime}  {id}    {text}
                """\
                    .format(
                        datetime=datetime.fromtimestamp(message['date']),
                        id=message['from']['id'],
                        text=message['text'].encode('utf-8')
                    )
            )