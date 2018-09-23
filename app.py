from flask import Flask, request, abort
from datetime import datetime
import gcaltools
import json
import traceback

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, StickerSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi('UE+D0Ot1CJIhR6/QxJnWW2GakEQW6XCXBltllhhI4PxRqHOA69BkaeWNCG4nSrw5q1RnDroACfFMD/yDYfj0+yWMy5GTfXZK6jIO5kJ4X/odeATHQRVxlfDA/LMddgJA4W2wRN9ea3hs5xVOfqbMpwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('ed8de0ee82cfe03116bffbd74858569c')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    print("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        print("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            print("  %s: %s" % (m.property, m.message))
        print("\n")
    except InvalidSignatureError:
        abort(400)

    return 'OK'


def isSimilar(message, template):
	similarity = len(template)
	
	for t in template:
		if(t in message):
			similarity -= 1
	return similarity == 0
	
	
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = event.message.text
    message = message.lower()
    splitted = message.split(' ')

    # Handle messages
    if(isSimilar(splitted, ['ini', 'ada', 'apa', 'aja'])):
        res = {"status":False}
        title = ""
        if(isSimilar(splitted, ['minggu'])):
            res = gcaltools.getThisWeekEvent()
            title = "Timeline HMIF - Minggu Ini"
        elif(isSimilar(splitted, ['hari'])):
            res = gcaltools.getTodayEvent()
            title = "Timeline HMIF - Hari Ini"
        try:
            res = json.loads(res)
            if(res['status']):
                if(len(res['events']) > 0):
                    contents = []
                    for t in res['events']:
                        startdate = datetime.fromtimestamp(t["start"]).strftime('%d %b')
                        name = t["name"]
                        starttime = datetime.fromtimestamp(t["start"]).strftime('%H:%M')
                        endtime = datetime.fromtimestamp(t["end"]).strftime('%H:%M')
                        content = {
                            "type" : "box",
                            "layout" : "horizontal",
                            "contents" : [
                                {
                                    "type" : "text",
                                    "text" : startdate,
                                    "align" : "start"
                                },
                                {
                                    "type" : "box",
                                    "layout" : "vertical",
                                    "contents" : [        
                                        {
                                            "type" : "text",
                                            "text" : name,
                                            "gravity" : "top"
                                        },
                                        {
                                            "type" : "text",
                                            "text" : starttime + " - " + endtime,
                                            "gravity" : "bottom"
                                        }
                                    ]
                                }
                            ]
                        }
                        contents.append(content)
                    
                    response = {
                        "type" : "flex",
                        "altText" : title,
                        "contents" : {
                            "type" : "bubble",
                            "header" : {
                                "type" : "box",
                                "layout" : "vertical",
                                "contents" : [
                                    {
                                        "type" : "text",
                                        "text" : title
                                    }
                                ]
                            },
                            "hero" : {
                                "type" : "image",
                                "url" : "https://drive.google.com/uc?export=view&id=1tv3z9drsKaxz_9nJVhCDN-Gpoc26wB_G"
                            },
                            "body" : {
                                "type" : "box",
                                "layout" : "vertical",
                                "contents" : contents
                            }
                        }
                    }
                else:
                    response = TextSendMessage(text='Wah minggu ini belum ada event nih!')
                line_bot_api.reply_message(event.reply_token, response)
                print(str, response)
        except:
            traceback.print_exc()
        

if __name__ == "__main__":
    app.run()