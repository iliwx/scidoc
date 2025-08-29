"""User handlers for deep-links and requests."""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.orm import Session

from app.config import settings
from app.models.base import get_db
from app.repo.user import UserRepository
from app.repo.bundle import BundleRepository
from app.repo.message import MessageRepository
from app.services.delivery import DeliveryService
from app.services.join_gate import JoinGateService
from app.services.requests import RequestService
from app.ui.fa import PersianTexts, PersianKeyboards
from app.utils.validators import is_valid_bundle_code

logger = logging.getLogger(__name__)
router = Router()


class UserStates(StatesGroup):
    """States for user interactions."""
    submitting_request = State()


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    """Handle /start command with optional deep-link code."""
    user_id = message.from_user.id
    
    # Register/update user
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user_repo.get_or_create_user(user_id)
    finally:
        db.close()
    
    # Check if there's a deep-link code
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        code = args[1].strip()
        await handle_deep_link(message, code, state)
    else:
        await send_starting_message(message)


async def handle_deep_link(message: Message, code: str, state: FSMContext):
    """Handle deep-link with bundle code."""
    user_id = message.from_user.id
    
    # Validate code format
    if not is_valid_bundle_code(code):
        await message.reply(PersianTexts.INVALID_CODE)
        await send_starting_message(message)
        return
    
    # Check if bundle exists and is active
    db = next(get_db())
    try:
        bundle_repo = BundleRepository(db)
        bundle = bundle_repo.get_bundle_by_code(code)
        
        if not bundle or not bundle.is_active:
            await message.reply(PersianTexts.INVALID_CODE)
            await send_starting_message(message)
            return
    finally:
        db.close()
    
    # Check join gate
    join_gate_service = JoinGateService(message.bot)
    membership_info = await join_gate_service.check_user_memberships(user_id)
    
    if not membership_info["all_joined"]:
        # User needs to join channels
        missing_channels = membership_info["missing_channels"]
        
        logger.debug(f"Missing channels for user {user_id}: {missing_channels}")
        
        if missing_channels:
            text = PersianTexts.JOIN_REQUIRED
            keyboard = PersianKeyboards.join_channels(missing_channels)
        else:
            text = PersianTexts.PLEASE_JOIN_ALL
            keyboard = PersianKeyboards.join_check()
        
        await message.reply(text, reply_markup=keyboard)
        
        # Store bundle code for later delivery
        await state.set_data({"bundle_code": code})
        await state.set_state("waiting_join")
        return
    
    # Deliver bundle
    await deliver_bundle_to_user(message, code)


async def deliver_bundle_to_user(message: Message, code: str):
    """Deliver bundle to user."""
    user_id = message.from_user.id
    
    delivery_service = DeliveryService(message.bot)
    success = await delivery_service.deliver_bundle(code, user_id)
    
    if success:
        await message.reply(PersianTexts.CONTENT_DELIVERED)
        logger.info(f"Bundle {code} delivered to user {user_id}")
    else:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        logger.error(f"Failed to deliver bundle {code} to user {user_id}")


async def send_starting_message(message: Message):
    """Send starting message to user."""
    db = next(get_db())
    try:
        message_repo = MessageRepository(db)
        starting_msg = message_repo.get_starting_message()
        
        from app.config import settings
        is_admin = message.from_user.id in settings.admin_ids_list
        
        # Determine keyboard to use
        keyboard = None if is_admin else PersianKeyboards.user_main()
        
        if starting_msg and starting_msg.from_chat_id and starting_msg.message_id:
            try:
                await message.bot.copy_message(
                    chat_id=message.chat.id,
                    from_chat_id=starting_msg.from_chat_id,
                    message_id=starting_msg.message_id
                )
                # Send keyboard separately for non-admin users
                if not is_admin:
                    await message.answer("👇", reply_markup=keyboard)
            except Exception as e:
                logger.warning(f"Failed to send starting message: {e}")
                await message.reply(PersianTexts.WELCOME, reply_markup=keyboard)
        else:
            await message.reply(PersianTexts.WELCOME, reply_markup=keyboard)
        
    finally:
        db.close()


@router.callback_query(F.data == "join_check")
async def check_join_callback(callback: CallbackQuery, state: FSMContext):
    """Handle join check callback."""
    user_id = callback.from_user.id
    
    # Get stored bundle code
    current_state = await state.get_state()
    if current_state != "waiting_join":
        await callback.answer("خطا در بررسی عضویت")
        logger.warning(f"User {user_id} not in waiting_join state: {current_state}")
        return
    
    state_data = await state.get_data()
    bundle_code = state_data.get("bundle_code")
    
    if not bundle_code:
        await callback.answer("کد بسته یافت نشد")
        logger.warning(f"No bundle code found for user {user_id}")
        return
    
    logger.info(f"Checking join status for user {user_id}, bundle {bundle_code}")
    
    # Check memberships again
    join_gate_service = JoinGateService(callback.bot)
    try:
        membership_info = await join_gate_service.check_user_memberships(user_id)
        
        if not membership_info["all_joined"]:
            await callback.answer(PersianTexts.PLEASE_JOIN_ALL)
            logger.info(f"User {user_id} still missing channels: {len(membership_info['missing_channels'])}")
            return
        
        # Clear state
        await state.clear()
        
        # Deliver bundle
        await callback.answer("در حال ارسال محتوا...")
        logger.info(f"Delivering bundle {bundle_code} to user {user_id}")
        await deliver_bundle_to_user(callback.message, bundle_code)
        
    except Exception as e:
        logger.error(f"Error in join check for user {user_id}: {e}")
        await callback.answer("خطا در بررسی عضویت. لطفاً دوباره تلاش کنید.")


@router.message(F.text == PersianTexts.SUBMIT_REQUEST)
async def request_submission_start(message: Message, state: FSMContext):
    """Start request submission process."""
    await state.set_state(UserStates.submitting_request)
    await message.reply(PersianTexts.ENTER_REQUEST)


@router.message(UserStates.submitting_request)
async def submit_request(message: Message, state: FSMContext):
    """Submit user request."""
    user_id = message.from_user.id
    request_text = message.text.strip()
    
    if not request_text:
        await message.reply("متن درخواست نمی‌تواند خالی باشد:")
        return
    
    request_service = RequestService()
    success = request_service.submit_request(user_id, request_text)
    
    if success:
        await message.reply(PersianTexts.REQUEST_SUBMITTED)
        logger.info(f"Request submitted by user {user_id}")
    else:
        await message.reply(PersianTexts.ERROR_OCCURRED)
    
    await state.clear()
