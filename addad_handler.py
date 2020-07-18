#from varname import nameof
from telegram.ext import Filters, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram import Message, Update
from enum import Enum

class State(Enum):
    def __str__(self):
        return 'addad_handler_{0}'.format(self.value)

    ROOT = 1
    CANCEL = 2
    DONE = 3
    ADD_TITLE = 4
    ADD_PRICE = 5
    ADD_DESCRIPTION = 6
    ADD_PICTURE = 7

#ROOT, CANCEL, DONE, ADD_TITLE, ADD_PRICE, ADD_DESCRIPTION, ADD_PICTURE = map(range(7))

reply_keyboardInline = [
        [InlineKeyboardButton('Заголовок', callback_data=str(State.ADD_TITLE))],
        [InlineKeyboardButton('Цена', callback_data=str(State.ADD_PRICE))],
        [InlineKeyboardButton('Описание', callback_data=str(State.ADD_DESCRIPTION))],
        [InlineKeyboardButton('Изображение', callback_data=str(State.ADD_PICTURE))],
        
        [InlineKeyboardButton('Отмена', callback_data=str(State.CANCEL)),
         InlineKeyboardButton('Готово', callback_data=str(State.DONE))],
    ]

reply_keyboard = [
        [KeyboardButton('Заголовок', callback_data=str(State.ADD_TITLE)),
        KeyboardButton('Цена', callback_data=str(State.ADD_PRICE)),
        KeyboardButton('Описание', callback_data=str(State.ADD_DESCRIPTION)),
        KeyboardButton('Изображение', callback_data=str(State.ADD_PICTURE))],
        
        [KeyboardButton('Отмена', callback_data=str(State.CANCEL)),
         KeyboardButton('Готово', callback_data=str(State.DONE))],
    ]

keyboard = reply_keyboardInline
markup = InlineKeyboardMarkup(keyboard) if keyboard == reply_keyboardInline else ReplyKeyboardMarkup(keyboard)

def addad_entry(update, context):
    print('\nADDAD ENTRY\n')
    return addad(update, context)

def addad(update, context):
    query = update.callback_query
    query.answer()
    context.bot.send_message(query.message.chat.id, "select", reply_markup=markup)
    #query.edit_message_text('Что вы хотите добавить в обьявление?', reply_markup=markup)
    return str(State.ROOT)

def addad_cancel(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nCANCEL', reply_markup=markup)
    return str(State.ROOT)

def addad_done(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nDONE', reply_markup=markup)
    return str(State.ROOT)

def addad_title(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nTITLE', reply_markup=markup)
    return str(State.ROOT)

def addad_price(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nPRICE', reply_markup=markup)
    return str(State.ROOT)

def addad_picture(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nPICTURE', reply_markup=markup)
    return str(State.ROOT)

def addad_description(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nDESCRIPTION', reply_markup=markup)
    return str(State.ROOT)

addad_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newad', addad),
            CallbackQueryHandler(addad_entry, pattern=f'^{3}$')
        ],
        states = {
            str(State.ROOT):            [CallbackQueryHandler(addad, pattern=str(State.CANCEL)),
                                        CallbackQueryHandler(addad_done, pattern=str(State.DONE)),
                                        CallbackQueryHandler(addad_title, pattern=str(State.ADD_TITLE)),
                                        CallbackQueryHandler(addad_price, pattern=str(State.ADD_PRICE)),
                                        CallbackQueryHandler(addad_picture, pattern=str(State.ADD_PICTURE)),
                                        CallbackQueryHandler(addad_description, pattern=str(State.ADD_DESCRIPTION))],
            #ADD_TITLE:       [MessageHandler(Filters.text, addad_title)],
            str(State.ADD_TITLE):       [CallbackQueryHandler(addad_title, pattern=str(State.ADD_TITLE))],
            #ADD_PRICE:       [MessageHandler(Filters.regex(r'(\d+([\.,]\d+)?)'), addad_price)],
            str(State.ADD_PRICE):       [CallbackQueryHandler(addad_price, pattern=str(State.ADD_PRICE))],
            #ADD_PICTURE:     [MessageHandler(Filters.photo, addad_picture)],
            str(State.ADD_PICTURE):     [CallbackQueryHandler(addad_picture, pattern=str(State.ADD_PICTURE))],
            #ADD_DESCRIPTION: [MessageHandler(Filters.text, addad_description)]
            str(State.ADD_DESCRIPTION): [CallbackQueryHandler(addad_description, pattern=str(State.ADD_DESCRIPTION))]
        },
        fallbacks=[CommandHandler('cancel', addad_cancel)]
    )