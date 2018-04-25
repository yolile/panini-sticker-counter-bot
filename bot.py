# -*- coding: utf-8 -*-

import logging
import os
import sqlite3

from telegram.ext import Updater, CommandHandler

token = os.environ['TELEGRAM_TOKEN']
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
conn = sqlite3.connect('panini.db')
cursor = conn.cursor()
sql_create_panini_table = """ CREATE TABLE IF NOT EXISTS figuras (
                                    id integer PRIMARY KEY,
                                    numero text NOT NULL,
                                    agregada INTEGER ,
                                    repetida INTEGER 
                                ); """
cursor.execute(sql_create_panini_table)
conn.commit()

if not cursor.execute('SELECT * FROM figuras').fetchone():
    print('Insertando')
    for i in range(0, 670):
        cursor.execute("INSERT INTO figuras VALUES (?, ?, 0, 0)", (i, str(i)))
conn.commit()
conn.close()
# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def list(bot, update):
    """Send a message when the command /start is issued."""
    conn = sqlite3.connect('panini.db')
    cursor = conn.cursor()
    command = update.message.text.replace('/', '')
    if command == 'agregadas':
        agregadas = 'Figuritas agregadas: '
        total = 0
        for row in cursor.execute('SELECT * FROM figuras WHERE agregada = 1'):
            total = total + 1
            agregadas += row[1] + ","
        update.message.reply_text(agregadas+ '\n Total = %d' % total)
    if command == 'repetidas':
        agregadas = 'Figuritas repetidas: '
        total = 0
        for row in cursor.execute('SELECT * FROM figuras WHERE repetida = 1'):
            agregadas += row[1] + ","
            total += 1
        update.message.reply_text(agregadas + '\n Total = %d' % total)
    if command == 'faltantes':
        total = 0
        agregadas = 'Figuritas faltantes: '
        for row in cursor.execute('SELECT * FROM figuras WHERE agregada = 0'):
            agregadas += row[1] + ","
            total += 1
        update.message.reply_text(agregadas + '\n Total = %d' % total)

def agregar(bot, update):
    conn = sqlite3.connect('panini.db')
    cursor = conn.cursor()
    lista = update.message.text.replace('/agregar', '').replace(' ', '').split(',')
    for figu in lista:
        figu_db = cursor.execute('SELECT agregada FROM figuras WHERE numero = ?', [figu]).fetchone()
        if figu_db[0] == 1:
            cursor.execute('UPDATE figuras SET repetida = 1 WHERE numero = ?', [figu])
        else:
            cursor.execute('UPDATE figuras SET agregada = 1 WHERE numero = ?', [figu])
    conn.commit()

def quitar(bot, update):
    conn = sqlite3.connect('panini.db')
    cursor = conn.cursor()
    lista = update.message.text.replace('/quitar', '').replace(' ', '').split(',')
    for figu in lista:
        cursor.execute('UPDATE figuras SET repetida = 0 WHERE id = ?', [figu])
    conn.commit()

def consultar(bot, update):
    conn = sqlite3.connect('panini.db')
    cursor = conn.cursor()
    figura = update.message.text.replace('/consultar', '').replace(' ', '')
    figu_db = cursor.execute('SELECT agregada, repetida FROM figuras WHERE id = ?', [figura]).fetchone()
    aRet = 'Figura %s ' % figura
    if figu_db[0] == 1:
        aRet += ' agregada'
    else:
        aRet += ' faltante'
    if figu_db[1] == 1:
        aRet += ' y repetida'
    conn.commit()
    update.message.reply_text(aRet)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("agregadas", list))
    dp.add_handler(CommandHandler("repetidas", list))
    dp.add_handler(CommandHandler("faltantes", list))
    dp.add_handler(CommandHandler("agregar", agregar))
    dp.add_handler(CommandHandler("quitar", quitar))
    dp.add_handler(CommandHandler("consultar", consultar))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
