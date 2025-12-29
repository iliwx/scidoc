"""Archive handlers for /add and /done commands."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from app.config import settings
from app.models.base import get_db
from app.repo.bundle import BundleRepository
from app.repo.settings import SettingsRepository
from app.ui.fa import PersianTexts, PersianKeyboards
from app.utils.helpers import generate_deep_link

logger = logging.getLogger(__name__)
router = Router()


class ArchiveStates(StatesGroup):
    """States for archive recording process."""
    recording = State()
    waiting_title = State()
    waiting_access_level = State()  # New state for access level selection


# Store recording data temporarily
recording_data = {}


@router.message(Command("add"))
async def start_recording(message: Message, state: FSMContext):
    """Start recording messages for a new bundle."""
    # Check if user is admin and in archive chat
    if (message.from_user.id not in settings.admin_ids_list or 
        message.chat.id not in settings.archive_chat_ids_list):
        return
    
    admin_id = message.from_user.id
    
    # Initialize recording data
    recording_data[admin_id] = {
        "messages": [],
        "chat_id": message.chat.id
    }
    
    await state.set_state(ArchiveStates.recording)
    await message.reply(PersianTexts.RECORDING_STARTED)
    
    logger.info(f"Admin {admin_id} started recording in chat {message.chat.id}")


@router.message(Command("done"))
async def finish_recording(message: Message, state: FSMContext):
    """Finish recording and ask for bundle title."""
    # Check if user is admin and in recording state
    if (message.from_user.id not in settings.admin_ids_list or 
        message.chat.id not in settings.archive_chat_ids_list):
        return
    
    admin_id = message.from_user.id
    current_state = await state.get_state()
    
    if current_state != ArchiveStates.recording or admin_id not in recording_data:
        await message.reply(PersianTexts.RECORDING_STOPPED)
        return
    
    # Check if any messages were recorded
    if not recording_data[admin_id]["messages"]:
        await message.reply("هیچ پیامی ضبط نشده است.")
        await state.clear()
        if admin_id in recording_data:
            del recording_data[admin_id]
        return
    
    await state.set_state(ArchiveStates.waiting_title)
    await message.reply(PersianTexts.ENTER_BUNDLE_TITLE)
    
    logger.info(f"Admin {admin_id} finished recording {len(recording_data[admin_id]['messages'])} messages")


@router.message(ArchiveStates.recording)
async def record_message(message: Message, state: FSMContext):
    """Record a message during recording state."""
    admin_id = message.from_user.id
    
    # Skip if not in recording data
    if admin_id not in recording_data:
        return
    
    # Skip commands
    if message.text and message.text.startswith('/'):
        return
    
    # Record message info
    message_info = {
        "from_chat_id": message.chat.id,
        "message_id": message.message_id,
        "media_type": _get_message_type(message),
        "caption_json": _get_caption_data(message) if message.caption else None,
        "extra_json": None
    }
    
    recording_data[admin_id]["messages"].append(message_info)
    
    logger.debug(f"Recorded message {message.message_id} from admin {admin_id}")


@router.message(ArchiveStates.waiting_title)
async def receive_title(message: Message, state: FSMContext):
    """Receive bundle title and ask for access level."""
    admin_id = message.from_user.id
    
    if admin_id not in recording_data:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    title = message.text.strip()
    if not title:
        await message.reply("عنوان نمی‌تواند خالی باشد. لطفاً عنوان معتبر وارد کنید:")
        return
    
    # Store title and ask for access level
    recording_data[admin_id]["title"] = title
    
    await state.set_state(ArchiveStates.waiting_access_level)
    await message.reply(
        PersianTexts.SELECT_ACCESS_LEVEL,
        reply_markup=PersianKeyboards.access_level_selection()
    )


@router.callback_query(F.data.startswith("level_"))
async def receive_access_level(callback: CallbackQuery, state: FSMContext):
    """Receive access level and create bundle."""
    admin_id = callback.from_user.id
    
    if admin_id not in recording_data:
        await callback.answer(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    access_level = callback.data.replace("level_", "")  # 'free', 'premium', or 'plus'
    
    title = recording_data[admin_id].get("title")
    if not title:
        await callback.answer(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    db = next(get_db())
    try:
        # Get next public number
        settings_repo = SettingsRepository(db)
        public_number = settings_repo.get_next_public_number()
        
        # Create bundle with access level
        bundle_repo = BundleRepository(db)
        bundle = bundle_repo.create_bundle(
            title=title,
            created_by=admin_id,
            public_number=public_number,
            access_level=access_level  # New parameter
        )
        
        # Add bundle items
        for msg_info in recording_data[admin_id]["messages"]:
            bundle_repo.add_bundle_item(
                bundle_id=bundle.id,
                from_chat_id=msg_info["from_chat_id"],
                message_id=msg_info["message_id"],
                media_type=msg_info["media_type"],
                caption_json=msg_info["caption_json"],
                extra_json=msg_info["extra_json"]
            )
        
        # Generate deep link
        bot_info = await callback.bot.get_me()
        deep_link = generate_deep_link(bot_info.username, bundle.code)
        
        # Access level text
        level_text = {"free": "🆓 رایگان", "premium": "💎 پریمیوم", "plus": "⭐ پلاس"}.get(access_level, access_level)
        
        # Send confirmation
        confirmation_text = PersianTexts.BUNDLE_CREATED.format(
            number=bundle.public_number_str,
            title=bundle.title,
            link=deep_link
        ) + f"\n\n🔒 سطح دسترسی: {level_text}"
        
        await callback.answer("بسته ایجاد شد ✅")
        await callback.message.edit_text(confirmation_text)
        
        logger.info(f"Bundle {bundle.public_number_str} created by admin {admin_id} with access_level={access_level}")
        
    except Exception as e:
        logger.error(f"Error creating bundle: {e}")
        await callback.answer(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()
        
        # Clean up
        await state.clear()
        if admin_id in recording_data:
            del recording_data[admin_id]


def _get_message_type(message: Message) -> str:
    """Determine the type of message."""
    if message.text:
        return "text"
    elif message.photo:
        return "photo"
    elif message.video:
        return "video"
    elif message.document:
        return "document"
    elif message.audio:
        return "audio"
    elif message.voice:
        return "voice"
    elif message.video_note:
        return "video_note"
    elif message.sticker:
        return "sticker"
    elif message.animation:
        return "animation"
    elif message.location:
        return "location"
    elif message.contact:
        return "contact"
    else:
        return "other"


def _get_caption_data(message: Message) -> dict:
    """Extract caption data from message."""
    if not message.caption:
        return None
    
    return {
        "text": message.caption,
        "entities": [
            {
                "type": entity.type,
                "offset": entity.offset,
                "length": entity.length,
                "url": entity.url if hasattr(entity, 'url') else None
            }
            for entity in (message.caption_entities or [])
        ]
    }
