import telebot
from telebot import types # для указание типов
import random
import mysql.connector
from mysql.connector import Error
import time

bot = telebot.TeleBot('5374684901:AAFvxEBxxpNOdkeuhGVklLy30Pnpuht_MKY')

def create_connection(host_name, user_name, user_password,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def delete_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database deleted successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def slovar(f):
    words = {}
    for line in f:
        x = list(map(str,line.split()))
        for word in x:
            word = word.lower()
            if word not in words:
                words[word] = 0
            words[word] += 1
    return words

def executemany_query(connection, query, val):
    cursor = connection.cursor()
    try:
        cursor.execute(query, val)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query_val(connection, query, val):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query,val)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

def add_words(connection, words, user_id):
    select_user = "SELECT user_id from user_id"
    users = execute_read_query(connection, select_user)
    USERS = set()
    for i in range(len(users)):
        USERS.add(users[i][0])
    if user_id not in USERS:
        insert_user = "INSERT INTO user_id ( user_id, bura ) VALUES ( %s, 0 )" %(user_id)
        execute_query(connection,insert_user)
        create_table = "CREATE TABLE u%s (id INT AUTO_INCREMENT, word TEXT NOT NULL, counter INT NOT NULL, PRIMARY KEY(id));" %(user_id)
        execute_query(connection,create_table)
    select_word = "SELECT word from u%s" %(user_id)
    word1 = execute_read_query(connection, select_word)
    WORD = set()
    for i in range(len(word1)):
        WORD.add(word1[i][0])
    for x in words:
        if x not in WORD:
            query =  "INSERT INTO u%s ( word, counter ) VALUES ( %s, %s )"
            val = (user_id,x,words[x])
            executemany_query(connection,query,val)
        else:
            query =  "UPDATE u%s SET counter = counter + %s WHERE word = %s"
            val = (user_id,words[x],x)
            executemany_query(connection,query,val)

@bot.message_handler(commands=['stat'])
def start_message(message):
    user_id = message.from_user.id
    select_user = "SELECT user_id from user_id"
    users = execute_read_query(connection, select_user)
    USERS = set()
    for i in range(len(users)):
        USERS.add(users[i][0])
    if user_id not in USERS:
        bot.send_message(message.chat.id, text = "Недостаточно слов для составления Вашего топа:(")
    else:
        queryy = "SELECT word,counter FROM u%s ORDER BY counter DESC" %(user_id)
        wordstat = execute_read_query(connection,queryy)
        if len(wordstat) >= 10:
            bot.send_message(message.chat.id, text = "Ваш топ 10 слов:\n"+str(wordstat[0][0])+' '+str(wordstat[0][1])+'\n'+str(wordstat[1][0])+' '+str(wordstat[1][1])+'\n'+str(wordstat[2][0])+' '+str(wordstat[2][1])+'\n'+str(wordstat[3][0])+' '+str(wordstat[3][1])+'\n'+str(wordstat[4][0])+' '+str(wordstat[4][1])+ '\n'\
                +str(wordstat[5][0])+' '+str(wordstat[5][1])+'\n'+str(wordstat[6][0])+' '+str(wordstat[6][1])+'\n'+str(wordstat[7][0])+' '+str(wordstat[7][1])+'\n'+str(wordstat[8][0])+' '+str(wordstat[8][1])+'\n'+str(wordstat[9][0])+' '+str(wordstat[9][1]))
        else:
            bot.send_message(message.chat.id, text = "Недостаточно слов для составления Вашего топа:(")

@bot.message_handler(commands=['info'])
def start_message(message):
    bot.send_message(message.chat.id, text = "Привет, я Диана. Спроси у меня повезёт? чтобы узнать повезёт ли тебе. Чтобы узнать статистику своих слов набери /stat")

@bot.message_handler(content_types=["text"])
def func(message):
    user_id = message.from_user.id
    s1 = "".join([z for d in ' '.join(a for a in message.text.split()) for x in d for z in x if z.isalnum() or z ==' ']).replace("  ", " ")
    a = list(map(str,s1.split()))
    words = slovar(a)
    add_words(connection, words, user_id)
    if message.text.strip() == 'Повезёт?':
        ans = random.randint(0,1)
        if ans == 0:
            bot.send_message(message.chat.id, text = 'Да')
        elif ans == 1:
            bot.send_message(message.chat.id, text = 'Нет')

connection = create_connection("localhost", "root", "password","telegramm_bot")

bot.polling(none_stop=True)