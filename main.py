# インポートするライブラリ
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    FollowEvent, MessageEvent, TextMessage, TextSendMessage, ImageMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, PostbackTemplateAction, MessageTemplateAction, URITemplateAction
)
import os

from io import BytesIO

from google.cloud import automl_v1beta1
from google.cloud.automl_v1beta1.proto import service_pb2

import random

# 軽量なウェブアプリケーションフレームワーク:Flask
app = Flask(__name__)


#環境変数からLINE Access Tokenを設定
LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
#環境変数からLINE Channel Secretを設定
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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

# MessageEvent
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    str_list = ['チョコの写真を送ってね。。。あっ察し。。',
    '義理チョコとは、一般には、恋愛感情を伴わない男性に対し、日頃の感謝の気持ちを込めて、またはホワイトデーの返礼を期待して、贈答するチョコレートのこと。',
    '恋だね',
    '愛、それはただ互いに見つめ合うことではなく、ふたりが同じ方向を見つめることである',
    '人間が恋に落ちるのは重力のせいではない',
    '恋に落ちると眠れなくなるでしょう。だって、ようやく現実が夢より素敵になったんだから',
    '人は、誰かから深く愛されることで力を得て、誰かを深く愛することで勇気を得る',
    '愛は約束、愛は思い出の品。一度与えられると、忘れ去られることはない。決して愛を失くしてしまわぬように',
    '恋は目で見ず、心で見るもの。だから翼をもつキューピットは盲に描かれている',
    '恋は踏み込むものじゃなく、落ちるものだ。真っ逆さまに。',
    'バレンタインのチョコの数とモテ度は関係ない。',
    'えーウソー？ウソー？今日バレンタイン？気づかなかったわー。今の今まで気づかなかったわー。',
    '「バレンタイン」とかけまして、「円周率」とときます。 そのこころは、「3.14で答えが出るでしょう」',
    '本命チョコとは、日本におけるバレンタインデーの日に女性が思いを寄せる男性に贈るチョコである。ボーイフレンドやその候補、夫等に贈られる。本命チョコは義理チョコと比べ、質が高く高価なものが選ばれる。本命チョコは、手作りされることも多い。']
    message = random.choice(str_list)

    line_bot_api.reply_message(
        event.reply_token,
        #TextSendMessage(text='「' + event.message.text + '」って何？')
        TextSendMessage(text=message)
    )

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    message_id = event.message.id
    message_content = line_bot_api.get_message_content(message_id)

    image_bin = BytesIO(message_content.content)
    image = image_bin.getvalue()
    request = get_prediction(image)
    print(request)
    score = request.payload[0].classification.score
    display_name = request.payload[0].display_name
    message = str(score*100)+'％の確率で、'
    if display_name=='honmei':
        message += '本命だね、おめでとう　'
        message += 'https://www.sugoren.com/search/%E6%9C%AC%E5%91%BD%E3%83%81%E3%83%A7%E3%82%B3'
        send_message(event, message)
    elif display_name=='giri':
        message += '義理だね　'
        message += 'これでも読みな　https://matome.naver.jp/odai/2151796984189198301'
        send_message(event, message)

def send_message(event, message):
    line_bot_api.reply_message(
        event.reply_token,
        #TextSendMessage(text='「' + event.message.text + '」って何？')
        TextSendMessage(text=message)
     )

def get_prediction(content):
    project_id = 'automl-vision-test-228914'
    model_id = 'ICN433808719521932743'
    #prediction_client = automl_v1beta1.PredictionServiceClient()
    # 環境変数にGOOGLE_APPLICATION_CREDENTIALSを設定していない場合は、以下の処理が必要
    KEY_FILE = "automl-vision-test-228914-c6c285cf0e67.json"
    prediction_client = automl_v1beta1.PredictionServiceClient.from_service_account_json(KEY_FILE)

    name = 'projects/{}/locations/us-central1/models/{}'.format(project_id, model_id)
    payload = {'image': {'image_bytes': content }}
    params = {}
    request = prediction_client.predict(name, payload, params)
    return request  # waits till request is returned


if __name__ == "__main__":
    port = int(os.getenv("PORT"))
    app.run(host="0.0.0.0", port=port)
