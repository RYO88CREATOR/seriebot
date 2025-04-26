import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CallbackContext, CommandHandler, CallbackQueryHandler
from config import BOT_TOKEN, SERIES_TV, ANIMATION, FILM_2025_CHANNEL_ID
from utils import try_delete_forwarded_message, try_delete_support_message, is_user_subscribed, send_subscription_message, forward_episode, generate_invite_link, show_main_menu, add_back_to_main_button

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Funzione per cancellare messaggi in sicurezza
async def safe_delete(message):
    try:
        await message.delete()
    except Exception as e:
        logger.warning(f"safe_delete: {e}")

# Funzione per decodificare il nome della serie dalla callback_data
def decode_series_name(encoded_name: str) -> str:
    """Decodifica il nome della serie dalla callback_data."""
    for collection in (SERIES_TV, ANIMATION):
        for name in collection.keys():
            if encoded_name == name.lower().replace(" ", "_"):
                return name
    return encoded_name.replace("_", " ").title()

# Funzione per mostrare il menu delle stagioni
async def show_seasons_menu(update: Update, context: CallbackContext, series_name: str, is_animation: bool = False):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    await try_delete_support_message(user_id, context)
    await safe_delete(query.message)

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
    await try_delete_support_message(user_id, context)
    await safe_delete(query.message)

    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return

    series_name = decode_series_name(series_name)
    season_data = SERIES_TV[series_name]["seasons"][season] if not is_animation else ANIMATION[series_name]["seasons"][season]

    episode_buttons = [
        InlineKeyboardButton(
            f"Episodio {ep}",
            callback_data=f"forward|{'animation' if is_animation else 'series'}|{series_name.lower().replace(' ', '_')}|{season}|{ep}",
        )
        for ep in range(1, season_data["num_episodes"] + 1)
    ]
    buttons = [episode_buttons[i:i + 2] for i in range(0, len(episode_buttons), 2)]
    buttons.extend(add_back_to_main_button())

    await context.bot.send_message(
        user_id, f"Seleziona l'episodio della stagione {season} di {series_name}:", reply_markup=InlineKeyboardMarkup(buttons)
    )

# Gestione delle callback
async def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    logger.info(f"Ricevuta callback: {query.data}")
    await query.answer()

    data = query.data.split("|") if "|" in query.data else query.data.split("_")

    if data[0] == "open":
        if data[1] == "series":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name)
        elif data[1] == "animation":
            series_name = decode_series_name(data[2])
            await show_seasons_menu(update, context, series_name, is_animation=True)

    elif data[0] == "show_episodes":
        content_type = data[1]
        series_name = data[2]
        season = int(data[3])
        await show_episodes_menu(update, context, series_name, season, is_animation=(content_type == "animation"))

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
        await main_menu(update, context)
# Funzione per mostrare il menu principale
async def main_menu(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    await try_delete_forwarded_message(user_id, context)
    await try_delete_support_message(user_id, context)

    buttons = [
        [InlineKeyboardButton("🎬 Film 2025", callback_data="open_film")],
        [InlineKeyboardButton("📺 Lista Serie TV", callback_data="open_serie_tv")],
        [InlineKeyboardButton("🌸 Animazione", callback_data="open_animazione")]
    ]
    await context.bot.send_message(
        chat_id=user_id,
        text="Benvenuto nel menu principale! Scegli una categoria:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per la verifica iscrizione
async def check_subscription(update: Update, context: CallbackContext) -> bool:
    user_id = update.effective_user.id
    if not await is_user_subscribed(user_id, context):
        await send_subscription_message(user_id, context)
        return False
    return True

# Funzione per aprire il canale Film 2025
async def open_film(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    await try_delete_support_message(user_id, context)
    await safe_delete(query.message)

    if not await check_subscription(update, context):
        return

    invite_link = await generate_invite_link(context, FILM_2025_CHANNEL_ID)
    await context.bot.send_message(
        chat_id=user_id,
        text=f"🎬 Accedi subito a Film 2025:\n\n{invite_link}"
    )

# Funzione per mostrare la lista delle Serie TV
async def open_serie_tv(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    await try_delete_support_message(user_id, context)
    await safe_delete(query.message)

    if not await check_subscription(update, context):
        return

    buttons = [
        [InlineKeyboardButton(series, callback_data=f"open_series|{series.lower().replace(' ', '_')}")]
        for series in SERIES_TV.keys()
    ]
    buttons.extend(add_back_to_main_button())

    await context.bot.send_message(
        chat_id=user_id,
        text="Seleziona una Serie TV:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione per mostrare la lista dell'Animazione
async def open_animazione(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    query = update.callback_query
    await query.answer()
    await try_delete_forwarded_message(user_id, context)
    await try_delete_support_message(user_id, context)
    await safe_delete(query.message)

    if not await check_subscription(update, context):
        return

    buttons = [
        [InlineKeyboardButton(series, callback_data=f"open_animation|{series.lower().replace(' ', '_')}")]
        for series in ANIMATION.keys()
    ]
    buttons.extend(add_back_to_main_button())

    await context.bot.send_message(
        chat_id=user_id,
        text="Seleziona una serie Animata:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# Funzione principale
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", main_menu))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(CallbackQueryHandler(open_film, pattern="open_film"))
    app.add_handler(CallbackQueryHandler(open_serie_tv, pattern="open_serie_tv"))
    app.add_handler(CallbackQueryHandler(open_animazione, pattern="open_animazione"))

    logger.info("Bot avviato...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    async def run():
        await main()
    asyncio.run(run())
