import logging
from telegram.ext import CallbackContext
from telegram import Update, ChatMember
from telegram.constants import ParseMode
from telegram.error import BadRequest
from config import REQUIRED_CHANNELS  # Importa la lista dei canali richiesti

logger = logging.getLogger(__name__)

async def try_delete_forwarded_message(user_id: int, context: CallbackContext):
    """Tenta di cancellare il messaggio inoltrato se presente nell'utente."""
    message_id = context.user_data.get(f"forwarded_message_{user_id}")
    if message_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=message_id)
            del context.user_data[f"forwarded_message_{user_id}"]
        except BadRequest as e:
            logger.warning(f"try_delete_forwarded_message - Errore nella cancellazione: {e}")
        except Exception as e:
            logger.error(f"try_delete_forwarded_message - Errore inaspettato: {e}")

async def try_delete_support_message(user_id: int, context: CallbackContext):
    """Tenta di cancellare il messaggio di supporto all'iscrizione se presente nell'utente."""
    message_id = context.user_data.get(f"support_message_{user_id}")
    if message_id:
        try:
            await context.bot.delete_message(chat_id=user_id, message_id=message_id)
            del context.user_data[f"support_message_{user_id}"]
        except BadRequest as e:
            logger.warning(f"try_delete_support_message - Errore nella cancellazione: {e}")
        except Exception as e:
            logger.error(f"try_delete_support_message - Errore inaspettato: {e}")

async def is_user_subscribed(user_id: int, context: CallbackContext) -> bool:
    """Verifica se l'utente è iscritto a tutti i canali richiesti."""
    for channel_username in REQUIRED_CHANNELS:
        try:
            chat_member = await context.bot.get_chat_member(chat_id=channel_username, user_id=user_id)
            if chat_member.status == ChatMember.LEFT or chat_member.status == ChatMember.BANNED:
                return False
        except Exception as e:
            logger.warning(f"is_user_subscribed - Errore nel controllare l'iscrizione a {channel_username}: {e}")
            return False  # Considera non iscritto in caso di errore
    return True

async def send_subscription_message(user_id: int, context: CallbackContext):
    """Invia un messaggio all'utente chiedendo di iscriversi ai canali."""
    channels_text = "\n".join([f"- {channel}" for channel in REQUIRED_CHANNELS])
    message = await context.bot.send_message(
        chat_id=user_id,
        text=f"⚠️ Per continuare, devi iscriverti ai seguenti canali:\n{channels_text}\n\nDopo esserti iscritto, premi /start per tornare al menu.",
        parse_mode=ParseMode.MARKDOWN
    )
    context.user_data[f"support_message_{user_id}"] = message.message_id

async def forward_episode(update: Update, context: CallbackContext, channel_id: int, message_id: int, caption: str = None):
    """Inoltra un episodio specifico all'utente e memorizza l'ID del messaggio."""
    try:
        message = await context.bot.forward_message(
            chat_id=update.effective_user.id,
            from_chat_id=channel_id,
            message_id=message_id
        )
        context.user_data[f"forwarded_message_{update.effective_user.id}"] = message.message_id
        if caption:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text=caption,
                reply_to_message_id=message.message_id
            )
    except Exception as e:
        logger.error(f"forward_episode - Errore nell'inoltro dell'episodio {message_id} dal canale {channel_id}: {e}")
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text="Si è verificato un errore nell'inoltro dell'episodio. Riprova più tardi."
        )

async def generate_invite_link(context: CallbackContext, channel_id: int) -> str:
    """Genera un link d'invito per un canale."""
    try:
        invite_link = await context.bot.create_chat_invite_link(chat_id=channel_id, creates_join_request=False)
        return invite_link.invite_link
    except Exception as e:
        logger.error(f"generate_invite_link - Errore nella generazione del link d'invito per il canale {channel_id}: {e}")
        return f"Impossibile generare il link d'invito per {channel_id}. Contatta l'amministratore."

def add_back_to_main_button():
    """Restituisce una lista contenente un pulsante per tornare al menu principale."""
    from telegram import InlineKeyboardButton  # Importa qui per evitare dipendenze circolari
    return [[InlineKeyboardButton("⬅️ Torna al Menu Principale", callback_data="main")]]

async def show_main_menu(update: Update, context: CallbackContext):
    """Mostra il menu principale (funzione duplicata, dovrebbe essere nel bot.py)."""
    from telegram import InlineKeyboardMarkup, InlineKeyboardButton  # Importa qui per evitare dipendenze circolari
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
