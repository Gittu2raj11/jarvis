import os
import telebot
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['rajbhai'])
def start(message):
    bot.reply_to(message, "Send me your .bat file and I'll process it.")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    input_filename = message.document.file_name
    output_filename = os.path.splitext(input_filename)[0] + "_converted.txt"

    # Read original content
    content = downloaded_file.decode('utf-8', errors='ignore')

    # Regex patterns
    lecture_pattern = re.compile(
        r'set\s+"lecture_\d+=(.*?)"\s.*?N_m3u8DL-RE\s+"(https?://[^\s"]+)',
        re.DOTALL
    )
    note_pattern = re.compile(
        r'set\s+"note_\d+=(.*?)"\s.*?curl\s+-L\s+-o\s+".*?"\s+"(https?://[^\s"]+)',
        re.DOTALL
    )

    output_lines = []
    count_m3u8 = 0
    count_pdf = 0

    for match in re.finditer(
        r'(set\s+"lecture_\d+.*?N_m3u8DL-RE\s+"https?://[^\s"]+")|(set\s+"note_\d+.*?curl\s+-L\s+-o\s+".*?"\s+"https?://[^\s"]+")',
        content,
        re.DOTALL
    ):
        block = match.group(0)
        lecture_match = lecture_pattern.search(block)
        if lecture_match:
            title, url = lecture_match.groups()
            output_lines.append(f"{title.strip()} : {url.strip()}")
            count_m3u8 += 1
            continue

        note_match = note_pattern.search(block)
        if note_match:
            title, url = note_match.groups()
            output_lines.append(f"{title.strip()} : {url.strip()}")
            count_pdf += 1

    result_text = "\n".join(output_lines)
    result_text += f"\n📽 Total m3u8 links: {count_m3u8}\n📄 Total pdf links: {count_pdf}"

    bot.send_document(message.chat.id, result_text.encode('utf-8'), visible_file_name=output_filename)

bot.polling(none_stop=True)
