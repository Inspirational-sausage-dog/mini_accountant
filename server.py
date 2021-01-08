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
import expenses

logging.basicConfig(level=logging.WARN)

logger = logging.getLogger(__name__)

API_TOKEN =  os.getenv("TELEGRAM_TOKEN")

class State(Enum):
    CHOOSING_COMMAND = 0
    REPLYING_CATEGORY_NAME_ADD= 1
    REPLYING_CATEGORY_NAME_DELETE= 2
    REPLYING_EXPENSE_CATEGORY_NAME = 3
    REPLYING_EXPENSE_AMMOUNT = 4

def start(update: Update, context: CallbackContext) -> int:
    """ Start of conversation, whether on bot start up or /start"""
    update.message.reply_text(
            "Hello, I'm a finance bot!\n\n"
            "List of commands:\n"
            "/add_category - add categories\n"
            "/categories - list categories\n"
            "/del_category - delete category\n"
            "/add_expense - add expense\n"
            "/expenses_today - show today's expenses\n"
            )
    return State.CHOOSING_COMMAND

def ask_add_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask name of category to create it """
    update.message.reply_text("Specify category name\n")
    return State.REPLYING_CATEGORY_NAME_ADD

def create_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and creates a category"""
    categories = Categories().get_all_categories()
    text = update.message.text

    for c in categories:
        if text  == c.name:
            update.message.reply_text("Category with this name already exists\n"
                                      "Specify a different name\n")
            return State.REPLYING_CATEGORY_NAME_ADD

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
    return State.REPLYING_CATEGORY_NAME_DELETE

def delete_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and deletes a category """
    categories = Categories().get_all_categories()
    text = update.message.text

    for c in categories:
        if text == c.name:
            Categories().del_category(c)
            expenses.delete_expenses(c)
            update.message.reply_text("Category and associated expenses were successfully deleted\n")
            return State.CHOOSING_COMMAND

    update.message.reply_text("Category you are trying to delete does not exist\n"
                              "Specify a different name\n")

    return State.REPLYING_CATEGORY_NAME_DELETE

def show_today_expenses(update: Update, context: CallbackContext) -> int:
    """ Show all expenses """
    update.message.reply_text(expenses.get_today_expenses())

    return State.CHOOSING_COMMAND

def ask_expense_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask category name of the expense """
    update.message.reply_text("In which category would you like to add an expense?\n")

    return State.REPLYING_EXPENSE_CATEGORY_NAME

def ask_expense_ammount(update: Update, context: CallbackContext) -> int:
    """ Ask expense ammount """
    context.user_data['category_name'] = update.message.text
    update.message.reply_text("What's the ammount of the expense?\n")

    return State.REPLYING_EXPENSE_AMMOUNT

def create_expense(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and creates an expence """
    category_name = context.user_data['category_name']
    ammount = update.message.text

    expenses.add_expense(category_name, ammount)

    update.message.reply_text(f"Expense has been successfully added to category {category_name}\n")

    return State.CHOOSING_COMMAND

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
                    CommandHandler('expenses_today', show_today_expenses),
                    CommandHandler('add_expense', ask_expense_category_name),
                    ],
                State.REPLYING_CATEGORY_NAME_ADD: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), create_category)
                    ],
                State.REPLYING_CATEGORY_NAME_DELETE:[
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), delete_category)
                    ],
                State.REPLYING_EXPENSE_CATEGORY_NAME: [
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), ask_expense_ammount)
                    ],
                State.REPLYING_EXPENSE_AMMOUNT:[
                    MessageHandler(Filters.text & ~(Filters.command | Filters.regex('^Done$')), create_expense)
                    ]
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
