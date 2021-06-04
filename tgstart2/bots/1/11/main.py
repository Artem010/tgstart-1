import sys,os
sys.path.insert(0, os.getcwd() + '/tgstart2/bots/')
import config,telebot,dbAll


bot = telebot.TeleBot(config.token)

records = dbAll.getCustomCommandDB(config);

# print(records)

keyboard1 = telebot.types.ReplyKeyboardMarkup(True,True)
hideBoard = telebot.types.ReplyKeyboardRemove()
# keyboardDB = ['fg','gfd']

print('records: '+str(records))
if(records != 0):
    i = 0

    while i < len(records):
        try:
            btn1 = records[i][1]
        except Exception as e:
            btn1 = ''
        try:
            btn2 = records[i+1][1]
        except Exception as e:
            btn2 = ''
        try:
            btn3 = records[i+2][1]
        except Exception as e:
            btn3 = ''

        keyboard1.row(btn1,btn2,btn3)
        i+=3
else:
    keyboard1.add('')

@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    user_profile = bot.get_user_profile_photos(message.from_user.id);
    if(user_profile.total_count > 0):
        file_path = (bot.get_file(user_profile.photos[0][0].file_id)).file_path;
    else:
        file_path = "None"

    dbAll.addUSerDB(config, str(message.chat.id), str(message.chat.username),str(message.chat.first_name),str(message.chat.last_name), file_path);
    bot.send_message(message.chat.id, 'User saved')

@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    i=0;
    if(records != 0):
        for r in records:
            if(message.text==r[1]):
                i=1;
                bot.send_message(message.chat.id, text=r[2], reply_markup=keyboard1)
        if i == 0:
            bot.send_message(message.chat.id, message.text, reply_markup = keyboard1)
    else:
        bot.send_message(message.chat.id, message.text, reply_markup=hideBoard)



    dbAll.addMsgsDB(config)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=1)
