"""Admin panel handlers."""
import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from app.config import settings
from app.models.base import get_db
from app.repo.bundle import BundleRepository
from app.repo.channel import ChannelRepository
from app.repo.message import MessageRepository
from app.repo.request import RequestRepository
from app.services.broadcast import BroadcastService
from app.services.stats import StatsService
from app.services.join_gate import JoinGateService
from app.ui.fa import PersianTexts, PersianKeyboards
from app.utils.validators import validate_channel_link, extract_chat_id_from_link
from app.utils.helpers import generate_deep_link, create_backup

logger = logging.getLogger(__name__)
router = Router()


class AdminStates(StatesGroup):
    """States for admin interactions."""
    bundle_search = State()
    channel_add = State()
    starting_message = State()
    ending_name = State()
    ending_message = State()
    broadcast_message = State()
    broadcast_confirm = State()


# Store temporary data
admin_temp_data = {}


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_ids_list


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    """Show admin panel."""
    if not is_admin(message.from_user.id):
        await message.reply(PersianTexts.ACCESS_DENIED)
        return
    
    await state.clear()
    await message.reply(
        PersianTexts.ADMIN_WELCOME,
        reply_markup=PersianKeyboards.admin_main_extended()  # Use extended panel with subscription features
    )


# Bundle Management
@router.callback_query(F.data == "admin_bundles")
async def bundles_menu(callback: CallbackQuery):
    """Show bundles menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.BUNDLES_MENU,
        reply_markup=PersianKeyboards.bundles_menu()
    )


@router.callback_query(F.data == "bundle_search")
async def bundle_search_start(callback: CallbackQuery, state: FSMContext):
    """Start bundle search."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminStates.bundle_search)
    await callback.message.edit_text(PersianTexts.BUNDLE_SEARCH)


@router.message(AdminStates.bundle_search)
async def bundle_search_execute(message: Message, state: FSMContext):
    """Execute bundle search."""
    query = message.text.strip()
    
    db = next(get_db())
    try:
        bundle_repo = BundleRepository(db)
        bundles = bundle_repo.search_bundles(query)
        
        if not bundles:
            await message.reply(PersianTexts.NO_BUNDLES_FOUND)
            await state.clear()
            return
        
        # Show results
        for bundle in bundles[:10]:  # Limit to 10 results
            status = "✅ فعال" if bundle.is_active else "❌ غیرفعال"
            text = f"📦 {bundle.public_number_str} - {bundle.title}\n🔗 کد: {bundle.code}\n📊 وضعیت: {status}"
            
            keyboard = PersianKeyboards.bundle_actions(bundle.id, bundle.is_active)
            await message.reply(text, reply_markup=keyboard)
        
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data.startswith("bundle_copy_"))
async def copy_bundle_link(callback: CallbackQuery):
    """Copy bundle deep link."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    bundle_id = int(callback.data.split("_")[-1])
    
    db = next(get_db())
    try:
        bundle_repo = BundleRepository(db)
        bundle = bundle_repo.get_bundle_by_id(bundle_id)
        
        if bundle:
            bot_info = await callback.bot.get_me()
            deep_link = generate_deep_link(bot_info.username, bundle.code)
            await callback.answer(f"لینک کپی شد: {deep_link}", show_alert=True)
        else:
            await callback.answer("بسته یافت نشد")
    finally:
        db.close()


@router.callback_query(F.data.startswith("bundle_activate_"))
async def activate_bundle(callback: CallbackQuery):
    """Activate bundle."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    bundle_id = int(callback.data.split("_")[-1])
    
    db = next(get_db())
    try:
        bundle_repo = BundleRepository(db)
        new_status = bundle_repo.toggle_bundle_status(bundle_id)
        
        if new_status:
            await callback.answer(PersianTexts.BUNDLE_ACTIVATED)
        else:
            await callback.answer(PersianTexts.BUNDLE_DEACTIVATED)
    finally:
        db.close()


@router.callback_query(F.data.startswith("bundle_deactivate_"))
async def deactivate_bundle(callback: CallbackQuery):
    """Deactivate bundle."""
    # Same logic as activate (toggle_bundle_status handles both)
    await activate_bundle(callback)


# Channel Management
@router.callback_query(F.data == "admin_channels")
async def channels_menu(callback: CallbackQuery):
    """Show channels menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.CHANNELS_MENU,
        reply_markup=PersianKeyboards.channels_menu()
    )


@router.callback_query(F.data == "channel_add")
async def channel_add_start(callback: CallbackQuery, state: FSMContext):
    """Start adding channel."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminStates.channel_add)
    await callback.message.edit_text(PersianTexts.ENTER_CHANNEL_LINK)


@router.message(AdminStates.channel_add)
async def channel_add_execute(message: Message, state: FSMContext):
    """Add new channel."""
    link = message.text.strip()
    
    if not validate_channel_link(link):
        await message.reply(PersianTexts.INVALID_CHANNEL_LINK)
        return
    
    # Extract chat info
    chat_info = extract_chat_id_from_link(link)
    
    db = next(get_db())
    try:
        channel_repo = ChannelRepository(db)
        join_gate_service = JoinGateService(message.bot)
        
        if chat_info[0]:  # Direct chat ID
            chat_id = chat_info[0]
            try:
                chat = await message.bot.get_chat(chat_id)
                title = chat.title or chat.first_name or "Unknown"
                username = chat.username
            except Exception as e:
                logger.error(f"Error getting chat info for {chat_id}: {e}")
                title = "Unknown Channel"
                username = None
        else:
            # Need to resolve username or invite link
            try:
                if chat_info[1]:  # Username
                    chat = await message.bot.get_chat(f"@{chat_info[1]}")
                else:  # Invite link - this is tricky, we'll store it as-is
                    await message.reply("لینک دعوت خصوصی ذخیره شد. عنوان به صورت خودکار به‌روزرسانی خواهد شد.")
                    channel_repo.create_channel(
                        chat_id=0,  # Placeholder
                        title="کانال خصوصی",
                        username=None,
                        join_link=link
                    )
                    await message.reply(PersianTexts.CHANNEL_ADDED)
                    await state.clear()
                    return
                
                chat_id = chat.id
                title = chat.title or chat.first_name or "Unknown"
                username = chat.username
            except Exception as e:
                logger.error(f"Error resolving channel {link}: {e}")
                await message.reply("خطا در دریافت اطلاعات کانال")
                return
        
        # Check if channel already exists
        existing = channel_repo.get_channel_by_chat_id(chat_id)
        if existing:
            await message.reply("این کانال قبلاً اضافه شده است.")
            await state.clear()
            return
        
        # Create channel
        channel_repo.create_channel(
            chat_id=chat_id,
            title=title,
            username=username,
            join_link=link if not username else f"https://t.me/{username}"
        )
        
        await message.reply(PersianTexts.CHANNEL_ADDED)
        logger.info(f"Channel {title} ({chat_id}) added by admin {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error adding channel: {e}")
        await message.reply(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data == "channel_list")
async def channel_list(callback: CallbackQuery):
    """Show channel list."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        channel_repo = ChannelRepository(db)
        channels = channel_repo.get_all_active_channels()
        
        if not channels:
            await callback.message.edit_text(PersianTexts.NO_CHANNELS)
            return
        
        for channel in channels:
            status = "✅ فعال" if channel.is_active else "❌ غیرفعال"
            text = f"📢 {channel.title}\n🆔 {channel.chat_id}\n📊 وضعیت: {status}"
            
            keyboard = PersianKeyboards.channel_actions(channel.id)
            await callback.message.answer(text, reply_markup=keyboard)
            
    finally:
        db.close()


@router.callback_query(F.data.startswith("channel_delete_"))
async def delete_channel(callback: CallbackQuery):
    """Delete channel."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    channel_id = int(callback.data.split("_")[-1])
    
    db = next(get_db())
    try:
        channel_repo = ChannelRepository(db)
        success = channel_repo.delete_channel(channel_id)
        
        if success:
            await callback.answer(PersianTexts.CHANNEL_REMOVED)
            await callback.message.delete()
        else:
            await callback.answer("خطا در حذف کانال")
    finally:
        db.close()


# Messages Management
@router.callback_query(F.data == "admin_messages")
async def messages_menu(callback: CallbackQuery):
    """Show messages menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.MESSAGES_MENU,
        reply_markup=PersianKeyboards.messages_menu()
    )


@router.callback_query(F.data == "msg_starting")
async def starting_message_set(callback: CallbackQuery, state: FSMContext):
    """Set starting message."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminStates.starting_message)
    await callback.message.edit_text(PersianTexts.SET_STARTING_MSG)


@router.message(AdminStates.starting_message)
async def starting_message_save(message: Message, state: FSMContext):
    """Save starting message."""
    db = next(get_db())
    try:
        message_repo = MessageRepository(db)
        message_repo.set_starting_message(message.chat.id, message.message_id)
        
        await message.reply(PersianTexts.STARTING_MSG_SET)
        logger.info(f"Starting message set by admin {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error setting starting message: {e}")
        await message.reply(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data == "msg_ending")
async def ending_messages_menu(callback: CallbackQuery):
    """Show ending messages menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.ENDING_MESSAGES,
        reply_markup=PersianKeyboards.ending_messages_menu()
    )


@router.callback_query(F.data == "ending_add")
async def ending_add_start(callback: CallbackQuery, state: FSMContext):
    """Start adding ending message."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminStates.ending_name)
    await callback.message.edit_text(PersianTexts.ENTER_ENDING_NAME)


@router.message(AdminStates.ending_name)
async def ending_name_received(message: Message, state: FSMContext):
    """Receive ending message name."""
    name = message.text.strip()
    
    if not name:
        await message.reply("نام نمی‌تواند خالی باشد:")
        return
    
    # Store name temporarily
    admin_temp_data[message.from_user.id] = {"ending_name": name}
    
    await state.set_state(AdminStates.ending_message)
    await message.reply(PersianTexts.SEND_ENDING_MSG)


@router.message(AdminStates.ending_message)
async def ending_message_save(message: Message, state: FSMContext):
    """Save ending message."""
    admin_id = message.from_user.id
    
    if admin_id not in admin_temp_data:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    name = admin_temp_data[admin_id]["ending_name"]
    
    db = next(get_db())
    try:
        message_repo = MessageRepository(db)
        message_repo.create_ending_message(name, message.chat.id, message.message_id)
        
        await message.reply(PersianTexts.ENDING_MSG_ADDED)
        logger.info(f"Ending message '{name}' added by admin {admin_id}")
        
    except Exception as e:
        logger.error(f"Error adding ending message: {e}")
        await message.reply(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()
        await state.clear()
        if admin_id in admin_temp_data:
            del admin_temp_data[admin_id]


# Requests Management
@router.callback_query(F.data == "admin_requests")
async def requests_menu(callback: CallbackQuery):
    """Show requests."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        request_repo = RequestRepository(db)
        requests = request_repo.get_open_requests()
        
        if not requests:
            await callback.message.edit_text(PersianTexts.NO_REQUESTS)
            return
        
        for request in requests[:10]:  # Limit to 10
            text = f"👤 کاربر: {request.user_id}\n📝 متن: {request.text}\n📅 تاریخ: {request.created_at.strftime('%Y-%m-%d %H:%M')}"
            keyboard = PersianKeyboards.request_actions(request.id)
            await callback.message.answer(text, reply_markup=keyboard)
            
    finally:
        db.close()


@router.callback_query(F.data.startswith("request_resolve_"))
async def resolve_request(callback: CallbackQuery):
    """Resolve request."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    request_id = int(callback.data.split("_")[-1])
    
    db = next(get_db())
    try:
        request_repo = RequestRepository(db)
        success = request_repo.resolve_request(request_id)
        
        if success:
            await callback.answer(PersianTexts.REQUEST_RESOLVED)
            await callback.message.delete()
        else:
            await callback.answer("خطا در حل درخواست")
    finally:
        db.close()


# Broadcast
@router.callback_query(F.data == "admin_broadcast")
async def broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Start broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminStates.broadcast_message)
    await callback.message.edit_text(PersianTexts.SEND_BROADCAST)


@router.message(AdminStates.broadcast_message)
async def broadcast_confirm(message: Message, state: FSMContext):
    """Confirm broadcast."""
    # Store message info
    admin_temp_data[message.from_user.id] = {
        "broadcast_chat_id": message.chat.id,
        "broadcast_message_id": message.message_id
    }
    
    # Get user count
    broadcast_service = BroadcastService(message.bot)
    user_count = broadcast_service.get_user_count()
    
    # Show preview
    preview_text = PersianTexts.BROADCAST_PREVIEW.format(
        message=message.text or "[پیام رسانه‌ای]",
        count=user_count
    )
    
    await state.set_state(AdminStates.broadcast_confirm)
    await message.reply(
        preview_text,
        reply_markup=PersianKeyboards.broadcast_confirm(user_count)
    )


@router.callback_query(F.data == "broadcast_send")
async def broadcast_execute(callback: CallbackQuery, state: FSMContext):
    """Execute broadcast."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    admin_id = callback.from_user.id
    
    if admin_id not in admin_temp_data:
        await callback.answer("خطا در اطلاعات پیام")
        return
    
    data = admin_temp_data[admin_id]
    
    await callback.answer(PersianTexts.BROADCAST_STARTED)
    await callback.message.edit_text(PersianTexts.BROADCAST_STARTED)
    
    # Execute broadcast
    broadcast_service = BroadcastService(callback.bot)
    result = await broadcast_service.send_broadcast(
        data["broadcast_chat_id"],
        data["broadcast_message_id"]
    )
    
    # Send result
    result_text = PersianTexts.BROADCAST_COMPLETED.format(
        success=result["success"],
        failed=result["failed"]
    )
    
    await callback.message.edit_text(result_text)
    
    # Clean up
    await state.clear()
    if admin_id in admin_temp_data:
        del admin_temp_data[admin_id]


@router.callback_query(F.data == "broadcast_cancel")
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel broadcast."""
    admin_id = callback.from_user.id
    
    await callback.message.edit_text(PersianTexts.BROADCAST_CANCELLED)
    await state.clear()
    
    if admin_id in admin_temp_data:
        del admin_temp_data[admin_id]


# Backup
@router.callback_query(F.data == "admin_backup")
async def backup_menu(callback: CallbackQuery):
    """Show backup menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.BACKUP_MENU,
        reply_markup=PersianKeyboards.backup_menu()
    )


@router.callback_query(F.data == "backup_run")
async def backup_execute(callback: CallbackQuery):
    """Execute backup."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.answer(PersianTexts.BACKUP_STARTED)
    await callback.message.edit_text(PersianTexts.BACKUP_STARTED)
    
    try:
        backup_path = create_backup()
        
        if backup_path and os.path.exists(backup_path):
            # Send backup file to admin
            backup_file = FSInputFile(backup_path)
            await callback.message.answer_document(
                backup_file,
                caption="🗄 پشتیبان‌گیری دیتابیس"
            )
            
            await callback.message.edit_text(PersianTexts.BACKUP_COMPLETED)
            logger.info(f"Backup created and sent to admin {callback.from_user.id}")
        else:
            await callback.message.edit_text(PersianTexts.BACKUP_FAILED)
            
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        await callback.message.edit_text(PersianTexts.BACKUP_FAILED)


# Statistics
@router.callback_query(F.data == "admin_stats")
async def stats_menu(callback: CallbackQuery):
    """Show stats menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.STATS_MENU,
        reply_markup=PersianKeyboards.stats_menu()
    )


@router.callback_query(F.data == "stats_weekly")
async def stats_weekly(callback: CallbackQuery):
    """Show weekly stats."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    stats_service = StatsService()
    stats = stats_service.get_weekly_stats()
    
    text = PersianTexts.STATS_WEEKLY_REPORT.format(
        downloads=stats["downloads"],
        active_users=stats["active_users"],
        top_bundle=stats["top_bundle"]
    )
    
    await callback.message.edit_text(text)


@router.callback_query(F.data == "stats_monthly")
async def stats_monthly(callback: CallbackQuery):
    """Show monthly stats."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    stats_service = StatsService()
    stats = stats_service.get_monthly_stats()
    
    text = PersianTexts.STATS_MONTHLY_REPORT.format(
        downloads=stats["downloads"],
        active_users=stats["active_users"],
        top_bundle=stats["top_bundle"]
    )
    
    await callback.message.edit_text(text)


@router.callback_query(F.data == "stats_total")
async def stats_total(callback: CallbackQuery):
    """Show total stats."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    stats_service = StatsService()
    stats = stats_service.get_total_stats()
    
    text = PersianTexts.STATS_TOTAL_REPORT.format(
        downloads=stats["downloads"],
        total_users=stats["total_users"],
        total_bundles=stats["total_bundles"],
        top_bundle=stats["top_bundle"]
    )
    
    await callback.message.edit_text(text)


# Back buttons
@router.callback_query(F.data == "admin_main")
async def back_to_main(callback: CallbackQuery):
    """Back to main admin menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.ADMIN_WELCOME,
        reply_markup=PersianKeyboards.admin_main()
    )
