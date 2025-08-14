from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import re
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Get from Render environment variable

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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

    output_file = os.path.splitext(filepath)[0] + "_converted.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    return output_file, count_m3u8, count_pdf

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file_path = f"temp_{doc.file_name}"

    # Download file
    new_file = await doc.get_file()
    await new_file.download_to_drive(file_path)

    # Process
    output_file, count_m3u8, count_pdf = process_file(file_path)

    # Reply
    await update.message.reply_text(
        f"🎥 Total m3u8 links: {count_m3u8}\n📄 Total pdf links: {count_pdf}"
    )
    await update.message.reply_document(document=open(output_file, "rb"))

    # Cleanup
    os.remove(file_path)
    os.remove(output_file)

# New command /rajbhai
async def rajbhai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey! Raj Bhai is here 🚀\nSend me a .bat or .txt file and I'll extract your links."
    )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command for /rajbhai
    app.add_handler(CommandHandler("rajbhai", rajbhai))

    # Handle file uploads
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("Bot is running...")
    app.run_polling()