#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8
from threading import Thread
import requests
import datetime
import time
from googleapiclient.discovery import build
url = "https://api.telegram.org/bot749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ/"
helpcmdstr = "/help - список всех команд\n/start - начать отправку новостей"
class BotHandler:
        def __init__(self,token):
                self.token = token
                self.api_url = "https://api.telegram.org/bot{}/".format(token)
                self.meduza = ' '
                self.newsapi = {
                        'CNN':' ',
                        'BBC':' ',
                        'Lenta':' '
                        }
                self.zk = []

        def get_updates(self,offset=None,timeout=30):
                params = {'timeout:': timeout, 'offset': offset}
                response = requests.get(self.api_url+'getUpdates',params)
                return response.json()['result']
        def cmd_help(self,chat_id):
                self.send_mess(chat_id,helpcmdstr)	 

        def set_keyboard(self):
                params = {'text': '/start'}
                response = requests.get(self.api_url+'KeyboardButton',params)                       
	
        def cmd_start(self,chat_id):
                fci = open('ids.txt', 'r')
                k = 0
                l = 0
                for line in fci:
                        if(str(chat_id) != line[0:9]):
                                k+=1		
                        l+=1
                if(k == l):
                        fci.close()
                        fci = open('ids.txt', 'a')
                        fci.write(str(chat_id) + '\n')
                        self.send_mess(chat_id, "Вы подписались на отправку новостей!")
                else:
                        self.send_mess(chat_id,"Вы уже подписаны на новости")
			
		
        def run_command(self,command,chat_id):
                switch = {
                        "/help":self.cmd_help,
                        "/start":self.cmd_start,			
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
        
        def send_mess(self,chat,text):
                params = {'chat_id':chat, 'text':text, 'parse_mode':'HTML'}
                response = requests.post(self.api_url + 'sendMessage', params)
                return response

        def send_photo(self,chat,photo,capture):
                params = {'chat_id':chat,'photo':photo,'caption':capture,'parse_mode':'HTML'}
                response = requests.post(self.api_url + 'sendPhoto', params)
                return response
        
        def send_newsapi_news(self,new,url):
                service = build('translate', 'v2',developerKey='AIzaSyAWYU-85WXnlOTy1CdRH6CbRRb7wp57ImE')
                rsp = requests.get(url)
                news = rsp.json()['articles']
                z = news[0]['publishedAt']
                if(z!=self.newsapi[new]):
                        title = service.translations().list(target='ru',q=[news[0]['title']]).execute()['translations'][0]['translatedText']
                        self.newsapi[new] = z
                        fci = open('ids.txt', 'r')
                        #title = translator.translate({news[0]['content']},dest='ru')
                        #print(title)
                        for line in fci:
                                try:
                                        self.send_photo(int(line),news[0]['urlToImage'],"<pre>"+new+"</pre>\n" + "<b>"+title+"</b>\n"+"<a>"+news[0]['url']+"</a>") 
                                except:
                                        print("Скорее всего файл ids.txt пустой")
        def send_meduza_news(self):
                        rsp = requests.get(meduza)
                        news = rsp.json()['documents']
                        max1 = -1
                        z = None
                        for ko in news:
                                if(int(news[ko]['published_at']) > max1):
                                        max1 = int(news[ko]['published_at'])
                                        z = ko
                        print(max1)
                        if(self.meduza != news[z]['url']):
                                #print(self.meduza + " " + news[z]['title'])
                                self.meduza = news[z]['url']
                                fci = open('ids.txt', 'r')
                                try:
                                        print(news[self.zk]['published_at'])
                                except:
                                        print("hi")
                                self.zk = z
                                for line in fci:
                                        try:
                                                self.send_photo(int(line),"https://meduza.io/"+news[z]['image']['large_url'],"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>")
                                                #self.send_mess(int(line),"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>" )
                                        except:
                                                self.send_mess(int(line),"<pre>Meduza</pre>\n"+"<b>"+news[z]['title']+"</b>"+"\n<a>"+"https://meduza.io/"+news[z]['url']+"</a>" )

mybot = BotHandler("749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ")
meduza = "https://meduza.io/api/v3/search?chrono=news&locale=ru&page=0&per_page=24"
cnn = "https://newsapi.org/v2/everything?sources=cnn&apiKey=e055568e37874d9d865d30630bb92d7e"
bbc = "https://newsapi.org/v2/everything?sources=bbc-news&apiKey=e055568e37874d9d865d30630bb92d7e"
lenta = "https://newsapi.org/v2/everything?sources=lenta&apiKey=e055568e37874d9d865d30630bb92d7e"
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
                        time.sleep(15)

def main():
        offset = None
        mybot.set_keyboard()
        nwthread = NewsThread("News")
        nwthread.start()
        while True:
                mybot.get_updates(offset)
                last_update = mybot.last_update()
                if(last_update != -1):
                        last_id = last_update['update_id']
                        last_text = last_update['message']['text']
                        #last_name = last_update['message']['chat']['first_name']
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
                                mybot.send_mess(last_chat_id, 'Why you,fucken bitch dont sleep?!')
                        offset = last_id+1                       

if __name__ == '__main__':  
	main()
