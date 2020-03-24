import logging
import latest_number
import telegram
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)


CHOOSING, TYPING_REPLY = range(2)  

reply_keyboard = [['近期開獎號碼'],['test1']]         
                  
markup = telegram.ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)





def start(bot, update):
    update.message.reply_text(
        "Hi 我是Bingo Binog 小幫手 下面可以選擇你要輸入的預測號碼 "
        ,
        reply_markup=markup)

    return CHOOSING


def regular_choice(bot, update):
    text = update.message.text
    user_id = update.message.from_user.id
    reply = latest_number.latest_number(text, user_id)
    update.message.reply_text(reply,
                              reply_markup=markup)


    return TYPING_REPLY


def received_information(bot, update):
    user_data = update.message.from_user.id
    text = update.message.text
    reply = latest_number.latest_number(user_data, text)
    update.message.reply_text(reply,reply_markup=markup)

    return CHOOSING


