import asyncio
import logging
from flask import Flask
import threading
import os

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

# Configurazione del logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

# Token del bot (DA SOSTITUIRE CON IL TUO)
BOT_TOKEN = "8085845485:AAGi5BcEENkGSkQg00YhHQyl3bkBXXDUO-o"

# Canali obbligatori
REQUIRED_CHANNELS = ["@NostraReteCanali", "@amznoes"]

# ID del canale Film 2025 (DA SOSTITUIRE CON IL TUO)
FILM_2025_CHANNEL_ID = -1002451786739

# Dizionari per gestire serie TV e animazione (ordinati alfabeticamente)
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
        "seasons": {1: {"start_episode": 3,
"num_episodes": 25},
        },
    },
}

# Dizionario per memorizzare l'ID del messaggio inoltrato per ogni utente
forwarded_message_ids = {}
main_menu_message_id = {}

# Semaphor per limitare le richieste all'API di Telegram
telegram_semaphore = asyncio.Semaphore(20)

# Funzioni di supporto
# Funzione per inviare il messaggio con i canali da seguire
async def send_subscription_message(user_id: int, context: CallbackContext):
    buttons = [
        [
            InlineKeyboardButton(
                "Canale 1", url=f"https://t.me/{REQUIRED_CHANNELS[0][1:]}"
            )
        ],
        [
            InlineKeyboardButton(
                "Canale 2", url=f"https://t.me/{REQUIRED_CHANNELS[1][1:]}"
            )
        ],
        [
            InlineKeyboardButton(
                "✅ Ho completato l'iscrizione", callback_data="check_subscription"
            )
        ],
    ]
    await context.bot.send_message(
        user_id, "Devi iscriverti ai canali per accedere!", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per verificare se l'utente è iscritto ai canali obbligatori
async def is_user_subscribed(user_id: int, context: CallbackContext) -> bool:
    for channel in REQUIRED_CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if chat_member.status in ["left", "kicked"]:
                return False
        except error.BadRequest:
            return False
        except Exception as e:
            logger.error(f"Errore nella verifica dell'iscrizione: {e}")
            return False
    return True

# Funzione per generare un link d'invito
async def generate_invite_link(channel_id: int, context: CallbackContext) -> str:
    try:
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=channel_id, member_limit=1
        )
        return invite_link.invite_link
    except Exception as e:
        logger.error(f"Errore nella generazione del link d'invito: {e}")
        return None

# Funzione per eliminare il messaggio inoltrato
async def try_delete_forwarded_message(user_id: int, context: CallbackContext):
    if user_id in forwarded_message_ids:
        try:
            await context.bot.delete_message(
                chat_id=user_id, message_id=forwarded_message_ids[user_id]
            )
            del forwarded_message_ids[user_id]
        except error.BadRequest:
            pass
        except Exception as e:
            logger.error(f"Errore nell'eliminazione del messaggio inoltrato: {e}")

# Funzione per aggiungere il pulsante "Torna all'inizio"
def add_back_to_main_button():
    return [[InlineKeyboardButton("⬅️ Torna all'inizio", callback_data="main_menu")]]

# Funzione per mostrare il menu principale
async def show_main_menu(user_id: int, context: CallbackContext, message_id: int = None):
    menu_text = (
        "⭐️ Clicca https://temu.to/k/en0oscwfxky\n"
        "per richiedere subito il tuo pacchetto buoni di 100€!\n\n"
        "Un'altra sorpresa per te! Fai clic su https://temu.to/k/er7ic7cdxyz per guadagnare insieme a me🤝!\n\n"
        "Menu Principale:"
    )
    buttons = [
        [InlineKeyboardButton(" Film 2025", callback_data="open_film")],
        [InlineKeyboardButton(" Serie TV", callback_data="open_serie_tv")],
        [InlineKeyboardButton("️ Animazione", callback_data="open_animazione")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    if message_id:
        try:
            await context.bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=menu_text,
                reply_markup=reply_markup,
                disable_web_page_preview=True  # Disabilita l'anteprima dei link
            )
        except error.BadRequest:
            sent_message = await context.bot.send_message(
                chat_id=user_id,
                text=menu_text,
                reply_markup=reply_markup,
                disable_web_page_preview=False  # Disabilita l'anteprima dei link
            )
            main_menu_message_id[user_id] = sent_message.message_id
    else:
        sent_message = await context.bot.send_message(
            chat_id=user_id,
            text=menu_text,
            reply_markup=reply_markup,
            disable_web_page_preview=False  # Disabilita l'anteprima dei link
        )
        main_menu_message_id[user_id] = sent_message.message_id

# Funzione per inoltrare un episodio
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
            buttons = []
            season, episode = map(int, query.data.split("|")[-2:])
            series_name = decode_series_name(query.data.split("|")[2])
            max_episodes = (SERIES_TV[series_name]["seasons"][season]["num_episodes"]
                            if query.data.split("|")[1] == "series"
                            else ANIMATION[series_name]["seasons"][season]["num_episodes"])

            next_episode_button = None
            if (episode + 1) <= max_episodes:
                next_episode_button = InlineKeyboardButton("Ep. successivo ->", callback_data=f"forward|{query.data.split('|')[1]}|{series_name.lower().replace(' ', '_')}|{season}|{episode+1}")

            back_to_main_button = InlineKeyboardButton("⬅️ Torna all'inizio", callback_data="main_menu")

            if next_episode_button:
                buttons.append([next_episode_button])
            buttons.append([back_to_main_button])

            await context.bot.send_message(
                user_id,
                f" {episode_title}",
                reply_markup=InlineKeyboardMarkup(buttons),
            )
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

# Funzione per mostrare il menu delle stagioni
async def show_seasons_menu(update: Update, context: CallbackContext, series_name: str, is_animation: bool = False):
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
    seasons = SERIES_TV[series_name]["seasons"] if not is_animation else ANIMATION[series_name]["seasons"]
    buttons = [
        [InlineKeyboardButton(
            f"Stagione {season}",
            callback_data=f"show_episodes|{'animation' if is_animation else 'series'}|{series_name}|{season}"
        )]
        for season in seasons.keys()
    ]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, f"Seleziona la stagione di {series_name}:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per mostrare il menu degli episodi
async def show_episodes_menu(update: Update, context: CallbackContext, series_name: str, season: int, is_animation: bool = False):
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
    # Decodifica il nome della serie dalla callback_data
    series_name = decode_series_name(series_name)
    season_data = SERIES_TV[series_name]["seasons"][season] if not is_animation else ANIMATION[series_name]["seasons"][season]
    episode_buttons = [
        InlineKeyboardButton(
            f"Episodio {ep}",
            callback_data=f"forward|{'animation' if is_animation else 'series'}|{series_name.lower().replace(' ', '_')}|{season}|{ep}",
        )
        for ep in range(1, season_data["num_episodes"] + 1)
    ]
    # Organizza i pulsanti su due colonne
    buttons = [episode_buttons[i:i + 2] for i in range(0, len(episode_buttons), 2)]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, f"Seleziona l'episodio della stagione {season} di {series_name}:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per decodificare il nome della serie dalla callback_data
def decode_series_name(encoded_name: str) -> str:
    """Decodifica il nome della serie dalla callback_data."""
    series_names = list(SERIES_TV.keys()) + list(ANIMATION.keys())
    for name in series_names:
        if encoded_name == name.lower().replace(" ", "_"):
            return name
    return encoded_name.replace("_", " ").title()  # fallback

# Gestione delle callback
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query

    if "|" in query.data:
        data = query.data.split("|")
    else:
        data = query.data.split("_")

    if data[0] == "open":
        if data[1] == "series":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name)
        elif data[1] == "animation":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name, is_animation=True)

    elif data[0] == "show_episodes":
        content_type = data[1]  # 'series' o 'animation'
        series_series_name = data[2]
        season = int(data[3])
        await show_episodes_menu(update, context, series_name, season, is_animation=(content_type == "animation"))

    elif data[0] == "forward":
        content_type = data[1]  # series or animation
        series_name = decode_series_name(data[2])
        season = int(data[3])
        episode = int(data[4])
        if content_type == "series":
            season_data = SERIES_TV[series_name]["seasons"][season]
            channel_id = SERIES_TV[series_name]["channel_id"]
        elif content_type == "animation":
            season_data = ANIMATION[series_name]["seasons"][season]
            channel_id = ANIMATION[series_name]["channel_id"]

        message_id = season_data["start_episode"] + episode -1
        await forward_episode(update, context, channel_id, message_id, f"Episodio {episode} della stagione {season} di {series_name}")

    elif data[0] == "main":
        await main_menu(update, context)

# /start
async def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
    else:
        await show_main_menu(user_id, context)

# Verifica dopo clic su "ho completato iscrizione"
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

# Gestione apertura Film 2025
async def open_film(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except Exception as e:
        logger.error(f"Errore durante l'eliminazione del messaggio in open_film: {e}")
        pass
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return
    link = await generate_invite_link(FILM_2025_CHANNEL_ID, context)
    if link:
        buttons = [[InlineKeyboardButton("Accedi a Film 2025", url=link)]]
        buttons.extend(add_back_to_main_button())
        await context.bot.send_message(
            user_id, "Ecco il canale:", reply_markup=InlineKeyboardMarkup(buttons)
        )
    else:
        buttons = add_back_to_main_button()
        await context.bot.send_message(
            user_id,
            "⚠️ Errore nel generare il link per Film 2025",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

# Gestione apertura menu Serie TV
async def open_serie_tv(update: Update, context: CallbackContext):
    logger.info("Funzione open_serie_tv chiamata!")
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
    buttons = [
        [InlineKeyboardButton(series, callback_data=f"open_series_{series.lower()}")]
        for series in sorted(SERIES_TV.keys())
    ]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, "Seleziona una serie TV:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Gestione apertura menu Animazione
async def open_animazione(update: Update, context: CallbackContext):
    logger.info("Funzione open_animazione chiamata!")
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
    buttons = [
        [InlineKeyboardButton(series, callback_data=f"open_animation_{series.lower()}")]
        for series in sorted(ANIMATION.keys())
    ]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, "Seleziona un'animazione:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per mostrare il menu delle stagioni
async def show_seasons_menu(update: Update, context: CallbackContext, series_name: str, is_animation: bool = False):
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
    seasons = SERIES_TV[series_name]["seasons"] if not is_animation else ANIMATION[series_name]["seasons"]
    buttons = [
        [InlineKeyboardButton(
            f"Stagione {season}",
            callback_data=f"show_episodes|{'animation' if is_animation else 'series'}|{series_name}|{season}"
        )]
        for season in seasons.keys()
    ]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, f"Seleziona la stagione di {series_name}:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per mostrare il menu degli episodi
async def show_episodes_menu(update: Update, context: CallbackContext, series_name: str, season: int, is_animation: bool = False):
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
    # Decodifica il nome della serie dalla callback_data
    series_name = decode_series_name(series_name)
    season_data = SERIES_TV[series_name]["seasons"][season] if not is_animation else ANIMATION[series_name]["seasons"][season]
    episode_buttons = [
        InlineKeyboardButton(
            f"Episodio {ep}",
            callback_data=f"forward|{'animation' if is_animation else 'series'}|{series_name.lower().replace(' ', '_')}|{season}|{ep}",
        )
        for ep in range(1, season_data["num_episodes"] + 1)
    ]
    # Organizza i pulsanti su due colonne
    buttons = [episode_buttons[i:i + 2] for i in range(0, len(episode_buttons), 2)]
    buttons.extend(add_back_to_main_button())
    await context.bot.send_message(
        user_id, f"Seleziona l'episodio della stagione {season} di {series_name}:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per decodificare il nome della serie dalla callback_data
def decode_series_name(encoded_name: str) -> str:
    """Decodifica il nome della serie dalla callback_data."""
    series_names = list(SERIES_TV.keys()) + list(ANIMATION.keys())
    for name in series_names:
        if encoded_name == name.lower().replace(" ", "_"):
            return name
    return encoded_name.replace("_", " ").title()  # fallback

# Gestione delle callback
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query

    if "|" in query.data:
        data = query.data.split("|")
    else:
        data = query.data.split("_")

    if data[0] == "open":
        if data[1] == "series":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name)
        elif data[1] == "animation":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name, is_animation=True)

    elif data[0] == "show_episodes":
        content_type = data[1]  # 'series' o 'animation'
        series_name = data[2]
        season = int(data[3])
        await show_episodes_menu(update, context, series_name, season, is_animation=(content_type == "animation"))

    elif data[0] == "forward":
        content_type = data[1]  # series or animation
        series_name = decode_series_name(data[2])
        season = int(data[3])
        episode = int(data[4])
        if content_type == "series":
            season_data = SERIES_TV[series_name]["seasons"][season]
            channel_id = SERIES_TV[series_name]["channel_id"]
        elif content_type == "animation":
            season_data = ANIMATION[series_name]["seasons"][season]
            channel_id = ANIMATION[series_name]["channel_id"]

        message_id = season_data["start_episode"] + episode -1
        await forward_episode(update, context, channel_id, message_id, f"Episodio {episode} della stagione {season} di {series_name}")

    elif data[0] == "main":
        await main_menu(update, context)

# Gestione del pulsante "Torna all'inizio"
async def main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    try:
        await query.message.delete()
    except:
        pass
    await show_main_menu(user_id, context, message_id=main_menu_message_id.get(user_id))

# Setup del bot
def main():
    print("In esecuzione...")
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN)
    app.connection_pool_size(128)
    app.pool_timeout(30.0)
    application = app.build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_subscription, pattern="check_subscription"))
    application.add_handler(CallbackQueryHandler(open_film, pattern="open_film"))
    application.add_handler(CallbackQueryHandler(open_serie_tv, pattern="open_serie_tv"))
    application.add_handler(CallbackQueryHandler(open_animazione, pattern="open_animazione"))
    application.add_handler(CallbackQueryHandler(callback_handler))  # Gestione delle callback
    application.add_handler(CallbackQueryHandler(main_menu, pattern="main_menu"))

    application.run_polling()

if __name__ == "__main__":
    main()
