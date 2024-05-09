import telebot
from config import *
import logging
from func import *
from database_func import *
from YaGPT import *
from creds import get_bot_token
bot = telebot.TeleBot(get_bot_token())
create_db()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="log_file.txt",
    filemode="w",
)

@bot.message_handler(commands=['start'])
def handler(message):
    user_id = message.chat.id
    bot.send_message(user_id, start)
@bot.message_handler(commands=['debug'])
def handler(message):
    if select_data(message.chat.id)[0][5] == 0:
        update_data(message.chat.id, "DEBUG", 1)
    elif select_data(message.chat.id)[0][5] == 1:
        update_data(message.chat.id, "DEBUG", 0)
@bot.message_handler(commands=['TEST'])
def handler(message):
    user_id = message.chat.id
    status, content = text_to_speech("проверка раз два три ")
    if status:
        bot.send_voice(user_id, content)
    else:
        bot.send_message(user_id, content)
    status, text = speech_to_text(content)
    if status:
        bot.send_message(user_id, text)
    else:
        bot.send_message(user_id, text)
@bot.message_handler(content_types = ['text'])
def handler(message):
    if len(datafr()) < 2 or user(message.chat.id) == True:
        user_database(message.chat.id)
        if count_tokens(message.text) < 30:
            logging.info("отправка запроса")
            text, token = ask_gpt(message.text)
            if int(token) < int(select_data(message.chat.id)[0][4]):
                logging.info("получение ответа")
                bot.send_message(message.chat.id, text)
                if select_data(message.chat.id)[0][5] == 0:
                    return None
                elif select_data(message.chat.id)[0][5] == 1:
                    with open("log_file.txt", "rb") as f:
                        bot.send_document(message.chat.id, f)
                update_data(message.chat.id, "text", int(select_data(message.chat.id)[0][4]) - int(token))
            else:
                bot.send_message(message.chat.id, "Не хватает токенов")
                logging.info("Не хватает токенов")
        else:
            bot.send_message(message.chat.id, "большой запрос")
            logging.info("большой запрос")
    else:
        bot.send_message(message.chat.id, "максимальное кол-во пользователей")
@bot.message_handler(content_types=['voice'])
def enter(message):
    if len(datafr()) < 2 or user(message.chat.id) == True:
        user_database(message.chat.id)
        user_id = message.chat.id
        stt_blocks, error = is_stt_block_limit(message.chat.id, message.voice.duration)
        if not stt_blocks:
            bot.send_message(user_id, 'Слишком длинное аудио')
            return
        file_id = message.voice.file_id  # получаем id голосового сообщения
        file_info = bot.get_file(file_id)  # получаем информацию о голосовом сообщении
        file = bot.download_file(file_info.file_path)  # скачиваем голосовое сообщение
        logging.info("речь в текст")
        status, text = speech_to_text(file)  # преобразовываем голосовое сообщение в текст
        if status:
            update_data(user_id, 'STT', select_data(user_id)[0][3] + stt_blocks)
            logging.info("отправка запроса")
            text, token = ask_gpt(text)
            if int(token) < int(select_data(message.chat.id)[0][2]):
                update_data(message.chat.id, "TTS", int(select_data(message.chat.id)[0][2]) - int(token))
                logging.info("текст в речь")
                status, content = text_to_speech(text)
                if status:
                    bot.send_voice(user_id, content)
                    logging.info("ГС получено")
                    if select_data(message.chat.id)[0][5] == 0:
                        return None
                    elif select_data(message.chat.id)[0][5] == 1:
                        with open("log_file.txt", "rb") as f:
                            bot.send_document(message.chat.id, f)
                else:
                    bot.send_message(user_id, content)
                    logging.info(content)

        else:
            bot.send_message(user_id, text)
            logging.info(text)
    else:
        bot.send_message(message.chat.id, "максимальное кол-во пользователей")
        logging.info("максимальное кол-во пользователей")

bot.polling()