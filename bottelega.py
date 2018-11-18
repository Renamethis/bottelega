import requests
import datetime
url = "https://api.telegram.org/bot749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ/"
class BotHandler:
        def __init__(self,token):
                self.token = token
                self.api_url = "https://api.telegram.org/bot{}/".format(token)

        def get_updates(self,offset=None,timeout=30):
                params = {'timeout:': timeout, 'offset': offset}
                response = requests.get(self.api_url+'getUpdates',params)
                return response.json()['result']

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
                params = {'chat_id':chat, 'text':text}
                response = requests.post(self.api_url + 'sendMessage', params)
                return response

mybot = BotHandler("749293177:AAGbvrWY1-Bw0gBGUKXfVRXQZ6ix6MIV3aQ")

def main():
        offset = None
        while True:
                mybot.get_updates(offset)
                last_update = mybot.last_update()
                if(last_update != -1):
                        last_id = last_update['update_id']
                        last_text = last_update['message']['text']
                        last_name = last_update['message']['chat']['first_name']
                        last_chat_id = last_update['message']['chat']['id']
                        now = datetime.datetime.now()
                        if(6<=now.hour<12):
                                mybot.send_mess(last_chat_id, 'Good Morning!')
                        elif(12<=now.hour<17):
                                mybot.send_mess(last_chat_id, 'Good Day!')
                        elif(17<=hour<23):
                                mybot.send_mess(last_chat_id, 'Good evening!')
                        else:
                                mybot.send_mess(last_chat_id, 'Why you,fucken bitch dont sleep?!')
                        offset = last_id+1                       

if __name__ == '__main__':  
	main()
