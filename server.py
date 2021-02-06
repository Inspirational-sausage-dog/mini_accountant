import os

import logging
import traceback

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
import exceptions

logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger(__name__)

API_TOKEN =  os.getenv("TELEGRAM_TOKEN")

class State(Enum):
    REPLYING_CATEGORY_NAME_CREATE = 0
    REPLYING_CATEGORY_NAME_DELETE= 1
    REPLYING_EXPENSE_INFO = 2

def start(update: Update, context: CallbackContext) -> int:
    """ Start of conversation, whether on bot start up or /start"""
    update.message.reply_text(
            "Hello, I'm mini-accountant!\n\n"
            "To add an expense use the /add_expense command.\n"
            )
    return ConversationHandler.END

def ask_create_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask name and limit of a category to create it """
    update.message.reply_text(
            "Specify the name of the category you wish to create"
            "Add a limit if you wish"
            "For Example: Transport -1000"
            )
    return State.REPLYING_CATEGORY_NAME_CREATE

def create_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and creates a category  """
    raw_message = update.message.text
    Categories().add_category(raw_message)
    update.message.reply_text("Success")
    return ConversationHandler.END

def ask_delete_category_name(update: Update, context: CallbackContext) -> int:
    """ Ask name of category to delete it """
    update.message.reply_text(
            "Specify the name of the category you wish you to delete\n"
            "Attention: Expenses associated with this category will be removed as well\n"
            )
    return State.REPLYING_CATEGORY_NAME_DELETE
    
def delete_category(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and deletes a category """
    categories = Categories().get_all_categories()
    text = update.message.text.lower()

    for c in categories:
        if text == c.name:
            Categories().del_category(c)
            expenses.delete_category(c)
            update.message.reply_text(
                    "Category and associated expenses were successfully deleted\n"
                    )
            return ConversationHandler.END

    update.message.reply_text(
            "Category you are trying to delete does not exist\n"
            "Specify a different name\n"
                              )

    return State.REPLYING_CATEGORY_NAME_DELETE

def delete_last(update: Update, context: CallbackContext) -> int:
    """ Delete last added expense """

    update.message.reply_text(expenses.delete_last())

    return ConversationHandler.END

def show_last_expenses(update: Update, context: CallbackContext) -> int:
    """ Show last 10 expenses """
    update.message.reply_text(expenses.get_expenses(expenses.Date.LAST))

    return ConversationHandler.END

def show_today_expenses(update: Update, context: CallbackContext) -> int:
    """ Show today's expenses """
    update.message.reply_text(expenses.get_expenses(expenses.Date.TODAY))

    return ConversationHandler.END

def show_month_expenses(update: Update, context: CallbackContext) -> int:
    """ Show this month's expenses """
    update.message.reply_text(expenses.get_expenses(expenses.Date.MONTH))
    return ConversationHandler.END

def ask_expense_info(update: Update, context: CallbackContext) -> int:
    """ Ask category name of the expense """
    update.message.reply_text(
            "To add an expense reply category and ammount of your expense.\n"
            "For Example: Transport -1000\n"
            "Tip: you can add multiple expenses dividing them with endline\n"
            )

    return State.REPLYING_EXPENSE_INFO

def create_expense(update: Update, context: CallbackContext) -> int:
    """ Finishes the exchange and creates an expence """
    raw_message  = update.message.text
    try:
        expense = expenses.add_expense(raw_message)
    except exceptions.NotCorrectMessageException as e:
        update.message.reply_text(str(e))
        return State.REPLYING_EXPENSE_INFO

    update.message.reply_text(
            "Expenses: \n"
            f"{raw_message} \n"
            "have been successfully added\n"
            "See latest expenses: /last\n"
            )

    return ConversationHandler.END

def main():

    """Passing bot token"""
    updater = Updater(token=API_TOKEN, use_context=True)

    dp = updater.dispatcher

    """Conversation Handler with states"""
    conv_handler = ConversationHandler(
            entry_points=[
                    CommandHandler('start', start),
                    CommandHandler('add_category', ask_create_category_name),
                    CommandHandler('del_category', ask_delete_category_name),
                    CommandHandler('del_last', delete_last),
                    CommandHandler('add_expense', ask_expense_info),
                    CommandHandler('last', show_last_expenses),
                    CommandHandler('today', show_today_expenses),
                    CommandHandler('month', show_month_expenses),
                    MessageHandler(~Filters.command, start)
                    ],
            states={
                State.REPLYING_CATEGORY_NAME_CREATE:[
                    MessageHandler(Filters.text & ~Filters.command, create_category)
                    ],
                State.REPLYING_CATEGORY_NAME_DELETE:[
                    MessageHandler(Filters.text & ~Filters.command, delete_category)
                    ],
                State.REPLYING_EXPENSE_INFO: [
                    MessageHandler(Filters.text & ~Filters.command, create_expense)
                    ]
                },
            fallbacks = [CommandHandler('cancel', start)],
            )
    dp.add_handler(conv_handler)

    #Start the bot
    updater.start_polling()

    #Run the bot until Ctrl+C
    updater.idle()

if __name__ == '__main__':
        main()
