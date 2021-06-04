import os
import sqlite3
import datetime

pathDB = os.getcwd() + '/db.sqlite3'

def getDate():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y")

def addUSerDB(config, tg_id, username, first_name, last_name, pathAvatar):
    try:
        sqlite_connection = sqlite3.connect(pathDB)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")


        sqlite_select_query = """SELECT tg_id from users_botuser where bot_name_id = ? and tg_id =?"""
        cursor.execute(sqlite_select_query, (config.bot_id, tg_id))
        records = cursor.fetchone()
        # Если в таблице нет пользователя с таким id у данного бота с bot_name_id, то добавляем нового
        if(records == None ):
            now = datetime.datetime.now()
            cDate = now.strftime("%d-%m-%Y %H:%M")

            sqlite_insert_query = """INSERT INTO users_botuser
                                    (username, first_name, last_name, tg_id, pathAvatar, bot_name_id, dateReg)
                                    VALUES (?, ?, ?, ?, ?, ?, ?);"""

            data_tuple  = (username,first_name, last_name,tg_id,pathAvatar,config.bot_id,cDate)

            count = cursor.execute(sqlite_insert_query, data_tuple)
            sqlite_connection.commit()
            print("Запись успешно вставлена ​​в таблицу users_botuser ", cursor.rowcount)
        else:
            print("Пользователь уже существует! ", cursor.rowcount)

        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")


def addMsgsDB(config):
    try:
        sqlite_connection = sqlite3.connect(pathDB)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from users_messages where bot_name_id = ? and date = ?"""
        cDate = getDate()
        cursor.execute(sqlite_select_query, (config.bot_id,cDate))
        records = cursor.fetchall()
        if(len(records) > 0 ):
            count = records[0][1] + 2
            sql_update_query = """Update users_messages set count = ? where bot_name_id = ? and date = ?"""
            cursor.execute(sql_update_query, (count, config.bot_id, cDate))
            sqlite_connection.commit()
            print("Запись успешно обновлена")
        else:
            sqlite_insert_query = """INSERT INTO users_messages
                                    (count,date, bot_name_id)
                                    VALUES (?, ?, ?);"""

            data_tuple  = (2, cDate, config.bot_id)
            count = cursor.execute(sqlite_insert_query, data_tuple)
            sqlite_connection.commit()
            print("Запись успешно вставлена ​​в таблицу users_messages ", cursor.rowcount)

        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")

def getCustomCommandDB(config):
    try:
        sqlite_connection = sqlite3.connect(pathDB)
        cursor = sqlite_connection.cursor()
        print("Подключен к SQLite")

        sqlite_select_query = """SELECT * from users_customcommand where bot_name_id = ?"""
        cursor.execute(sqlite_select_query, (config.bot_id,))
        records = cursor.fetchall()
        if(len(records) > 0 ):
            return records
        else:
            print('NONE')
            return 0
        cursor.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)
    finally:
        if sqlite_connection:
            sqlite_connection.close()
            print("Соединение с SQLite закрыто")
