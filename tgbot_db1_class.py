import datetime
from datetime import timedelta
import requests
import json
import sqlite3
import config


# DB_PATH = 'tgbot_db.db'
# COIN_LIST = ['bitcoin', 'ethereum', 'tether', 'usd-coin', 'binancecoin']
# COIN_LIMIT = 6
# LOGIN_LIMIT = 5
# LOGIN_DELTA_TIME = 10  # 60
# LOGIN_BLOCK_TIME = 10  # 600


class tgbot_db_class:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path, check_same_thread=False)
        self.cur = self.con.cursor()

        self.cur.execute("CREATE TABLE if not exists users(user_id, blocked, block_time, coin_list, create_date)")
        self.cur.execute("CREATE TABLE if not exists login_log(user_id, timestamp, action)")
        self.cur.execute("CREATE TABLE if not exists coins(id, code, name, url, curs, get_date)")

        self.set_coins()

    def user_exist(self, uid):
        print(uid, type(uid))
        res = self.cur.execute("SELECT count(*) FROM users WHERE user_id='" + uid + "' ")
        data = res.fetchone()
        # print('user_exist', data)
        result = data[0]
        # print('user_exist', result)
        if result:
            return True
        else:
            return False

    def create_new_user(self, uid, default_coin_list):
        if not (self.user_exist(uid)):
            coin_list = json.dumps(default_coin_list)
            # print(default_coin_list, coin_list)
            # print(type(default_coin_list), type(coin_list))
            now = datetime.datetime.now()
            data_to_insert = [(uid, False, None, coin_list, now), ]
            self.cur.executemany("INSERT INTO users VALUES(?, ?, ?, ?, ?)", data_to_insert)
            self.con.commit()
            # print('Create new user', uid, now)
            return 'Пользователь создан'
        else:
            return 'Пользователь уже существует'

    def get_user_coins(self, uid):
        if not (self.user_exist(uid)):
            self.create_new_user(uid, config.COIN_LIST)

        res = self.cur.execute("SELECT coin_list FROM users WHERE user_id='" + uid + "' ")
        data = res.fetchone()
        # print('get_user_coins', data)
        result = json.loads(data[0])
        # print('get_user_coins', result)
        # print(type(result))
        return result

    def is_user_blocked(self, uid):
        res = self.cur.execute("SELECT blocked FROM users WHERE user_id='" + uid + "' ")
        data = res.fetchone()
        # print('user_blocked', data)
        if data == None:  # нет такого пользователя
            return None
            exit()
        result = data[0]
        # print('user_bloked', result)
        if result:
            return True
        else:
            return False

    def block_user(self, uid):
        now = datetime.datetime.now()
        self.cur.execute("UPDATE users SET blocked = ?, block_time = ?  WHERE user_id = ?", (True, str(now), uid))
        self.con.commit()

    def unblock_user(self, uid):
        self.cur.execute("UPDATE users SET blocked = ? WHERE user_id = ?", (False, uid))
        self.con.commit()

    def update_coins(self, uid, new_coin_list):
        coin_list = json.dumps(new_coin_list)
        self.cur.execute("UPDATE users SET coin_list = ? WHERE user_id = ?", (coin_list, uid))
        self.con.commit()

    def add_coin(self, uid, coin_id):
        if not (self.user_exist(uid)):
            self.create_new_user(uid, config.COIN_LIST)

        if not ((coin_id,) in self.list_coins2()):
            return f'Не могу добавить! Валюты {coin_id} не существует'
            exit()

        user_coins = self.get_user_coins(uid)

        if coin_id in user_coins:
            return f'Не могу добавить! Валюта {coin_id} уже есть в списке'
            exit()

        # print(len(user_coins), config.COIN_LIMIT)
        if len(user_coins) >= config.COIN_LIMIT:
            return 'Cлишком много валют, сначала удалеите одну'
        else:
            user_coins.insert(0, coin_id)
            self.update_coins(uid, user_coins)
            return f'Валюта {coin_id} добавлена'

    def del_coin(self, uid, coin_id):
        if not (self.user_exist(uid)):
            self.create_new_user(uid, config.COIN_LIST)

        user_coins = self.get_user_coins(uid)
        if coin_id in user_coins:
            user_coins.remove(coin_id)
            self.update_coins(uid, user_coins)
            return f'Вы удалили {coin_id}'
        else:
            return f'Монеты {coin_id} нет в вашем списке'

    def log_add(self, uid, action):
        now = datetime.datetime.now()
        data = [(uid, now, action), ]
        self.cur.executemany("INSERT INTO login_log VALUES(?, ?, ?)", data)
        self.con.commit()

    def login_count(self, uid, time):
        now = datetime.datetime.now()
        delta = timedelta(seconds=time)
        # print(f'SELECT count(*) FROM login_log WHERE timestamp > "{now-delta}"')
        res = self.cur.execute(
            f'SELECT count(*) FROM login_log WHERE timestamp > "{now - delta}" and user_id= "{uid}"')
        # print(res.fetchone())
        # print(res.fetchone()[0])
        result = res.fetchone()[0]
        return result

    def get_user_blocked_time(self, uid):
        res = self.cur.execute("SELECT block_time FROM users WHERE user_id='" + uid + "' ")
        data = res.fetchone()
        # print('get_user_coins', data)
        result = data[0]
        # print('get_user_coins', result)
        # print(type(result))
        return result

    def get_coin_info(self, uid, coin):
        if not (self.user_exist(uid)):
            print(self.create_new_user(uid, config.COIN_LIST))

        # print(self.login_count(uid, config.LOGIN_DELTA_TIME), config.LOGIN_LIMIT)

        if self.login_count(uid, config.LOGIN_DELTA_TIME) > config.LOGIN_LIMIT:
            self.block_user(uid)
            print('заблокировали!!')

        else:
            self.log_add(uid, 'get')
            return f'По моим данным стоимость {coin} составляет {self.get_coin_curs(coin)} долларов.'
            exit()

        if self.is_user_blocked(uid):
            # print('можно разблокировать?')
            now = datetime.datetime.now()
            # print(get_user_blocked_time(uid))

            unblock_time = datetime.datetime.strptime(self.get_user_blocked_time(uid),
                                                      "%Y-%m-%d %H:%M:%S.%f") + timedelta(
                seconds=config.LOGIN_DELTA_TIME)

            if now > unblock_time:
                self.unblock_user(uid)
            else:
                return f'Придйтся подожать до {unblock_time.strftime("%Y-%m-%d %H:%M:%S")}'


    def set_coins(self):
        list_url = 'https://api.coingecko.com/api/v3/coins/list'
        response = requests.get(list_url)
        json_string = json.loads(response.text)
        for i in json_string:
            # print(i)
            data = [(i['id'], i['symbol'], i['name'],
                     f'https://api.coingecko.com/api/v3/simple/price?ids={i["id"]}&vs_currencies=usd', None, None), ]
            self.cur.executemany("INSERT INTO coins VALUES(?, ?, ?, ?, ?, ?)", data)
        self.con.commit()

    def list_coins(self):
        result = ''
        res = self.cur.execute("SELECT id FROM coins")
        list1 = res.fetchall()
        list2 = []
        for i in list1:
            # print(i[0])
            list2.append(i[0])
        new_str = ', '.join(list2)
        return new_str

    def list_coins2(self):
        result = ''
        res = self.cur.execute("SELECT id FROM coins")
        list1 = res.fetchall()

        # print('list_coins2', list1)

        return list1

    def get_coin_curs(self, coin_id):
        x = 0
        res = self.cur.execute("SELECT curs, url, get_date FROM coins WHERE id='" + coin_id + "' ")
        data = res.fetchone()
        # print('get_user_coins', data)

        if data[0] is None:
            # print('Ещё не запрашивали курс')
            # url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
            # print(url)
            response = requests.get(data[1])
            json_string = json.loads(response.text)
            # print(json_string)
            # print(json_string[coin_id]['usd'])
            x = json_string[coin_id]['usd']
            now = datetime.datetime.now()
            self.cur.execute("UPDATE coins SET curs = ?, get_date = ? WHERE id = ?", (x, now, coin_id))
            self.con.commit()

        else:
            # print('Выдать курс из базы')
            # print('get_user_coins', data[0])
            x = data[0]

        return x
