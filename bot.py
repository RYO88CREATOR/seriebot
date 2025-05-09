import asyncio
import logging
import os
import json
from flask import Flask, send_file
import threading
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    error,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    CallbackContext,
    MessageHandler,
    filters,
)

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Token del bot
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Link Web App
WEBAPP_LINK = "https://ryo88creator.github.io/video-vetrina/"

# Canali obbligatori
REQUIRED_CHANNELS = ["@NostraReteCanali", "@amznoes"]

# Percorso file offerte
OFFERTE_FILE = "offerte.json"

# Funzione START
async def start(update: Update, context: CallbackContext):
    user = update.effective_user
    chat_id = update.effective_chat.id

    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user.id)
            if member.status not in ["member", "administrator", "creator"]:
                await update.message.reply_text(
                    f"\U0001F512 Per accedere al catalogo devi iscriverti ai canali:\n\n"
                    f"\u27A1\uFE0F {REQUIRED_CHANNELS[0]}\n"
                    f"\u27A1\uFE0F {REQUIRED_CHANNELS[1]}"
                )
                return
        except error.TelegramError:
            await update.message.reply_text("Errore durante la verifica dell'iscrizione.")
            return

    keyboard = [[InlineKeyboardButton("\U0001F3AF Genera pulsante catalogo", callback_data="generate_catalog_button")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("\u2705 Accesso autorizzato!", reply_markup=reply_markup)

# Gestione click
async def generate_catalog_button(update: Update, context: CallbackContext):
    query = update.callback_query
    user = query.from_user

    for channel in REQUIRED_CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user.id)
            if member.status not in ["member", "administrator", "creator"]:
                await query.answer()
                await query.message.reply_text(
                    f"\U0001F512 Per accedere al catalogo devi iscriverti ai canali:\n\n"
                    f"\u27A1\uFE0F {REQUIRED_CHANNELS[0]}\n"
                    f"\u27A1\uFE0F {REQUIRED_CHANNELS[1]}"
                )
                return
        except error.TelegramError:
            await query.answer()
            await query.message.reply_text("Errore durante la verifica dell'iscrizione.")
            return

    await query.answer()

    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except error.TelegramError:
        pass

    keyboard = [[InlineKeyboardButton("\U0001F3AC Apri Catalogo Video", web_app=WebAppInfo(url=WEBAPP_LINK))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await context.bot.send_message(chat_id=query.message.chat_id, text="\U0001F39D\uFE0F Catalogo disponibile:", reply_markup=reply_markup)

    await asyncio.sleep(5)
    try:
        await context.bot.delete_message(chat_id=msg.chat_id, message_id=msg.message_id)
    except error.TelegramError:
        pass

    keyboard_back = [[InlineKeyboardButton("\U0001F3AF Genera pulsante catalogo", callback_data="generate_catalog_button")]]
    reply_markup_back = InlineKeyboardMarkup(keyboard_back)
    await context.bot.send_message(chat_id=msg.chat_id, text="\U0001F501", reply_markup=reply_markup_back)

# Funzione per salvare offerte da messaggi del canale
async def salva_offerta(update: Update, context: CallbackContext):
    message = update.effective_message
    if message.chat.username != "amznoes":
        return

    titolo = message.text or "Offerta Amazon"
    link = ""
    img_url = "https://via.placeholder.com/150"

    if message.entities:
        for entity in message.entities:
            if entity.type == "url":
                link = message.text[entity.offset:entity.offset + entity.length]

    if message.photo:
        photo = message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        img_url = file.file_path

    offerta = {"titolo": titolo, "link": link, "img": img_url}

    if os.path.exists(OFFERTE_FILE):
        with open(OFFERTE_FILE, "r", encoding="utf-8") as f:
            offerte = json.load(f)
    else:
        offerte = []

    offerte.insert(0, offerta)
    offerte = offerte[:15]  # massimo 15 offerte

    with open(OFFERTE_FILE, "w", encoding="utf-8") as f:
        json.dump(offerte, f, ensure_ascii=False, indent=2)

# Flask app per Render
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot attivo!"

@app.route("/offerte.json")
def serve_offerte():
    if os.path.exists(OFFERTE_FILE):
        return send_file(OFFERTE_FILE, mimetype="application/json")
    return "{}", 200, {"Content-Type": "application/json"}

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Avvio bot
if __name__ == '__main__':
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(generate_catalog_button, pattern="^generate_catalog_button$"))
    application.add_handler(MessageHandler(filters.ALL, salva_offerta))
    application.run_polling()
