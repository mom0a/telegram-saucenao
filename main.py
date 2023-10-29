# Made by @alcortazzo
# v0.5

import os
import time
import config
import logging
import traceback
from telebot import TeleBot, types

from telegram_saucenao import media_processing
from telegram_saucenao import api_requests


bot = TeleBot(config.tgBotToken)


@bot.message_handler(commands=["start"])
def cmd_start(message):
    def send_messages():
        bot.send_message(
            message.chat.id,
            'This <a href="https://github.com/alcortazzo/telegram-saucenao"><b>open source</b></a> '
            'bot provides you with an interface to use <a href="https://saucenao.com/"><b>SauceNAO</b></a>`s '
            "reverse image search engine. \n\n<b>author: @alcortazzo</b>\n"
            '<b>donate <a href="https://telegra.ph/Donate-07-22-2">here</a></b>',
            parse_mode="HTML",
            disable_web_page_preview=True,
        )

    send_messages()


@bot.message_handler(content_types=["photo"])
def msg_media(message):
    def send_results(result):
        try:
            if "urls" in result and len(result["urls"]) > 0:
                text_result = ""
                if result["name"]:
                    text_result += f"<b>{result['name']}</b>\n\n"
                if result["part"]:
                    text_result += f"<b>Part:</b> {result['part']}\n"
                if result["year"]:
                    text_result += f"<b>Year:</b> {result['year']}\n"
                if result["time"]:
                    text_result += f"<b>Time:</b> {result['time']}\n"
                if result["pic"]:
                    text_result += f"<a href=\"{result['pic']}\">Thumbnail</a>"

                markup = types.InlineKeyboardMarkup()
                buttons = []
                buttons2 = []
                for url in result["urls"]:
                    if url["url"] and url["source"] and url["similarity"]:
                        if float(url["similarity"]) < 70.00:
                            buttons2.append(
                                types.InlineKeyboardButton(
                                    text=f"{url['source']} - {url['similarity']}%", url=url["url"]
                                )
                            )
                        else:
                            buttons.append(
                                types.InlineKeyboardButton(
                                    text=f"{url['source']} - {url['similarity']}%", url=url["url"]
                                )
                            )
                if len(buttons) > 0:
                    markup.add(buttons[0])
                    # if len(buttons) > 1:
                    for bi in range(len(buttons) - 1):
                        if bi == 0 or bi > 6:
                            continue
                        if bi + 1 < len(buttons):
                            markup.row(buttons[bi], buttons[bi + 1])
                        else:
                            markup.add(buttons[bi])
                elif len(buttons2) > 0:  # Return all results when no results match more than 70%
                    markup.add(buttons2[0])
                    # if len(buttons) > 1:
                    for bi in range(len(buttons2) - 1):
                        if bi == 0 or bi > 6:
                            continue
                        if bi + 1 < len(buttons2):
                            markup.row(buttons2[bi], buttons2[bi + 1])
                        else:
                            markup.add(buttons2[bi])
                bot.send_message(
                    message.chat.id,
                    text_result,
                    parse_mode="HTML",
                    reply_markup=markup,
                    reply_to_message_id=message.id,
                )
            else:
                text_result = "No sauce found."
                bot.send_message(
                    message.chat.id,
                    text_result,
                    parse_mode=None,
                    reply_to_message_id=message.id,
                )
        except Exception as ex:
            text = traceback.format_exc()
            logger.error(text)

    file_name = str(int(time.time()))
    try:
        bot.send_chat_action(message.chat.id, "typing")

        media_file = media_processing.MediaFile(bot, message, file_name)
        media_file.download_media()
        file = media_file.prepare_file()
        results = api_requests.ApiRequest(message.chat.id, file_name)
        results = results.get_result(file)
        send_results(results)
    except Exception as ex:
        text = traceback.format_exc()
        logger.error(text)
    finally:
        delete_media(message.chat.id, file_name)


def delete_media(chat_id, filename):
    try:
        folders = os.listdir(f"./media/")
        files = []
        if str(chat_id) in folders:
            files = os.listdir(f"./media/{chat_id}/")
            if f"{filename}.jpg" in files:
                os.remove(f"./media/{chat_id}/{filename}.jpg")
    except Exception as ex:
        text = traceback.format_exc()
        logger.error(text)


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler("dev.log")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as ex:
            text = traceback.format_exc()
            logger.error(text)
            if type(ex).__name__ == "ConnectionError":
                time.sleep(3)