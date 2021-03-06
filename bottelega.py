#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from threading import Thread
import requests
import datetime
import time
import json
from googleapiclient.discovery import build
import os
import psycopg2
from psycopg2 import sql
url = "https://api.telegram.org/bot749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ/"
helpcmdstr = "/help - список всех команд\n/start - начать отправку новостей\n/settings - настроить бота\n/stop - прекратить отправку новостей"
DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn.autocommit = True
cursor = conn.cursor()
#records = cursor.fetchall()
#print(records)
cursor.execute("SELECT * FROM users")
records = cursor.fetchall()
print(records)
class BotHandler:
        def __init__(self,token):
                self.token = token
                self.issid = -1
                self.api_url = "https://api.telegram.org/bot{}/".format(token)
                self.meduza = ' '
                self.newsapi = {
                        'CNN':' ',
                        'BBC':' ',
                        'Lenta':' '
                        }
                self.zk = []
                self.dict = {}
                self.max = 0
                self.chi = 0
                try:
                        self.service = build('translate', 'v2',developerKey='AIzaSyAWYU-85WXnlOTy1CdRH6CbRRb7wp57ImE')
                except:
                        print('Шота с инициализацией переводчика')
                
        def get_updates(self,offset=None,timeout=30):
                params = {'timeout:': timeout, 'offset': offset}
                try:
                        response = requests.get(self.api_url+'getUpdates',params)
                        return response.json()['result']
                except:
                        return None

        def cmd_settings(self, chat_id):
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (chat_id, ))
                records = cursor.fetchall()
                if(records):
                        buttons = [[{'text':"CNN", 'callback_data':0}, {'text':"BBC", "callback_data":1}, {'text':"Lenta",'callback_data':2}, {'text':"Meduza", 'callback_data':3}], [{'text':'Set up','callback_data':chat_id}]]
                        self.dict[chat_id] = ""
                        return self.send_inline_key(chat_id, "Выберите новостные порталы,новости с этих порталов будут отправляться ботом:",buttons)
                else:
                        return self.send_mess(chat_id,"Для настройки бота подпишитесь на рассылку!")
        def cmd_help(self,chat_id):
                self.send_mess(chat_id,helpcmdstr)
        def set_keyboard(self):
                params = {'text': '/start'}
                response = requests.get(self.api_url+'KeyboardButton',params)                       
        def cmd_stop(self,chat_id):
                cursor.execute("DELETE FROM users WHERE user_id = %s", (chat_id, ))
                self.send_mess(chat_id, "Вы отписались от отправки новостей!")
        def cmd_start(self,chat_id):
                cursor.execute("SELECT * FROM users WHERE user_id = %s", (chat_id, ))
                records = cursor.fetchall()
               # print(records)
                if(not records):
                        cursor.execute("INSERT INTO users(user_id, subs) VALUES(%s,%s)",(chat_id,'all'))
                        try:
                                records = cursor.fetchall()
                                print(records)
                        except:
                                print("No results")
 #                       insert = sql.SQL('INSERT INTO users (user_id, subs) VALUES ()').format(sql.SQL(',').join(map(sql.Literal, (int(chat_id),'all'))))
 #                       cursor.execute(insert)
                        self.send_mess(chat_id, "Вы подписались на отправку новостей!")
                else:
                        self.send_mess(chat_id,"Вы уже подписаны на новости")
			
		
        def run_command(self,command,chat_id):
                switch = {
                        "/help":self.cmd_help,
                        "/start":self.cmd_start,
                        "/settings":self.cmd_settings,
                        "/stop":self.cmd_stop
                }		
		#p = switch.get(command, lambda: send_mess(chat_id,"Не существует такой команды"))
                k=0
                for st in switch:
                        if(command == st):
                                switch[command](chat_id)	
                                break
                        else:
                                k+=1
                if(k == len(switch)):
                        self.send_mess(chat_id, "Не существует такой команды")
        def last_update(self):
                get_result = self.get_updates()
                if len(get_result) > 0:
                        last_update = get_result[len(get_result)-1]
                else:
                        last_update = -1
                return last_update
        
        def error(code,error):
                return "ERROR: " + code + " : " + error
        
        def send_inline_key(self, chat, text,buttons):
                inkey = {"inline_keyboard":buttons}
                rpmark = json.dumps(inkey)
                params = {"text":text, "chat_id":chat, 'reply_markup':rpmark} 
                response = requests.post(self.api_url + 'sendMEssage', params)
                return response
        
        def send_mess(self,chat,text):
                params = {'chat_id':chat, 'text':text, 'parse_mode':'HTML'}
                response = requests.post(self.api_url + 'sendMessage', params)
                return response

        def send_photo(self,chat,photo,capture):
                params = {'chat_id':chat,'photo':photo,'caption':capture,'parse_mode':'HTML'}
                response = requests.post(self.api_url + 'sendPhoto', params)
                return response
        
        def send_newsapi_news(self,new,url):
            try:
                rsp = requests.get(url)
                if(rsp.json()['status'] == 'error'):
                    print('Developer account)))))))')
                    return
                print(rsp.json())
                news = rsp.json()['articles']
                z = news[0]['publishedAt']
                if(z!=self.newsapi[new]):
                        try:
                                title = self.service.translations().list(target='ru',q=[news[0]['title']]).execute()['translations'][0]['translatedText']
                        except:
                                title = news[0]['title']
                                print('Что то с переводчиком')
                        self.newsapi[new] = z
                        cursor.execute("SELECT * FROM users")
                        records = cursor.fetchall()
                        for line in records:
                                if(line[1].find(new) != -1 or line[1] == 'all'):
                                        try:
                                                self.send_photo(int(line[0]),news[0]['urlToImage'],"<pre>"+new+"</pre>\n" + "<b>"+title+"</b>\n"+"<a>"+news[0]['url']+"</a>") 
                                        except:
                                                print("Скорее всего БД пуста")
            except:
                print("Что-то не так у " + new)
                                                
        def send_meduza_news(self):
                    try:
                        rsp = requests.get(meduza)
                        news = rsp.json()['documents']
                        z = self.zk
                        for ko in news:
                                if(int(news[ko]['published_at']) > self.max):
                                        self.max = int(news[ko]['published_at'])
                                        z = ko
                        print(self.max)
                        if(self.meduza != news[z]['url']):
                                #print(self.meduza + " " + news[z]['title'])
                                self.meduza = news[z]['url']
                                self.zk = z
                                cursor.execute("SELECT * FROM users")
                                records = cursor.fetchall()
                                for line in records:
                                        if(line[1].find('Meduza') != -1 or line[1] == 'all'):
                                                try:
                                                    self.send_photo(int(line[0]),"https://meduza.io/"+news[z]['image']['large_url'],"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>")
                                                        #self.send_mess(int(line),"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>" )
                                                except:
                                                        self.send_mess(int(line[0]),"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>" )

                    except:
                        print('Что то пошло не так у Meduza')
mybot = BotHandler("749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ")
meduza = "https://meduza.io/api/v3/search?chrono=news&locale=ru&page=0&per_page=1"
cnn = "https://newsapi.org/v2/everything?sources=cnn&apiKey=e055568e37874d9d865d30630bb92d7e"
bbc = "https://newsapi.org/v2/everything?sources=bbc-news&apiKey=e055568e37874d9d865d30630bb92d7e"
lenta = "https://newsapi.org/v2/everything?sources=lenta&apiKey=e055568e37874d9d865d30630bb92d7e"
nwarray = ['CNN', 'BBC', 'Lenta', 'Meduza']
class NewsThread(Thread):
        def __init__(self,name):
                Thread.__init__(self)
                self.name = name
        def run(self):
                while True:
                        print('checking...')
                        #Meduza.io
                        
                        mybot.send_meduza_news()
                        #CNN
                        mybot.send_newsapi_news("CNN",cnn)
                        #BBC
                        mybot.send_newsapi_news("BBC",bbc)
                        #Lenta
                        mybot.send_newsapi_news("Lenta", lenta)
                        #print(news[z]['title'])
                        time.sleep(10)

def main():
        upk = []
        offset = None
        mybot.set_keyboard()
        nwthread = NewsThread("News")
        nwthread.start()
        while True:
                mybot.get_updates(offset)
                last_update = mybot.last_update()
                #print(last_update)
                if(last_update != -1 and last_update != upk):
                        try:
                                last_id = last_update['update_id']
                                last_text = last_update['message']['text']
                                last_chat_id = last_update['message']['chat']['id']
                                now = datetime.datetime.now()
                                if(last_text[0] == '/'):
                                        mybot.run_command(last_text,last_chat_id)
                                        offset = last_id+1
                                        continue
                                if(6<=now.hour<12):
                                        mybot.send_mess(last_chat_id, 'Good Morning!')
                                elif(12<=now.hour<17):
                                        mybot.send_mess(last_chat_id, 'Good Day!')
                                elif(17<=now.hour<23):
                                        mybot.send_mess(last_chat_id, 'Good evening!')
                                else:
                                        mybot.send_mess(last_chat_id, 'Good night!')
                                offset = last_id+1
                        except:
                                chat_id = last_update['callback_query']['from']['id']
                                if(chat_id in mybot.dict):
                                        cursor.execute("SELECT * FROM users WHERE user_id = %s", (chat_id, ))
                                        records = cursor.fetchall()
                                        if(records):
                                                if(last_update['callback_query']['data'] != str(chat_id)):
                                                        if(mybot.dict[chat_id].find(nwarray[int(last_update['callback_query']['data'])]) == -1):
                                                                mybot.dict[chat_id]+=nwarray[int(last_update['callback_query']['data'])] + '\n'
                                                                mybot.send_mess(chat_id, nwarray[int(last_update['callback_query']['data'])] + " добавлена в список новостных порталов")
                                                else:
                                                        mybot.send_mess(chat_id, "Вы подписались на:\n" + mybot.dict[chat_id])
                                                        if(mybot.dict[chat_id].count('\n') == 4):
                                                                mybot.dict[chat_id] = "all"
                                                        cursor.execute("UPDATE users SET subs = %s WHERE user_id = %s", (mybot.dict[chat_id],chat_id, ))
                                                        del(mybot.dict[chat_id])
                                        else:
                                                mybot.send_mess(chat_id, "Вы не подписаны на новости!")
                                        
                        upk = last_update
        cursor.close()
        conn.close()
if __name__ == '__main__':  
	main()
