import sys, logging, re, json
from pymongo import MongoClient
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PreCheckoutQueryHandler, CallbackQueryHandler, ConversationHandler, BaseFilter
from telegram import User, Invoice, LabeledPrice, SuccessfulPayment, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from ad_filter_table import is_match_ad, FilterNode, AD_PATTERN_TREE, AD_FILTERS, AD_FILTER_FLAGS, Logic
from config import config as cfg

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)

logger = logging.getLogger(__name__)                  

DEFAULT_BOT = 'FusionClubADMaster'
QUOTA_PRICE = 10

# Stages
MAIN_MENU, TOPUP_MENU = range(2)
# Callback data
HELP, BALANCE, TOPUP, ADDAD, BACK = range(5)

# Create the client
client = MongoClient('localhost', 27017)
filter_root = FilterNode(AD_PATTERN_TREE)
# Connect to our database
db = client['FusionClubDB']
# Fetch our series collection
users_collection = db['users']
orders_collection = db['orders']
setting_collection = db['settings']

class CustomFilter(BaseFilter):
    def filter(self, update):
        child_filters = []
        for group in get_allowed_groups(): child_filters.append(Filters.chat(group["_id"]))

        for child_f in child_filters:
            if child_f.filter(update): return True

        return False

def get_settings():
    return setting_collection.find_one({'bot_name' : cfg.get('db_bot', DEFAULT_BOT)})

def get_bot_name():
    return get_settings()["bot_name"]

def get_bot_token():
    return get_settings()["bot_token"]

def get_pay_token():
    return get_settings()["pay_token"]

def get_allowed_groups():
    return get_settings()["allowed_groups"]

def get_chat_admin(context, chat_id, find_creator=False):
    admins = context.bot.get_chat_administrators(chat_id)

    for admin in admins:
        if not find_creator:
            if admin:
                return admin

        if admin.status == 'creator':
            return admin
    
def get_user_name(user):
    return f"@{user.username}" if user.username else f"{user.first_name} {user.last_name}" if user.last_name else f"{user.first_name}"

def get_member_name(member):
    return get_user_name(member.user)


def successful_payment_callback(update, context):
    user_id = update.message.from_user.id
    quota_payload = int(update.message.successful_payment.invoice_payload)
    if users_collection.count_documents({"_id" : user_id}) == 0:
        users_collection.insert_one({"_id" : user_id, "quota" : quota_payload})
    else:
        users_collection.update_one({"_id": user_id},{'$inc': {"quota": quota_payload}})
    update.message.reply_text("Спасибо за оплату!")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def menu_callback(update, context):
    user_id = update.message.from_user.id

    if users_collection.count_documents({"_id" : user_id}) == 0:
        users_collection.insert_one({"_id" : user_id, "quota" : 0})

    keyboard = [[InlineKeyboardButton("Помощь", callback_data=str(HELP)),
                 InlineKeyboardButton("Моя квота", callback_data=str(BALANCE))],

                [InlineKeyboardButton("Пополнить", callback_data=str(TOPUP))],
                [InlineKeyboardButton("Подать обьявление", callback_data=str(ADDAD))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Fusion Club Ukraine', reply_markup=reply_markup)

    print('Command: [{}] {}'.format(update.message.from_user.username, update.message.text))
    return MAIN_MENU

def main_menu_callback(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("Помощь", callback_data=str(HELP)),
                 InlineKeyboardButton("Моя квота", callback_data=str(BALANCE))],

                [InlineKeyboardButton("Пополнить", callback_data=str(TOPUP))],
                [InlineKeyboardButton("Подать обьявление", callback_data=str(ADDAD))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text("Fusion Club Ukraine", reply_markup=reply_markup)
    return MAIN_MENU

def buy_callback(update, context):
    query = update.callback_query
    command, count_str = query.data.split('_')
    count = int(count_str)
    ok = (command == 'topup')
    print('Command: [{}]'.format("BUY : %s in chat %s" % (int(count), query.message.chat.id)))
    query.answer(ok)

    if not ok:
        return

    chat_id = query.message.chat.id
    title = 'Квота на публикацию обьявлений'
    description = 'Fusion Club Ukraine'
    payload = count_str
    token = get_pay_token()
    start_parameter = 'test-payment'
    currency = 'UAH'
    prices = [LabeledPrice("Пополнение квоты x %d" % count, count * QUOTA_PRICE * 100)]
    context.bot.send_invoice(chat_id, title, description, payload, token, start_parameter, currency, prices)

def message_handler(update, context):
    print('Message: [{}] {}'.format(update.message.from_user.username, update.message.text))

def precheckout_callback(update, context):
    query = update.pre_checkout_query
    if not query.invoice_payload.isdigit():
        query.answer(ok=False, error_message="Something went wrong...")
    else:
        query.answer(ok=True)

def help_callback(update, context):
    query = update.callback_query
    query.answer()
    message_text = "Тестовый режим!\nКарта: 4242 4242 4242 4242\nДата: любая\nCVV2: любой\nЕсли бота добавить в админы\nон будет удалять сообщения\nсо ссылками на auto.ria.com"

    query.edit_message_text(message_text, reply_markup=query.message.reply_markup)
    print('Message: [{}]'.format("HELP"))
    return MAIN_MENU

def balance_callback(update, context):
    query = update.callback_query
    query.answer()
    print('Message: [{}]'.format("BALANCE"))
    user_id = query.from_user.id
    user = users_collection.find_one({"_id" : user_id})
    query.edit_message_text(text="Ваша квота обьявлений: %d" % user['quota'], reply_markup=query.message.reply_markup)
    print("User: {}".format(user))

    return MAIN_MENU    

def end_callback(update, context):
    return 
        
def topup_callback(update, context):
    query = update.callback_query
    query.answer()
    keyboard = [[InlineKeyboardButton("1", callback_data="topup_%d" % 1),
                 InlineKeyboardButton("5", callback_data="topup_%d" % 5),
                 InlineKeyboardButton("10", callback_data="topup_%d" % 10)],

                [InlineKeyboardButton("Назад", callback_data=str(BACK))]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    query.edit_message_text(text="Выберите колличество.", reply_markup=reply_markup)
    return TOPUP_MENU

def addad_callback(update, context):
    query = update.callback_query
    query.edit_message_text(text="Я пока что нифига такого не умею!", reply_markup=query.message.reply_markup)
    return MAIN_MENU

def collect_strings(update):
    strings = []
    message_objects = []

    if update.message:
        message_objects.append(update.message)
    if update.edited_message:
        message_objects.append(update.edited_message)

    for msg in message_objects:
        if msg.text:
            strings.append(msg.text)
        if msg.caption:
            strings.append(msg.caption)

    return strings

def is_message_ad(update, context):
    strings = collect_strings(update)

    for string in strings:
        if filter_root.is_match_scheme(string):
            return True
        # if is_match_ad(string): return True

    return False

def is_message_banofbot(msg, context):
    mention = None
    if msg.text and msg.reply_to_message:
        if msg.reply_to_message.from_user.id == context.bot.get_me().id:
            if ('@' in msg.text and ('banofbot' in msg.text)):
                if ('@silent_banofbot' in msg.text):
                    mention = '@silent_banofbot'
                else:
                    mention = '@banofbot'
            elif ('voteban' in msg.text):
                mention = 'voteban'
            elif ('Voteban' in msg.text):
                mention = 'Voteban'
    return mention 

def on_ad_messsage(msg, context):
    user_id = msg.from_user.id
    user_nick = msg.from_user.username
    chat_id = msg.chat.id
    msg_id = msg.message_id

    # To not delete messabe but send warning
    ad_monitor_mode = True

    user = users_collection.find_one({"_id" : user_id})
    if (user['quota'] >= 1):
        users_collection.update_one({"_id" : user_id}, {'$inc': {"quota": -1}})
    else:
        if ad_monitor_mode:
            user_mention = "@%s" % user_nick
            reply_text = "Обнаружена реклама!\nВы получаете предупреждение!"
            context.bot.send_message(chat_id, "%s\n%s" % (user_mention, reply_text), reply_to_message_id = msg_id)
        else:
            try:
                context.bot.delete_message(chat_id, msg_id)
                user_mention = "@%s" % user_nick
                reply_text = "Обнаружена несанкционированная реклама!\nСообщение удалено!"
                context.bot.send_message(chat_id, "%s\n%s" % (user_mention, reply_text), parse_mode=None)
            except:
                user_mention = "@%s" % user_nick
                reply_text = "Обнаружена реклама!\nВы получаете предупреждение!"
                context.bot.send_message(chat_id, "%s\n%s" % (user_mention, reply_text), reply_to_message_id = msg_id)


def on_banofbot_mention(msg, banof_mention, context):
    complain_banofbot_vote = True
    user_id = msg.from_user.id
    user_nick = msg.from_user.username
    chat_id = msg.chat.id
    msg_id = msg.message_id
    sticker_fuck_you_file_id = 'CAACAgIAAx0CV_vo1QACAQteys6AittesCZ9iGkRPLCueYMWxwACGgIAAzigCtQ5vjSOsG1SGQQ'
    sticker_I_will_be_back_file_id = 'CAACAgIAAx0CV_vo1QACAUFeyvCvkCgAAWhcHR8ud-qkY0zOgggAAg8CAAM4oApaClLQrALznRkE'
    context.bot.send_sticker(chat_id, sticker_fuck_you_file_id, reply_to_message_id=msg_id)
    
    if complain_banofbot_vote:
        creator = get_chat_admin(context, chat_id, True)
        context.bot.send_message(chat_id, f"Что же, я бы этого не делал!\n{banof_mention}\nУпс, боты не могут видеть сообщения друг друга...\nНо я могу пожаловаться!", reply_to_message_id=msg_id)
        context.bot.send_message(chat_id, f"{get_member_name(creator)}\nЧто за дела?\nЯ так немогу работать!\nМеня хочет забанить: {get_user_name(msg.from_user)}", reply_to_message_id=msg_id)
    else:
        context.bot.send_message(chat_id, f"Что же, я бы этого не делал!\n{banof_mention}\nУпс, боты не могут видеть сообщения друг друга...", reply_to_message_id=msg_id)
        context.bot.send_sticker(chat_id, sticker_I_will_be_back_file_id)


def group_message(update, context):
    msg = None
    if update.message:
        msg = update.message
    elif update.edited_message:
        msg = update.edited_message
    if not msg: return

    user_id = msg.from_user.id
    user_nick = msg.from_user.username
    chat_id = msg.chat.id
    msg_id = msg.message_id

    if users_collection.count_documents({"_id" : user_id}) == 0:
        users_collection.insert_one({"_id" : user_id, "quota" : 0})

    print("---------------------------------------------------------------------------------------------------------------------------------------------\nGroup message: {}".format(update.message))

    banof_mention  = is_message_banofbot(msg, context)

    if is_message_ad(update, context):
        return on_ad_messsage(msg, context)
    elif banof_mention:
        return on_banofbot_mention(msg, banof_mention, context)



def main(argv):
    updater = Updater(get_bot_token(), use_context=True)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('menu', menu_callback, Filters.private),
                        CommandHandler('start', menu_callback, Filters.private)],
        states={
            MAIN_MENU:  [CallbackQueryHandler(help_callback, pattern='^' + str(HELP) + '$'),
                        CallbackQueryHandler(balance_callback, pattern='^' + str(BALANCE) + '$'),
                        CallbackQueryHandler(topup_callback, pattern='^' + str(TOPUP) + '$'),
                        CallbackQueryHandler(addad_callback, pattern='^' + str(ADDAD) + '$')],
            TOPUP_MENU: [CallbackQueryHandler(main_menu_callback, pattern='^' + str(BACK) + '$'),
                        CallbackQueryHandler(buy_callback, pattern=r'^topup_\d+$')]
        },
        fallbacks=[CommandHandler('menu', menu_callback, Filters.private)]
    )

    # updater.dispatcher.add_handler(CommandHandler('start', start_callback))
    # updater.dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), message_handler))

    updater.dispatcher.add_handler(conv_handler)
    # updater.dispatcher.add_handler(CommandHandler('start', group_activation_callback, Filters.group))
    # updater.dispatcher.add_handler(MessageHandler(Filters.chat(test_group) | Filters.chat(test_group2) | Filters.chat(FusionClubBotTest) | Filters.chat(FusionClubUkraine), group_message))
    updater.dispatcher.add_handler(MessageHandler(CustomFilter(), group_message))
    updater.dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    updater.dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main(sys.argv)