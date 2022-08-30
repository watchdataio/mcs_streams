import logging

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import CallbackContext
from telegram.ext import CallbackQueryHandler
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from models import delete_addresses
from models import get_address_by_telegram_id_address_blockchain
from models import get_addresses_by_telegram_id
from models import insert_address
from watchdata import add_filter
from watchdata import filter_info
from watchdata import get_balance
from watchdata import remove_filter

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Константы для обработчиков
MAIN, ADDRESS, BLOCKCHAIN, NEW_ADDRESS, NEW_NAME = range(5)

user_dict = {}

def get_default_keyboard():
    reply_keyboard = [['Мои адреса', 'Узнать цены', 'Написать отзыв']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    return markup_key

def check_balance(address, blockchain):
    balance = get_balance(blockchain=blockchain, address=address)
    return balance

def start(update, _):
    update.message.reply_text(
        """
Привет! Я бот, созданный в рамках совместных стримов Moscow Coding School и WachData!
Что я умею?
    1. Отслеживать трансферы по адресам в блокчейнах: Polygon, BSC, Ethereum
    2. Смотреть баланс по адресам
        """,
        reply_markup=get_default_keyboard(), )

    return MAIN


def main(update, _):
    user = update.message.from_user
    text = update.message.text
    if text == 'Мои адреса':
        addresses = get_addresses_by_telegram_id(telegram_id=user.id)
        if addresses is None:
            addresses = []

        buttons = []

        for ad in addresses:
            address_button = InlineKeyboardButton(text=f"{ad['name']}, {ad['address'][:10]} in {ad['blockchain']}",
                                                  callback_data=f"{ad['address']},{ad['blockchain']}")
            buttons.append([address_button])

        back_button = InlineKeyboardButton(text='Назад', callback_data='Назад')
        buttons.append([back_button])
        back_button = InlineKeyboardButton(text='Добавить адрес', callback_data='Добавить адрес')
        buttons.append([back_button])

        markup = InlineKeyboardMarkup(buttons)
        update.message.reply_text(
            'Ваши адреса',
            reply_markup=markup,
        )
        return ADDRESS


def address(update: Update, ctx: CallbackContext):
    user = update.callback_query.from_user
    query = update.callback_query
    answer = str(query.data)

    if answer == 'Назад':
        ctx.bot.send_message(chat_id=user.id, text='Меню', reply_markup=get_default_keyboard)
        return MAIN

    if answer == 'Добавить адрес':
        reply_keyboard = [['bsc', 'polygon', 'eth']]
        markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        ctx.bot.send_message(chat_id=user.id, text='Какой блокчейн', reply_markup=markup_key)
        return BLOCKCHAIN

    # Что делать в случае удаление адреса
    if answer.startswith('del '):
        address = answer.split()[1]
        blockchain = answer.split()[2]
        delete_addresses(user.id, address=address, blockchain=blockchain)
        filters = filter_info(blockchain=blockchain, address=address)
        if filters:
            for filt in filters:
                remove_filter(blockchain=blockchain, filter_id=filt['filter_id'])
        ctx.bot.send_message(chat_id=user.id, text='Меню', reply_markup=get_default_keyboard())
        return MAIN

    # Что делать в случае получение баланса по адресу
    if answer.startswith('bal '):
        address = answer.split()[1]
        blockchain = answer.split()[2]
        balance = check_balance(address, blockchain)
        ctx.bot.send_message(chat_id=user.id, text=f'Баланс: {balance}')
        ctx.bot.send_message(chat_id=user.id, text='Меню', reply_markup=get_default_keyboard())
        return MAIN
    # Если ни один из if не сработал, то думаем что пользователь выбрал адрес
    buttons = []
    address = answer.split(',')[0]
    blockchain = answer.split(',')[1]

    delete_data = f'del {address} {blockchain}'
    delete_button = InlineKeyboardButton(text='Удалить адрес',
                                         callback_data=str(delete_data))
    balance_data = f'bal {address} {blockchain}'
    balance_button = InlineKeyboardButton(text='Узнать баланс',
                                          callback_data=str(balance_data))
    back_button = InlineKeyboardButton(text='Назад', callback_data='Назад')
    buttons.append([delete_button])
    buttons.append([balance_button])
    buttons.append([back_button])

    res = get_address_by_telegram_id_address_blockchain(telegram_id=user.id, address=address, blockchain=blockchain)
    query.edit_message_text(text=f"{str(res)}", reply_markup=InlineKeyboardMarkup(buttons))

    return ADDRESS


def blockchain(update, _):
    global user_dict
    user = update.message.from_user
    user_dict[user.id] = dict(blockchain=update.message.text)
    update.message.reply_text(
        'Введите адрес'
    )
    return NEW_ADDRESS


def new_address(update, _):
    global user_dict
    user = update.message.from_user
    user_dict[user.id]['address'] = update.message.text

    update.message.reply_text('Введите имя для адреса')
    return NEW_NAME


def new_name(update, _):
    global user_dict
    user = update.message.from_user
    user_dict[user.id]['name'] = update.message.text
    data = user_dict[user.id]

    insert_address(telegram_id=user.id, address=data['address'],
                   blockchain=data['blockchain'], name=data['name'],
                   )
    add_filter(address=data['address'],
               blockchain=data['blockchain'])

    update.message.reply_text('Адрес добавлен')
    reply_keyboard = [['Мои адреса', 'Узнать цены', 'Написать отзыв']]
    markup_key = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    update.message.reply_text('Выбирайте', reply_markup=markup_key)
    return MAIN


if __name__ == '__main__':
    updater = Updater("YOUR_TOKEN")
    dispatcher = updater.dispatcher

    handler = ConversationHandler(  # здесь строится логика разговора
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN: [MessageHandler(Filters.regex('^(Мои адреса|Узнать цены|Написать отзыв)$'), main)],
            ADDRESS: [CallbackQueryHandler(address)],
            BLOCKCHAIN: [MessageHandler(Filters.regex('^(bsc|polygon|eth)$'), blockchain)],
            NEW_ADDRESS: [MessageHandler(Filters.text, new_address)],
            NEW_NAME: [MessageHandler(Filters.text, new_name)],
        },
        fallbacks=[],
    )

    dispatcher.add_handler(handler)

    updater.start_polling()
    updater.idle()
