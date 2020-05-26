#from varname import nameof
from telegram.ext import Filters, CommandHandler, ConversationHandler, CallbackQueryHandler, MessageHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import Message, Update
ROOT, CANCEL, DONE, ADD_TITLE, ADD_PRICE, ADD_DESCRIPTION, ADD_PICTURE = range(7)

reply_keyboard = [
        [InlineKeyboardButton('Заголовок', callback_data=f'{ADD_TITLE}')],
        [InlineKeyboardButton('Цена', callback_data=f'{ADD_PRICE}')],
        [InlineKeyboardButton('Описание', callback_data=f'{ADD_DESCRIPTION}')],
        [InlineKeyboardButton('Изображение', callback_data=f'{ADD_PICTURE}')],
        
        [InlineKeyboardButton('Отмена', callback_data=f'{CANCEL}'),
         InlineKeyboardButton('Готово', callback_data=f'{DONE}')],
    ]

def addad(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text('Что вы хотите добавить в обьявление?', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_cancel(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nCANCEL', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_done(update, context):
    query = update.callback_query
    query.answer()
    update.message.edit_message_text(f'{query.message.text}\nDONE', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_title(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nTITLE', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_price(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nPRICE', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_picture(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nPICTURE', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

def addad_description(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(f'{query.message.text}\nDESCRIPTION', reply_markup=InlineKeyboardMarkup(reply_keyboard))
    return ROOT

addad_handler = ConversationHandler(
        entry_points = [
            CommandHandler('newad', addad),
            CallbackQueryHandler(addad, pattern=f'^{3}$')
        ],
        states = {
            ROOT:            [CallbackQueryHandler(addad, pattern=f'^{CANCEL}$')],
            #ADD_TITLE:       [MessageHandler(Filters.text, addad_title)],
            ADD_TITLE:       [CallbackQueryHandler(addad_title, pattern=f'^{ADD_TITLE}$')],
            #ADD_PRICE:       [MessageHandler(Filters.regex(r'(\d+([\.,]\d+)?)'), addad_price)],
            ADD_PRICE:       [CallbackQueryHandler(addad_price, pattern=f'^{ADD_PRICE}$')],
            #ADD_PICTURE:     [MessageHandler(Filters.photo, addad_picture)],
            ADD_PICTURE:     [CallbackQueryHandler(addad_picture, pattern=f'^{ADD_PICTURE}$')],
            #ADD_DESCRIPTION: [MessageHandler(Filters.text, addad_description)]
            ADD_DESCRIPTION: [CallbackQueryHandler(addad_description, pattern=f'^{ADD_DESCRIPTION}$')]
        },
        fallbacks=[CommandHandler('cancel', addad_cancel)]
    )