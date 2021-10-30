import os
import telebot
import sqlite3 as sl
from settings import tgToken, id_cabin_income, id_cabin_send, db_cabin
import time


bot = telebot.TeleBot(tgToken)

def couts_cabin(cabin, status):
    con = sl.connect(db_cabin)
    cur = con.cursor()
    cur.execute("SELECT * FROM doprov WHERE cabin=:cabin AND status=:status", {'cabin' : cabin, 'status':'Начат'})
    stroka = cur.fetchone() 
    if stroka != None:
        if stroka[2] >=2:
            print(f'[ERRO] Выявлено {stroka[2]} попыток завершения этапа для кабины {cabin} в статусе {status}')
            return(f"Для кабины {cabin} зарегистрировано {stroka[2]} попыток завершения этапа")


def add_upd_cabin(cabin, status):
    con = sl.connect(db_cabin)
    cur = con.cursor()
    cur.execute("SELECT * FROM doprov WHERE cabin=:cabin AND status=:status", {'cabin' : cabin, 'status':'Начат'})
    stroka = cur.fetchone() 
    if status == "Завершен":
        count = 0
    elif stroka == None:
        count = 1
    else:
        count = stroka[2] + 1
    cur.execute("INSERT OR REPLACE INTO doprov(cabin,status,count) VALUES (:cabin,:status,:count)", {'cabin' : cabin, 'status':status, 'count':count})
    con.commit()
    return(f'[INFO] Зарегистрирована кабина {cabin} в статусе {status}')

def rasbor_stroki(text):
    text = text.replace("Допроведение кабины: ","").replace(" Статус: ",",").strip().split(',')
    cabin = text[0]
    status = text[1]
    con = sl.connect(db_cabin)
    cur = con.cursor()
    cur.executescript("""CREATE TABLE IF NOT EXISTS doprov (
                    cabin TEXT PRIMARY KEY,
                    status TEXT,
                    count INTEGER)
    """)
    con.commit()
    time.sleep(1)
    print(add_upd_cabin(cabin, status))
    cout_cabin = couts_cabin(cabin,status)
    con.close
    return(cout_cabin)

@bot.message_handler(commands=['start'])
def start_message(message):
    print(f'[MESS] {message.chat.id}: {message.text}')
    if message.chat.id in id_cabin_income:
        print(f'[MESS] in work from Cabin')
        bot.send_message(message.chat.id, 'Привет!')

@bot.message_handler(commands=['cabin'])
def start_message(message):
    print(f'[MESS] {message.chat.id}: {message.text}')
    if message.chat.id in id_cabin_income:
        print(f'[MESS] in work from Cabin')
        bot.send_message(message.chat.id, 'Привет!')

@bot.message_handler(content_types=['text'])
def send_text(message):
    print(f'[MESS] {message.chat.id}: {message.text}')
    if message.chat.id in id_cabin_income:
        print(f'[MESS] in work from Cabin')
        if message.text.lower() == 'привет':
            bot.send_message(message.chat.id, 'Ещё раз привет!')
        elif message.text.lower() == 'пока':
            bot.send_message(message.chat.id, 'Пока!')
        else: 
            msg = rasbor_stroki(message.text)
            if msg != None:
                for chat in id_cabin_send:
                    bot.send_message(chat, msg)


bot.polling(none_stop=True,timeout=30)