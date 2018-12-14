from flask import Flask, request, abort,render_template

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import errno
import os
import tempfile
import jieba
import speech_recognition
import ffmpy

from argparse import ArgumentParser

app = Flask(__name__)
# Channel Access Token
line_bot_api = LineBotApi('c3PBJUUzHsh82aF8GGvT9TeeqAYTO8hh4dgrhTejV2BNjTkxR+7jdJ+K2HsO2PzFpl+8+39/76e5tPpEl8/CtQic3ry2RgQgldu4e4qkxaH0oPlTZmJbQ3PuWRmPj2fHINqmynxPVlqhTkLXC1jPCAdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('2f5d7e950ecd44c4a0eda0ecbc7ccb26')


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

static_tmp_path = os.path.join(os.path.dirname("."), 'static', 'tmp')

#文字訊息事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msgtxt = event.message.text
    if msgtxt == 'DemoStart':
        feedback = "你好！歡迎來到“孫仔！哩底堆？”\n接下來的問題，你可以選擇用打字或錄音回覆我喔！\n最近天氣變冷了，有沒有穿暖一點啊？"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text = feedback))
    else: 
        seg_list = jieba.lcut(msgtxt)
        print("|".join(seg_list))

        ### 語意
        flagSt = 0
        replyMsgList = [TextMessage(text='文字訊息')]
        for item in seg_list:
            if item =='冷':
                replyMsgList.append(TextMessage(text='那我們起來動一動吧！'))
                replyMsgList.append(ImageSendMessage(
                    original_content_url='https://imgur.com/27Fw9Vl.png',
                    preview_image_url='https://imgur.com/27Fw9Vl.png'
                ))
                flagSt+= 1
                break
            elif item == '分享':
                replyMsgList.append(TextMessage(text='你可以按影片旁邊的分享按鈕，分享給其他人喔！'))
                replyMsgList.append(ImageMessage(
                    original_content_url='https://i.imgur.com/aDA0hpM.gif',
                    preview_image_url='https://i.imgur.com/aDA0hpM.gif'
                ))
                flagSt+= 1
                break
        
        if flagSt == 0:
            replyMsgList.append(TextMessage(text='AI人生好難，爆肝寫程式'))
        
        line_bot_api.reply_message(event.reply_token, replyMsgList)
        


#語音訊息事件    
@handler.add(MessageEvent, message=AudioMessage)
def handle_content_message(event):
    print("收到音訊")
    ext = 'm4a'
    message_content = line_bot_api.get_message_content(event.message.id)
    
    with tempfile.NamedTemporaryFile(dir=static_tmp_path,prefix=ext + '-', delete=False) as tf:
        for chunk in message_content.iter_content():
            tf.write(chunk)
        tempfile_path = tf.name

    dist_path = tempfile_path + '.' + ext
    dist_path_wav = tempfile_path + '.' + 'wav'
    dist_name = os.path.basename(dist_path)
    os.rename(tempfile_path, dist_path)
    auFile = os.path.join('static', 'tmp', dist_name)
    auFile_wav = os.path.join('static', 'tmp', 'wav',dist_path_wav)
    
    ff = ffmpy.FFmpeg(executable='/Users/ikea/Documents/GitCodeRepo/linebot-ai-ergo/ffmpeg', inputs={auFile: None},
                      outputs={auFile_wav: None})
    ff.run()
    r = speech_recognition.Recognizer()
    with speech_recognition.AudioFile(auFile_wav) as source:
        audio = r.record(source)
    speechToTxt = r.recognize_google(audio, language='zh-tw')
    seg_list = jieba.lcut(speechToTxt)
    print(type(seg_list))
    print("|".join(seg_list))
    #msg_reply = "|".join(seg_list)
    ### 語意
    replyMsgList = [TextMessage(text='收到語音')]
    flagSt = 0
    for seg in seg_list:
        print('語音迴圈')
        if seg =='冷':
            replyMsgList.append(TextMessage(text='那我們起來動一動吧！'))
            replyMsgList.append(ImageSendMessage(
                original_content_url='https://imgur.com/27Fw9Vl.png',
                preview_image_url='https://imgur.com/27Fw9Vl.png'
            ))
            flagSt += 1
            break
        elif seg == '分享':
            replyMsgList.append(TextMessage(text='你可以按影片旁邊的分享按鈕，分享給其他人喔！'))
            replyMsgList.append(ImageMessage(
                original_content_url='https://i.imgur.com/aDA0hpM.gif',
                preview_image_url='https://i.imgur.com/aDA0hpM.gif'
            ))
            flagSt += 1
            break
        
    if flagSt == 0:
        replyMsgList.append(TextMessage(text='AI人生好難，爆肝寫程式'))
    
    line_bot_api.reply_message(event.reply_token, replyMsgList)
    

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('localhost', 5000, app)