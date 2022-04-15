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
            # return(f"Для кабины {cabin} зарегистрировано {stroka[2]} попыток завершения этапа")


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
        open_cabin = get_open_cabin()
        # menu1 = telebot.types.InlineKeyboardMarkup()
        # menu1.add(telebot.types.InlineKeyboardButton(text='<<', callback_data='back'))
        # menu1.add(telebot.types.InlineKeyboardButton(text='Вторая кнопка', callback_data='close'))
        # menu1.add(telebot.types.InlineKeyboardButton(text='>>', callback_data='forvord'))
        # msg = bot.send_message(message.chat.id, text ='Нажми первую inline кнопку', reply_markup = menu1)

        msg = bot.send_message(message.chat.id,text=f'Зарезистрированно {len(open_cabin)} кабин')
        for i, item in enumerate(open_cabin):
            if int(i + 1) % 20 != 0:
                time.sleep(1)
            else:
                print(f'[MESS] Привышен лимит сообщений в минуту, пауза 40 сек')
                time.sleep(40)
            msg = bot.send_message(message.chat.id,
                                   text=f'Кабина: {item[0]} допроведение: {item[2]}  ({int(i + 1)})')
            print(f'[MESS] Кабина: {item[0]} допроведение: {item[2]}  ({int(i + 1)})')


@bot.message_handler(commands=['cabin_all'])
def start_message(message):
    print(f'[MESS] {message.chat.id}: {message.text}')
    if message.chat.id in id_cabin_income:
        print(f'[MESS] in work from Cabin')
        open_cabin = get_open_cabin()
        # menu1 = telebot.types.InlineKeyboardMarkup()
        # menu1.add(telebot.types.InlineKeyboardButton(text='<<', callback_data='back'))
        # menu1.add(telebot.types.InlineKeyboardButton(text='Вторая кнопка', callback_data='close'))
        # menu1.add(telebot.types.InlineKeyboardButton(text='>>', callback_data='forvord'))
        # msg = bot.send_message(message.chat.id, text ='Нажми первую inline кнопку', reply_markup = menu1)
        cabin_all = f'Зарезистрированно {len(open_cabin)} кабин\n'
        for i, item in enumerate(open_cabin):
            if int(i + 1) % 20 != 0:
                cabin_all += f'Кабина: {item[0]} допроведение: {item[2]}  ({int(i + 1)})\n'
            else:
                time.sleep(1)
                msg = bot.send_message(message.chat.id, text=cabin_all)
                cabin_all = f'Кабина: {item[0]} допроведение: {item[2]}  ({int(i + 1)})\n'

        msg = bot.send_message(message.chat.id, text=cabin_all)
        #print(f'[MESS] Для кабины {item[0]} зарегистрированно {item[2]} допроведения ({int(i + 1)})')


@bot.message_handler(commands=['cabin_txt'])
def start_message(message):
    print(f'[MESS] {message.chat.id}: {message.text}')
    if message.chat.id in id_cabin_income:
        print(f'[MESS] in work from Cabin')
        open_cabin = get_open_cabin()
        with open('cabin.txt', 'w') as filehandle:  
            for i, item in enumerate(open_cabin):
                #print(f'{item[0]}')
                filehandle.write(f'{item[0]}')  
                #print(f"{i+1} != {len(open_cabin)}")
                #print(i+1 != len(open_cabin))
                if i+1 != len(open_cabin):
                    filehandle.write('\n')    

        with open("cabin.txt", "rb") as file:
            bot.send_document(message.chat.id, file)
            #print(file)
            #print(file.name)
        cabin_all = f'Зарезистрированно {len(open_cabin)} кабин\n'
        msg = bot.send_message(message.chat.id, text=cabin_all)
        #msg = bot.send_document(message.chat.id, f, filename='f.name')


def get_open_cabin():
    con = sl.connect(db_cabin)
    cur = con.cursor()
    cur.execute("SELECT * FROM doprov WHERE status<>:status", {'status':'Завершен'})
    result = cur.fetchall()
    con.close
    return(result)

@bot.message_handler(commands=['test1'])
def start1_message(message):
    bot.send_message(message.chat.id, 'Допроведение кабины: 0000-3800.1.1 Статус: Завершен')


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
            if "Допроведение кабины:" in message.text:
                print(f'[MESS] msg in work - {message.text}')
                msg = rasbor_stroki(message.text)
                if msg != None:
                    for chat in id_cabin_send:
                        bot.send_message(chat, msg)
                try:
                    print(f'[INFO] Сообщение id={message.id} удалено')
                    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
                except:
                    print("your message deleted")
                time.sleep(1)
            else:
                print(f'[ERRO] msg not work - {message.text}')


bot.polling(none_stop=True,interval=1,timeout=30)