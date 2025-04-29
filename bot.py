import asyncio
import logging
from flask import Flask
import threading
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    error,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler,
)

# Flask app per tenere vivo il bot
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.start()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Token bot
BOT_TOKEN = "8085845485:AAGi5BcEENkGSkQg00YhHQyl3bkBXXDUO-o"

# Canali obbligatori
REQUIRED_CHANNELS = ["@NostraReteCanali", "@amznoes"]

# Canale Film 2025
FILM_2025_CHANNEL_ID = -1002451786739

# Messaggio affiliato
AFFILIATE_TEXT = ("\n\nCiao! Sostieni il progetto: considera di fare i tuoi acquisti Amazon tramite il mio link affiliato:\n"
                 "⚡ https://amzn.to/432DGwn ⚡\n"
                 "Per te il prezzo non cambia, ma a me dai una grande aiuto! Usa il link prima dei tuoi acquisti o dai un'occhiata al mio canale offerte! Grazie per il supporto!")

# Semaforo API
telegram_semaphore = asyncio.Semaphore(20)

# Dizionari messaggi utente
forwarded_message_ids = {}
main_menu_message_id = {}

# Serie TV
SERIES_TV = {
    "Adolescence": {
        "channel_id": -1002675705816,
        "seasons": {1: {"start_episode": 9, "num_episodes": 4}},
    },
    "Bondsman": {
        "channel_id": -1002604311389,
        "seasons": {1: {"start_episode": 2, "num_episodes": 8}},
    },
    "Daredevil: Rinascita": {
        "channel_id": -1002680217150,
        "seasons": {1: {"start_episode": 17, "num_episodes": 9}},
    },
    "Dark": {
        "channel_id": -1002354278272,
        "seasons": {
            1: {"start_episode": 29, "num_episodes": 8},
            2: {"start_episode": 40, "num_episodes": 8},
            3: {"start_episode": 49, "num_episodes": 8},
        },
    },
    "Fallout": {
        "channel_id": -1002436517723,
        "seasons": {1: {"start_episode": 3, "num_episodes": 8}},
    },
    "From": {
        "channel_id": -1002518123352,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 10},
            2: {"start_episode": 14, "num_episodes": 10},
            3: {"start_episode": 25, "num_episodes": 10},
        },
    },
    "Game Of Throne": {
        "channel_id": -1002513976563,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 10},
            2: {"start_episode": 14, "num_episodes": 10},
            3: {"start_episode": 25, "num_episodes": 10},
            4: {"start_episode": 36, "num_episodes": 10},
            5: {"start_episode": 47, "num_episodes": 10},
            6: {"start_episode": 58, "num_episodes": 10},
            7: {"start_episode": 69, "num_episodes": 7},
            8: {"start_episode": 77, "num_episodes": 6},
        },
    },
    "House Of The Dragon": {
        "channel_id": -1002621025753,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 10},
            2: {"start_episode": 14, "num_episodes": 8},
        },
    },
    "Last Of Us": {
        "channel_id": -1002376588088,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 9},
            2: {"start_episode": 13, "num_episodes": 2},
        },
    },
    "Lol Chi Ride è Fuori": {
        "channel_id": -1002531644367,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 6},
            2: {"start_episode": 10, "num_episodes": 6},
            3: {"start_episode": 19, "num_episodes": 6},
            4: {"start_episode": 32, "num_episodes": 6},
            5: {"start_episode": 39, "num_episodes": 6},
        },
    },
    "Lotr Gli Anelli Del Potere": {
        "channel_id": -1002560421098,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 8},
            2: {"start_episode": 12, "num_episodes": 8},
        },
    },
    "Marianne": {
        "channel_id": -1002617020563,
        "seasons": {1: {"start_episode": 3, "num_episodes": 8}},
    },
    "Mercoledì": {
        "channel_id": -1002365102959,
        "seasons": {1: {"start_episode": 3, "num_episodes": 8}},
    },
    "Shogun": {
        "channel_id": -1002415243106,
        "seasons": {1: {"start_episode": 3, "num_episodes": 10}},
    },
    "Squid Game": {
        "channel_id": -1002592764511,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 9},
            2: {"start_episode": 13, "num_episodes": 7},
        },
    },
    "Star Wars Andor": {
        "channel_id": -1002568386722,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 12},
            2: {"start_episode": 16, "num_episodes": 3},
        },
    },
    "Il Problema Dei 3 Corpi": {
        "channel_id": -1002592753657,
        "seasons": {1: {"start_episode": 3, "num_episodes": 8}},
    },
    "Tulsa King": {
        "channel_id": -1002405535389,
        "seasons": {
            1: {"start_episode": 23, "num_episodes": 9},
            2: {"start_episode": 33, "num_episodes": 10},
        },
    },
    "Vikings": {
        "channel_id": -1002535554393,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 9},
            2: {"start_episode": 13, "num_episodes": 10},
            3: {"start_episode": 24, "num_episodes": 10},
            4: {"start_episode": 35, "num_episodes": 20},
            5: {"start_episode": 56, "num_episodes": 20},
            6: {"start_episode": 77, "num_episodes": 20},
        },
    },
    "Will & Grace": {
        "channel_id": -1002499613359,
        "seasons": {
            1: {"start_episode": 2, "num_episodes": 22},
            2: {"start_episode": 24, "num_episodes": 24},
            3: {"start_episode": 48, "num_episodes": 25},
            4: {"start_episode": 73, "num_episodes": 27},
            5: {"start_episode": 100, "num_episodes": 24},
            6: {"start_episode": 124, "num_episodes": 24},
            7: {"start_episode": 148, "num_episodes": 24},
            8: {"start_episode": 172, "num_episodes": 23},
        },
    },
}

ANIMATION = {
    "Castlevania": {
        "channel_id": -1002604188008,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 4},
            2: {"start_episode": 8, "num_episodes": 8},
            3: {"start_episode": 17, "num_episodes": 10},
            4: {"start_episode": 28, "num_episodes": 10},
        },
    },
    "Castlevania Nocturne": {
        "channel_id": -1002630249164,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 8},
            2: {"start_episode": 12, "num_episodes": 8},
        },
    },
    "Dandadan": {
        "channel_id": -1002551341475,
        "seasons": {1: {"start_episode": 3, "num_episodes": 12}},
    },
    "Devil May Cry": {
        "channel_id": -1002621270196,
        "seasons": {1: {"start_episode": 2, "num_episodes": 8}},
    },
    "Hazbin Hotel": {
        "channel_id": -1002560801602,
        "seasons": {1: {"start_episode": 3, "num_episodes": 8}},
    },
    "I Simpson": {
        "channel_id": -1002558310523,
        "seasons": {
            1: {"start_episode": 3, "num_episodes": 13},
            2: {"start_episode": 17, "num_episodes": 22},
            3: {"start_episode": 40, "num_episodes": 24},
            4: {"start_episode": 65, "num_episodes": 22},
            5: {"start_episode": 88, "num_episodes": 22},
            6: {"start_episode": 111, "num_episodes": 25},
            7: {"start_episode": 137, "num_episodes": 25},
            8: {"start_episode": 163, "num_episodes": 25},
            9: {"start_episode": 189, "num_episodes": 25},
            10: {"start_episode": 215, "num_episodes": 23},
            11: {"start_episode": 239, "num_episodes": 20},
        },
    },
    "Ranma": {
        "channel_id": -1002304997557,
        "seasons": {1: {"start_episode": 3, "num_episodes": 12}},
    },
    "Sakamoto Days": {
        "channel_id": -1002666782757,
        "seasons": {1: {"start_episode": 3, "num_episodes": 11}},
    },
    "Solo Leveling": {
        "channel_id": -1002547983685,
        "seasons": {
            1: {"start_episode": 2, "num_episodes": 12},
            2: {"start_episode": 26, "num_episodes": 12},
        },
    },
    "Tekkaman": {
        "channel_id": -1002697417639,
        "seasons": {1: {"start_episode": 3, "num_episodes": 25}},
    },
}

# (blocchi SERIES_TV e ANIMATION già presenti sopra)

# Funzione per aggiungere il pulsante "Torna all'inizio"
def add_back_to_main_button():
    return [[InlineKeyboardButton("⬅️ Torna all'inizio", callback_data="main_menu")]]

# Funzione per decodificare il nome della serie dalla callback_data
def decode_series_name(encoded_name: str) -> str:
    series_names = list(SERIES_TV.keys()) + list(ANIMATION.keys())
    for name in series_names:
        if encoded_name == name.lower().replace(" ", "_"):
            return name
    return encoded_name.replace("_", " ").title()

# Funzione per mostrare il menu principale
def build_main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(" Film 2025", callback_data="open_film")],
        [InlineKeyboardButton(" Serie TV", callback_data="open_serie_tv")],
        [InlineKeyboardButton("️ Animazione", callback_data="open_animazione")],
    ])

async def show_main_menu(user_id: int, context: CallbackContext, message_id: int = None):
    menu_text = (
        "⭐️ Clicca https://temu.to/k/en0oscwfxky"
        "per richiedere subito il tuo pacchetto buoni di 100€!"
        "Un'altra sorpresa per te! Fai clic su https://temu.to/k/er7ic7cdxyz per guadagnare insieme a me🤝!"
        "Menu Principale:"
    )
    reply_markup = build_main_menu()
    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=menu_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        except error.BadRequest:
            sent_message = await context.bot.send_message(
                chat_id=user_id,
                text=menu_text,
                reply_markup=reply_markup,
                disable_web_page_preview=False
            )
            main_menu_message_id[user_id] = sent_message.message_id
    else:
        sent_message = await context.bot.send_message(
            chat_id=user_id,
            text=menu_text,
            reply_markup=reply_markup,
            disable_web_page_preview=False
        )
        main_menu_message_id[user_id] = sent_message.message_id

# Funzione per mostrare il menu delle stagioni
def get_seasons_keyboard(series_name: str, is_animation: bool = False):
    seasons = SERIES_TV[series_name]["seasons"] if not is_animation else ANIMATION[series_name]["seasons"]
    buttons = [
        [InlineKeyboardButton(
            f"Stagione {season}",
            callback_data=f"show_episodes|{'animation' if is_animation else 'series'}|{series_name}|{season}"
        )] for season in seasons
    ]
    buttons.extend(add_back_to_main_button())
    return InlineKeyboardMarkup(buttons)

# Funzione per mostrare il menu degli episodi
def get_episodes_keyboard(series_name: str, season: int, is_animation: bool = False):
    season_data = SERIES_TV[series_name]["seasons"][season] if not is_animation else ANIMATION[series_name]["seasons"][season]
    episode_buttons = [
        InlineKeyboardButton(
            f"Episodio {ep}",
            callback_data=f"forward|{'animation' if is_animation else 'series'}|{series_name.lower().replace(' ', '_')}|{season}|{ep}"
        ) for ep in range(1, season_data["num_episodes"] + 1)
    ]
    buttons = [episode_buttons[i:i+2] for i in range(0, len(episode_buttons), 2)]
    buttons.extend(add_back_to_main_button())
    return InlineKeyboardMarkup(buttons)

# Funzione callback handler
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if "|" in query.data:
        data = query.data.split("|")
    else:
        data = query.data.split("_")

    if data[0] == "open":
        if data[1] == "series":
            series_name = decode_series_name(data[2])
            await context.bot.send_message(user_id, f"Seleziona la stagione di {series_name}:", reply_markup=get_seasons_keyboard(series_name))
        elif data[1] == "animation":
            series_name = decode_series_name(data[2])
            await context.bot.send_message(user_id, f"Seleziona la stagione di {series_name}:", reply_markup=get_seasons_keyboard(series_name, is_animation=True))

    elif data[0] == "show_episodes":
        content_type = data[1]
        series_name = decode_series_name(data[2])
        season = int(data[3])
        await context.bot.send_message(user_id, f"Seleziona l'episodio della stagione {season} di {series_name}:", reply_markup=get_episodes_keyboard(series_name, season, is_animation=(content_type == "animation")))

    elif data[0] == "forward":
        content_type = data[1]
        series_name = decode_series_name(data[2])
        season = int(data[3])
        episode = int(data[4])
        if content_type == "series":
            season_data = SERIES_TV[series_name]["seasons"][season]
            channel_id = SERIES_TV[series_name]["channel_id"]
        else:
            season_data = ANIMATION[series_name]["seasons"][season]
            channel_id = ANIMATION[series_name]["channel_id"]
        message_id = season_data["start_episode"] + episode - 1
        await forward_episode(update, context, channel_id, message_id, f"Episodio {episode} della stagione {season} di {series_name}")

    elif data[0] == "main":
        await show_main_menu(user_id, context, message_id=main_menu_message_id.get(user_id))

# Funzione per eliminare messaggio inoltrato
async def try_delete_forwarded_message(user_id: int, context: CallbackContext):
    if user_id in forwarded_message_ids:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=forwarded_message_ids[user_id])
            del forwarded_message_ids[user_id]
        except:
            pass

# Funzione per controllare iscrizione e inviare richiesta
async def send_subscription_message(user_id: int, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton("Canale 1", url=f"https://t.me/{REQUIRED_CHANNELS[0][1:]}")],
        [InlineKeyboardButton("Canale 2", url=f"https://t.me/{REQUIRED_CHANNELS[1][1:]}")],
        [InlineKeyboardButton("✅ Ho completato l'iscrizione", callback_data="check_subscription")],
    ]
    await context.bot.send_message(user_id, "Devi iscriverti ai canali per accedere!", reply_markup=InlineKeyboardMarkup(buttons))

# Avvio del bot
async def start(update: Update, context: CallbackContext):
    user_id = update.effective_chat.id
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
    else:
        await show_main_menu(user_id, context)

async def check_subscription(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if not await is_user_subscribed(user_id, context):
        try:
            await query.message.delete()
        except:
            pass
        await send_subscription_message(user_id, context)
    else:
        await show_main_menu(user_id, context, message_id=query.message.message_id)
    await try_delete_forwarded_message(user_id, context)

# Funzione per accedere a Film 2025
async def open_film(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Errore durante l'eliminazione del messaggio in open_film: {e}")
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return
    link = await generate_invite_link(FILM_2025_CHANNEL_ID, context)
    if link:
        buttons = [[InlineKeyboardButton("Accedi a Film 2025", url=link)]]
        buttons.extend(add_back_to_main_button())
        await context.bot.send_message(user_id, "Ecco il canale:", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        buttons = add_back_to_main_button()
        await context.bot.send_message(user_id, "⚠️ Errore nel generare il link per Film 2025", reply_markup=InlineKeyboardMarkup(buttons))

# Funzioni menu Serie TV e Animazione
async def open_serie_tv(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except:
        pass
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return
    buttons = [[InlineKeyboardButton(series, callback_data=f"open_series_{series.lower().replace(' ', '_')}")] for series in sorted(SERIES_TV.keys())]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(user_id, "Seleziona una serie TV:", reply_markup=InlineKeyboardMarkup(buttons))

async def open_animazione(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except:
        pass
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return
    buttons = [[InlineKeyboardButton(serie, callback_data=f"open_animation_{serie.lower().replace(' ', '_')}")] for serie in sorted(ANIMATION.keys())]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(user_id, "Seleziona un'animazione:", reply_markup=InlineKeyboardMarkup(buttons))

# Funzione main()
def main():
    print("Bot in esecuzione...")
    keep_alive()
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(open_film, pattern="open_film"))
    application.add_handler(CallbackQueryHandler(open_serie_tv, pattern="open_serie_tv"))
    application.add_handler(CallbackQueryHandler(open_animazione, pattern="open_animazione"))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="main_menu"))

    application.run_polling()

if __name__ == "__main__":
    main()

# Funzione per verificare iscrizione
async def is_user_subscribed(user_id: int, context: CallbackContext) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except:
            return False
    return True
async def forward_episode(update: Update, context: CallbackContext, channel_id: int, message_id: int, episode_title: str):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except:
        pass
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return
    async with telegram_semaphore:
        try:
            sent_message = await context.bot.forward_message(
                chat_id=user_id,
                from_chat_id=channel_id,
                message_id=message_id,
                protect_content=True,
            )
            forwarded_message_ids[user_id] = sent_message.message_id

            testo = f"{episode_title}{AFFILIATE_TEXT}"
            buttons = [[InlineKeyboardButton("⬅️ Torna all'inizio", callback_data="main_menu")]]
            await context.bot.send_message(user_id, text=testo, reply_markup=InlineKeyboardMarkup(buttons))

        except error.ChatNotFound:
            await context.bot.send_message(
                user_id,
                "⚠️ Errore nell'inoltro dell'episodio: Chat non trovata.",
                reply_markup=InlineKeyboardMarkup(add_back_to_main_button()),
            )
        except error.BadRequest:
            await context.bot.send_message(
                user_id,
                "⚠️ Errore nell'inoltro dell'episodio: Messaggio non trovato nel canale.",
                reply_markup=InlineKeyboardMarkup(add_back_to_main_button()),
            )
        except Exception as e:
            await context.bot.send_message(user_id, f"⚠️ Errore nell'inoltro dell'episodio: {e}")
            logger.error(f"Errore nell'inoltro episodio: {e}")
