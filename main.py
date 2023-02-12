# pip install pyTelegramBotAPI
import tgbot_db1_class
import sqlite3
import telebot
import config
import bot_token
from telebot import types

bot = telebot.TeleBot(bot_token.TOKEN)

bot_db = tgbot_db1_class.tgbot_db_class(config.DB_PATH)


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Посмотреть курсы валют")
    markup.add(btn1)
    bot.send_message(message.from_user.id,
                     "Привет!\nЯ могу рассказать тебе о курсе криптовалют.\nЕсли хочешь изменить список криптовалют, "
                     "воспользуйся командой: /help",
                     reply_markup=markup)
    user_id = message.from_user.id
    print(user_id)


@bot.message_handler(commands=['help', 'del', 'add', 'ls', 'back', 'list'])
def start(message):
    uid = str(message.from_user.id)
    if message.text == '/help':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок

        bot.send_message(message.from_user.id,
                         'Для удаления валют  воспользуйтесь функцией /del и название криптовалюты которую вы хотите '
                         'удалить\nДля добавления воспользуйтесь функцией /add и название криптовалюты\nДля просмотра '
                         'всех валют в вашем списке воспользуйтесь функцией /ls\nДля просмотра всех криптовалюты, '
                         'курсы '
                         'которых мы можем вам предоставить воспользуйтесь функцией /list',
                         reply_markup=markup)  # ответ бота
#        bot.send_message(message.from_user.id, 'Что бы вернуться обратно воспользуйтесь командой: /back',
#                         reply_markup=markup)
        user_id = message.from_user.id
        print(user_id)
    elif '/del' in message.text:
        if message.text in '/del':
            bot.send_message(message.from_user.id,
                             'После команды /del вы ещё должны ввести название криптовалюты, например: /del bitcoin',
                             parse_mode='Markdown')
        # bot.send_message(message.from_user.id, 'Какую валюту вы хотите удалить?', parse_mode='Markdown')
        else:  # message.text.split()[1] in config.:
            res = bot_db.del_coin(uid=uid, coin_id=message.text.split()[1].lower())
            bot.send_message(message.from_user.id, res, parse_mode='Markdown')
        # else: bot.send_message(message.from_user.id, f'Криптовалюты {message.text.split()[1]} нету в вашем списке
        # криптовалют', parse_mode='Markdown')
    elif '/add' in message.text:
        # bot.send_message(message.from_user.id, 'Какую валюту вы хотите добавить?', parse_mode='Markdown') if
        # message.text.split()[1] in config.COIN_LIST: bot.send_message(message.from_user.id, f'Эта криптовалюта уже
        # есть в вашем списке', parse_mode='Markdown') else: print(uid, message.text.split()[1].lower())
        res = bot_db.add_coin(uid=uid, coin_id=message.text.split()[1].lower())
        # bot.send_message(message.from_user.id, f'Вы добавили {message.text.split()[1]} в список ваших криптовалют',
        # parse_mode='Markdown')
        bot.send_message(message.from_user.id, res, parse_mode='Markdown')

    elif '/ls' in message.text:
        # bot.send_message(message.from_user.id, f'На данный момент в вашем списке криптовалют находятся: {
        # config.button_list}', parse_mode='Markdown')
        bot.send_message(message.from_user.id,
                         f'На данный момент в вашем списке криптовалют находятся:\n {bot_db.get_user_coins(uid=uid)}',
                         parse_mode='Markdown')
    elif '/list' in message.text:
        # bot.send_message(message.from_user.id, f'На данный момент в вашем списке криптовалют находятся: {
        # config.button_list}', parse_mode='Markdown')
        msg = bot_db.list_coins()
        # print(len(msg))

        bot.send_message(message.from_user.id, f'На данный момент в вашем списке криптовалют находятся:\n {msg[:3000]}',
                         parse_mode='Markdown')
    elif message.text == '/back':
        bot.send_message(message.from_user.id, 'Ща добавлю', parse_mode='Markdown')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    uid = str(message.from_user.id)
    print(message.text)
    if message.text == 'Посмотреть курсы валют':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        # for i in range(len(config.button_list)):
        #     markup.add(types.KeyboardButton(config.button_list[i]))

        button_list = bot_db.get_user_coins(uid=uid)
        for i in range(len(button_list) // 3):
            # x = []
            # for j in range(3):
            #     x.append(types.KeyboardButton(config.button_list[i*3 + j]))
            # markup.add([x])

            btn1 = types.KeyboardButton(button_list[i * 3])
            btn2 = types.KeyboardButton(button_list[i * 3 + 1])
            btn3 = types.KeyboardButton(button_list[i * 3 + 2])
            markup.add(btn1, btn2, btn3)

        if len(button_list) % 3 == 1:
            btn1 = types.KeyboardButton(button_list[len(button_list) - 1])
            markup.add(btn1)

        if len(button_list) % 3 == 2:
            btn1 = types.KeyboardButton(button_list[len(button_list) - 2])
            btn2 = types.KeyboardButton(button_list[len(button_list) - 1])
            markup.add(btn1, btn2)

        bot.send_message(message.from_user.id, 'Выберете одну из валют', reply_markup=markup)
        user_id = message.from_user.id
        print(user_id)

    else:
        if message.text.lower() in bot_db.get_user_coins(uid=uid):
            msg = bot_db.get_coin_info(uid=uid, coin=message.text.lower())
            bot.send_message(message.from_user.id, msg, parse_mode='Markdown')

    # elif message.text == 'bitcoin':
    #     msg = bot_db.get_coin_info(uid=uid, coin='bitcoin')
    #     bot.send_message(message.from_user.id, msg, parse_mode='Markdown')
    # elif message.text == 'ethereum':
    #     bot.send_message(message.from_user.id, f'Курс ETH составляет: {bot_db.get_coin_curs("ethereum")}', parse_mode='Markdown')
    # elif message.text == 'usdt':
    #     bot.send_message(message.from_user.id, f'Курс USDT составляет: {bot_db.get_coin_curs("usd-coin")}', parse_mode='Markdown')


bot.infinity_polling()
