# -*- coding: utf-8 -*-

import sys
import os
import requests
import json

from tg_middlewares import (SecurityMiddleware, 
                            NextStepMiddleware,
                            FormatMiddleware,
                            LoggingMiddleware)
#r = requests.get(request_url.format(
#    bot_token=TOKEN,
#    operation="getUpdates"), params={'offset' : : 163754265, 'timeout' : 300})
#
class tgbot:
    
    _commands = {
        
    }
    _last_update_offset = 0
    _request_url = "https://api.telegram.org/bot{bot_token}/{operation}"
    
    _middlewares = [
        FormatMiddleware,
        LoggingMiddleware,
        SecurityMiddleware,
        NextStepMiddleware,
    ]
    _middleware_chain = None
    
    def __init__(self,
                 token
    ):
        self._token = token
    
    def __send_request(self,
                      method,
                      operation, 
                      params
    ):
        request = getattr(requests, method)
        
        return  request(self._request_url.format(
                        bot_token=self._token,
                        operation=operation
                    ), 
                    params=params
                )
    def send_message(self, chat_id, text):
        return self.__send_request(
            method='get',
            operation='sendMessage',
            params={'chat_id' : chat_id,'text' : text}
        )
    
    def __process_update(self, update):
        update_id = update['update_id']
        message = update['message']
        chat_id = message['chat']['id']

        try:
            response = self.get_response(message)
        except Exception as ex:
            response = "Что-то пошло не так"
        
        if response:
            self.send_message(
                chat_id,
                response
            )
        self._last_update_offset = update_id + 1
    
    def load_middlewares(self):
        handler = self.__get_response
        
        for mw in reversed(self._middlewares):
            handler = mw(handler)
        
        self._middleware_chain = handler
    def get_response(self, message):
        if message.get('text'): message['text'] = message['text'].strip()
        response = self._middleware_chain(message)
        
        return response
    
    def __get_response(self, message):
        
        response = None
        command = self.__get_command(message)
        
        if not command: response = "Такой команды не существует"
        
        if response == None:
            try:
                response = command(message)
            except Exception as ex:
                response = "Ошибка при обработке запроса"
        
        return response
    def __get_command(self, message):
        mesg = message['text'].strip()
        command = mesg.split(' ')
        if not command or command[0] not in self._commands:
            return None
        cmd = self._commands[command[0]]
        
        return cmd
    
    def set_next_user_step(self, message, func):
        chat_id = message['chat']['id']
        NextStepMiddleware.registrate_next_step(chat_id, func)
        
    def remove_next_user_step(self, message):
        chat_id = message['chat']['id']
        NextStepMiddleware.remove_next_step(chat_id)
    
    def handle_updates(self, update_timeout = 6000, update_limit = 100):
        rqst = self.__send_request(
            'get', 
            'getUpdates',
            params={
                'timeout' : update_timeout,
                'limit' : update_limit,
                'offset' : self._last_update_offset
            }
        )
        updates = json.loads(
            rqst.content
        )
        
        for update in updates['result']:
            self.__process_update(
                update
            )
    def start_pooling(self, update_timeout = 60, update_limit = 100):
        self.load_middlewares()
        
        while True:
            self.handle_updates(update_timeout, update_limit)
    
    def message_handler(self, command):
        
        def decorator(func):
            self._commands.update(
                {command : func}
            )
            
            return func
        
        return decorator
        

        
        
            