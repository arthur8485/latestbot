from emoji import emojize
import logging
from flask import Flask, request
import configparser
import telegram
from telegram import ReplyKeyboardMarkup
from telegram.ext import *
import requests
import latest_number
import prac
import function1
from time import sleep
import datetime


import pytz
import time

# Load Data from config.ini file
config = configparser.ConfigParser()
config.read('config.ini')
app = Flask(__name__)
bot = telegram.Bot(token=(config['TELEGRAM']['ACCESS_TOKEN']))


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)


@app.route('/hook', methods=['POST'])
def webhook_handler():
    """Set route /hook with POST method will trigger this method."""
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)

        # Update dispatcher process that handler to process this message
        dp.process_update(update)
        # GoogleSheet.sheets.logs(str(update))
    return 'ok'


def error_handler(bot, update, error):
    """Log Errors caused by Updates."""
    logger.error('Update "%s" caused error "%s"', update, error)
    update.message.reply_text('對不起主人，更多時間處理 Q_Q')


dp = Dispatcher(bot, None)


def location_hanlder(bot, update):
    # get users location
    message = update.message.location  # dicts type
    user_location = [message['longitude'], message['latitude']]
    print(user_location)
    # find the nearset lottery shop {'longitude': 121.194055, 'latitude': 25.059664}
    a = prac.nearest_shop(message['latitude'], message['longitude'])
    print(a)
    # send location

    bot.send_location(update.message.chat.id,
                      latitude=a[0], longitude=a[1],
                      reply_to_message_id=update.message.message_id
                      )
    bot.send_location(update.message.chat.id,
                      latitude=a[2], longitude=a[3],
                      reply_to_message_id=update.message.message_id
                      )
    logging.info('[location_hanlder][chat id]: %s' % update.message.chat.id)
    logging.info('[location_hanlder][reply_to_message_id]: %s' %
                 update.message.message_id)
    logging.info('[location_hanlder][location]: %s' % message)

#emoji
new = emojize(":new:", use_aliases=True)  
dart = emojize(":dart:", use_aliases=True)  
wave = emojize(":wave:", use_aliases=True)  
telephone_receiver = emojize(":telephone_receiver:", use_aliases=True)  
chart_with_upwards_trend = emojize(":chart_with_upwards_trend:", use_aliases=True)  
round_pushpin = emojize(":round_pushpin:", use_aliases=True)  

newest = new + "最新開獎"
bingo = dart +"bingo預測"
chart = chart_with_upwards_trend+' 趨勢圖'
CHOOSING, TYPING_REPLY, TYPING_CHOICE = range(3)


reply_keyboard = [
    [
        {"text": '最新開獎'},
        {'text': 'bingo預測'},
        {'text': '趨勢圖'}
    ],
    [
        # function OK !
        {'text': round_pushpin+'最近一家彩券行', 'request_location': True},
        {'text': telephone_receiver+'Get_contact', 'request_contact': True},

    ],
    [
        # ok

        {'text': wave+" 離開"}
    ]

]
markup = ReplyKeyboardMarkup(
    reply_keyboard, resize_keyboard=True, one_time_keyboard=True)


def start(bot, update):
    update.message.reply_text(
        "主人您好, 歡迎來到Bingo Bingo 小幫手\n以下會出現小鍵盤供主人方便使用 ~",

        reply_markup=markup)

    return CHOOSING


def regular_choice(bot, update):
    text = update.message.text
    s = pytz.utc.localize(datetime.time(8, 35))
    e = pytz.utc.localize(datetime.time(23, 59))
    cur = pytz.utc.localize(datetime.datetime.utcnow().time())
    warning = emojize(":warning:", use_aliases=True)
    collision = emojize(":collision:", use_aliases=True)  
    # dicts type

    if str(text) == '最新開獎':
        update.message.reply_text(warning+warning+warning+'資料爬取中..清稍後'+warning+warning+warning, reply_markup=markup)
        reply = latest_number.latest_number(bot, update)
        sleep(1)
        update.message.reply_text(reply, reply_markup=markup)
        sleep(0.5)
        update.message.reply_text("主人, 這是最新一期的號碼 "+collision+collision, reply_markup=markup)

    elif str(text) == 'bingo預測':
        clock_a = emojize(":clock830:", use_aliases=True)  
        clock_b = emojize(":clock12:", use_aliases=True)  
        
        update.message.reply_text(warning+warning+warning+'資料運算處理中, 請稍後'+warning+warning+warning, reply_markup=markup)
        if cur >= s or cur<= e:

            reply = prac.predict_number(bot, update)
            update.message.reply_text(reply, reply_markup=markup)
            sleep(0.5)
            update.message.reply_text("主人, 祝您中大獎 "+collision+collision, reply_markup=markup)
        else:
            zzz = emojize(":zzz:", use_aliases=True)
            point_right = emojize(":point_right:", use_aliases=True)
            point_left = emojize(":point_left:", use_aliases=True)
            update.message.reply_text('對不起主人'+point_right+point_left+' ，我還需要休息'+zzz+',\n我會在每天的\n早上:  8:35 '+clock_a+'        開始預測\n晚上:  23:59 '+clock_b+'      休息')

    elif str(text) == "趨勢圖":

        update.message.reply_text("趨勢圖", reply_markup=markup)

    elif str(text) == 'Get_contact':

        update.message.reply_text('sent contact', reply_markup=markup)

    return TYPING_REPLY


def done(bot, update):

    update.message.reply_text("謝謝主人的使用,期待您再度使用\n 若想再度使用請點我 /start ")
    return ConversationHandler.END


# Get the dispatcher to register handlers


# Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],

    states={
        CHOOSING: [MessageHandler(Filters.text('^(最新開獎|bingo預測)$'), regular_choice)],

        TYPING_REPLY: [MessageHandler(Filters.text, regular_choice)]
    },

    fallbacks=[MessageHandler(Filters.regex('^離開$'), done)]
)

dp.add_handler(conv_handler)
dp.add_handler(MessageHandler(Filters.location, location_hanlder))
# log all errors
dp.add_error_handler(error_handler)
dp.add_handler(CommandHandler('url', function1.getUrl))

if __name__ == "__main__":
    # Running server
    app.debug = True
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 88)))
    # https://api.telegram.org/bot960949087:AAF_bb_FdEXxH1OuJd0PL_KJLzWPEY1UIek/setWebhook?url=https://0bc8863a.ngrok.io/hook
