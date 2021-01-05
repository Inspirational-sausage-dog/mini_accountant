import os

import logging

from typing import Dict, List
from enum import Enum

from telegram import ReplyKeyboardMarkup, Update, InlineKeyboardMarkup
from telegram.ext import (
        Updater,
        CommandHandler,
        MessageHandler,
        Filters,
        ConversationHandler,
        CallbackContext,
        )

from categories import Categories

logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)

API_TOKEN =  os.getenv("TELEGRAM_TOKEN")
class State(Enum):
    CHOOSING_COMMAND = 0
    REPLYING_NAME_ADD= 1
    REPLYING_NAME_DELETE= 2

class Category_mode(Enum):
    DELETE = 0
    ADD = 1

def start(update: Update, context: CallbackContext) -> int:
    """ Start of conversation, whether on bot start up or /start"""
    update.message.reply_text(
            "Hello, I'm a finance bot!\n\n"
            "List of commands:\n"
            "/add_category - add categories\n"
            "/categories - list categories\n"
            "/del_category - delete category\n"
            )
    return State.CHOOSING_COMMAND

def ask_add_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask name of category to create it """
    update.message.reply_text("Specify category name\n")
    return State.REPLYING_NAME_ADD

def create_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and creates a category"""
    categories = Categories().get_all_categories()
    text = update.message.text

    for c in categories:
        if text  == c.name:
            update.message.reply_text("Category with this name already exists\n"
                                      "Specify a different name\n")
            return State.REPLYING_NAME_ADD

    Categories().add_category(text)
    update.message.reply_text("Success\n")

    return State.CHOOSING_COMMAND

def show_categories(update: Update, context: CallbackContext) -> int:
    """ Show all categories available in database"""
    categories = Categories().get_all_categories()

    answer_message = "Categories:\n\n" +\
            ("\n".join([c.name for c in categories]))

    update.message.reply_text(answer_message)

    return State.CHOOSING_COMMAND

def ask_delete_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask name of category to delete it """
    update.message.reply_text("Specify category name\n")
    return State.REPLYING_NAME_DELETE

def delete_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and deletes a category """
    categories = Categories().get_all_categories()
    text = update.message.text

    for c in categories:
        if text == c.name:
            Categories().del_category(c)
            update.message.reply_text("Category successfully deleted\n")

    update.message.reply_text("Category you are trying to delete does not exist\n"
                              "Specify a different name\n")

    return State.REPLYING_NAME_DELETE

def main():

    """Passing bot token"""
    updater = Updater(token=API_TOKEN, use_context=True)

    dp = updater.dispatcher

    """Conversation Handler with states"""
    conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                State.CHOOSING_COMMAND: [
                    CommandHandler('add_category', ask_add_category_name),
                    CommandHandler('categories', show_categories),
                    CommandHandler('del_category', ask_delete_category_name),
                    ],
                State.REPLYING_NAME_ADD: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), create_category)
                    ],
                State.REPLYING_NAME_DELETE:[
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), delete_category)
                    ],
                },
            fallbacks = [CommandHandler('cancel', start)],
            allow_reentry = True,
            )
    dp.add_handler(conv_handler)

    #Start the bot
    updater.start_polling()

    #Run the bot until Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
