"""User subscription handlers for status, tokens, purchase, and support."""
import logging
import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.config import settings
from app.models.base import get_db
from app.repo.user import UserRepository
from app.repo.subscription_plan import SubscriptionPlanRepository
from app.repo.payment_queue import PaymentQueueRepository
from app.services.subscription import SubscriptionService
from app.ui.fa import PersianTexts, PersianKeyboards
from app.utils.jalali import format_jalali_date

logger = logging.getLogger(__name__)
router = Router()


class SubscriptionStates(StatesGroup):
    """States for subscription flow."""
    selecting_plan = State()
    awaiting_payment = State()
    sending_receipt = State()
    requesting_doc = State()


# ============ STATUS SCREEN ============

@router.message(F.text == PersianTexts.BTN_MY_STATUS)
async def show_status(message: Message):
    """Show user subscription status."""
    user_id = message.from_user.id
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_or_create_user(user_id)
        
        # Determine tier name
        if user.is_subscription_active:
            tier_name = PersianTexts.TIER_PLUS if user.subscription_tier == 'plus' else PersianTexts.TIER_PREMIUM
            expiry_date = format_jalali_date(user.expiry_date)
        else:
            tier_name = PersianTexts.TIER_FREE
            expiry_date = PersianTexts.NO_EXPIRY
        
        # Get referral count
        referral_count = user_repo.get_referral_count(user.referral_code or "")
        
        status_text = PersianTexts.STATUS_SCREEN.format(
            tier_name=tier_name,
            expiry_date=expiry_date,
            tokens=user.referral_tokens,
            total_downloads=user.total_downloads,
            referral_count=referral_count
        )
        
        await message.reply(status_text, reply_markup=PersianKeyboards.status_actions())
        
    finally:
        db.close()


# ============ TOKEN SYSTEM ============

@router.message(F.text == PersianTexts.BTN_GET_TOKEN)
async def show_tokens(message: Message):
    """Show token system screen."""
    user_id = message.from_user.id
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_or_create_user(user_id)
        
        # Generate referral link
        bot_info = await message.bot.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start=ref_{user.referral_code}"
        
        token_text = PersianTexts.TOKEN_SCREEN.format(
            tokens=user.referral_tokens,
            referral_link=referral_link,
            referral_code=user.referral_code
        )
        
        await message.reply(token_text, reply_markup=PersianKeyboards.token_actions())
        
    finally:
        db.close()


@router.callback_query(F.data == "get_token")
async def get_token_callback(callback: CallbackQuery):
    """Handle get token callback."""
    await callback.answer()
    await show_tokens(callback.message)


@router.callback_query(F.data == "sub_invite")
async def invite_friends_callback(callback: CallbackQuery):
    """Handle invite friends callback."""
    await callback.answer()
    await show_tokens(callback.message)


@router.callback_query(F.data == "referral_stats")
async def referral_stats(callback: CallbackQuery):
    """Show referral statistics."""
    user_id = callback.from_user.id
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_tg_id(user_id)
        
        if not user:
            await callback.answer("خطا در دریافت اطلاعات")
            return
        
        referral_count = user_repo.get_referral_count(user.referral_code or "")
        
        stats_text = f"""👥 آمار دعوت‌های شما

✅ کاربران دعوت شده: {referral_count} نفر
🎁 توکن‌های کسب شده: {referral_count}
🪙 توکن فعلی: {user.referral_tokens}"""
        
        await callback.answer()
        await callback.message.edit_text(stats_text, reply_markup=PersianKeyboards.token_actions())
        
    finally:
        db.close()


# ============ SUBSCRIPTION PURCHASE ============

@router.message(F.text == PersianTexts.BTN_BUY_SUBSCRIPTION)
async def show_subscription_menu(message: Message, state: FSMContext):
    """Show subscription plans."""
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plans = plan_repo.get_all_active_plans()
        
        if not plans:
            await message.reply("در حال حاضر هیچ پلنی فعال نیست.")
            return
        
        await state.set_state(SubscriptionStates.selecting_plan)
        await message.reply(
            PersianTexts.SUBSCRIPTION_MENU,
            reply_markup=PersianKeyboards.subscription_plans(plans)
        )
        
    finally:
        db.close()


@router.callback_query(F.data == "sub_menu")
async def sub_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Handle subscription menu callback."""
    await callback.answer()
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plans = plan_repo.get_all_active_plans()
        
        await state.set_state(SubscriptionStates.selecting_plan)
        await callback.message.edit_text(
            PersianTexts.SUBSCRIPTION_MENU,
            reply_markup=PersianKeyboards.subscription_plans(plans)
        )
    finally:
        db.close()


@router.callback_query(F.data == "sub_renew")
async def renew_subscription(callback: CallbackQuery, state: FSMContext):
    """Handle renew subscription callback."""
    await sub_menu_callback(callback, state)


@router.callback_query(F.data.startswith("plan_") & ~F.data.startswith("plan_edit") & ~F.data.startswith("plan_add") & ~F.data.startswith("plan_toggle") & ~F.data.startswith("plan_modify"))
async def show_plan_details(callback: CallbackQuery, state: FSMContext):
    """Show plan details."""
    plan_id = callback.data.replace("plan_", "")
    
    if plan_id == "difference":
        # Show difference between premium and plus
        await callback.answer()
        await callback.message.edit_text(
            PersianTexts.SUBSCRIPTION_GUIDE,
            reply_markup=PersianKeyboards.support_understood()
        )
        return
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plan = plan_repo.get_plan_by_id(plan_id)
        
        if not plan:
            await callback.answer("پلن یافت نشد")
            return
        
        benefits = PersianTexts.BENEFITS_PLUS if plan.tier == 'plus' else PersianTexts.BENEFITS_PREMIUM
        
        details_text = PersianTexts.PLAN_DETAILS.format(
            plan_name=plan.plan_name,
            duration=plan.duration_days,
            price=f"{plan.price:,}",
            benefits=benefits
        )
        
        # Store selected plan
        await state.update_data(selected_plan=plan_id)
        
        await callback.answer()
        await callback.message.edit_text(
            details_text,
            reply_markup=PersianKeyboards.plan_confirmation(plan_id)
        )
        
    finally:
        db.close()


@router.callback_query(F.data.startswith("buy_"))
async def show_payment_details(callback: CallbackQuery, state: FSMContext):
    """Show payment details."""
    plan_id = callback.data.replace("buy_", "")
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plan = plan_repo.get_plan_by_id(plan_id)
        
        if not plan:
            await callback.answer("پلن یافت نشد")
            return
        
        # Check if user already has pending payment
        payment_repo = PaymentQueueRepository(db)
        pending = payment_repo.get_user_pending_payment(callback.from_user.id)
        
        if pending:
            await callback.answer()
            await callback.message.edit_text(PersianTexts.PAYMENT_PENDING)
            return
        
        payment_text = PersianTexts.PAYMENT_DETAILS.format(
            plan_name=plan.plan_name,
            duration=plan.duration_days,
            price=f"{plan.price:,}",
            card_number="6219-8619-0878-5420",
            card_holder="علیرضا حسین آبادی"
        )
        
        # Store payment info
        await state.update_data(selected_plan=plan_id)
        await state.set_state(SubscriptionStates.awaiting_payment)
        
        await callback.answer()
        await callback.message.edit_text(
            payment_text,
            reply_markup=PersianKeyboards.payment_actions()
        )
        
    finally:
        db.close()


@router.callback_query(F.data == "send_receipt")
async def request_receipt(callback: CallbackQuery, state: FSMContext):
    """Request user to send payment receipt."""
    await state.set_state(SubscriptionStates.sending_receipt)
    await callback.answer()
    await callback.message.edit_text(PersianTexts.SEND_SCREENSHOT)


@router.message(SubscriptionStates.sending_receipt)
async def receive_receipt(message: Message, state: FSMContext):
    """Receive payment receipt screenshot."""
    # Check if message has photo
    if not message.photo:
        await message.reply("لطفاً تصویر رسید را ارسال کنید.")
        return
    
    user_id = message.from_user.id
    data = await state.get_data()
    plan_id = data.get("selected_plan")
    
    if not plan_id:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    # Get the largest photo (best quality)
    photo = message.photo[-1]
    file_id = photo.file_id
    
    db = next(get_db())
    try:
        # Create payment queue entry
        payment_repo = PaymentQueueRepository(db)
        payment = payment_repo.create_payment(
            user_id=user_id,
            plan_id=plan_id,
            screenshot_file_id=file_id
        )
        
        await message.reply(PersianTexts.PAYMENT_SUBMITTED)
        logger.info(f"Payment receipt submitted by user {user_id} for plan {plan_id}")
        
        # Notify admin about new payment (if queue milestone)
        pending_count = payment_repo.get_pending_count()
        if pending_count in [5, 10, 20, 30, 40, 50]:
            for admin_id in settings.admin_ids_list:
                try:
                    await message.bot.send_message(
                        admin_id,
                        PersianTexts.PAYMENT_QUEUE_ALERT.format(count=pending_count)
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify admin {admin_id}: {e}")
        
    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        await message.reply(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data == "cancel_payment")
async def cancel_payment(callback: CallbackQuery, state: FSMContext):
    """Cancel payment."""
    await state.clear()
    await callback.answer("پرداخت لغو شد")
    await callback.message.edit_text("پرداخت لغو شد. در صورت نیاز دوباره از منو اقدام کنید.")


# ============ SUPPORT MENU ============

@router.message(F.text == PersianTexts.BTN_SUPPORT)
async def show_support_menu(message: Message):
    """Show support menu."""
    await message.reply(
        PersianTexts.SUPPORT_MENU,
        reply_markup=PersianKeyboards.support_menu()
    )


@router.callback_query(F.data == "support_guide")
async def support_guide(callback: CallbackQuery):
    """Show subscription guide."""
    await callback.answer()
    await callback.message.edit_text(
        PersianTexts.SUBSCRIPTION_GUIDE,
        reply_markup=PersianKeyboards.support_understood()
    )


@router.callback_query(F.data == "support_back")
async def support_back(callback: CallbackQuery):
    """Back to support menu."""
    await callback.answer()
    await callback.message.edit_text(
        PersianTexts.SUPPORT_MENU,
        reply_markup=PersianKeyboards.support_menu()
    )


@router.callback_query(F.data == "support_request")
async def support_request_doc(callback: CallbackQuery, state: FSMContext):
    """Start document request."""
    await state.set_state(SubscriptionStates.requesting_doc)
    await callback.answer()
    await callback.message.edit_text(PersianTexts.REQUEST_DOC_PROMPT)


@router.message(SubscriptionStates.requesting_doc)
async def receive_doc_request(message: Message, state: FSMContext):
    """Receive document request."""
    request_text = message.text
    
    if not request_text:
        await message.reply("لطفاً متن درخواست را ارسال کنید.")
        return
    
    # Forward to admins
    user = message.from_user
    forward_text = f"""📝 درخواست مستند جدید

👤 کاربر: {user.full_name}
🆔 ID: {user.id}
📱 یوزرنیم: @{user.username or 'ندارد'}

📄 درخواست:
{request_text}"""

    for admin_id in settings.admin_ids_list:
        try:
            await message.bot.send_message(admin_id, forward_text)
        except Exception as e:
            logger.warning(f"Failed to send doc request to admin {admin_id}: {e}")
    
    await message.reply(PersianTexts.REQUEST_DOC_SUBMITTED)
    await state.clear()


@router.callback_query(F.data == "support_contact")
async def support_contact(callback: CallbackQuery):
    """Show support contact."""
    await callback.answer()
    await callback.message.edit_text(
        "💬 برای بررسی وضعیت پرداخت یا سایر سوالات:\n\n📞 @techuebepro",
        reply_markup=PersianKeyboards.support_understood()
    )


# ============ COPY REFERRAL LINK ============

@router.callback_query(F.data == "copy_referral")
async def copy_referral_link(callback: CallbackQuery):
    """Handle copy referral link - show the link for user to copy."""
    user_id = callback.from_user.id
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_tg_id(user_id)
        
        if not user:
            await callback.answer("خطا در دریافت اطلاعات")
            return
        
        bot_info = await callback.bot.get_me()
        referral_link = f"https://t.me/{bot_info.username}?start=ref_{user.referral_code}"
        
        # Send link as message so user can copy it
        await callback.answer("لینک در پیام جداگانه ارسال شد")
        await callback.message.answer(f"🔗 لینک دعوت شما:\n\n{referral_link}")
        
    finally:
        db.close()


# ============ REDOWNLOAD ============

@router.callback_query(F.data.startswith("redownload_"))
async def redownload_bundle(callback: CallbackQuery):
    """Handle re-download of a bundle (no token deduction)."""
    bundle_code = callback.data.replace("redownload_", "")
    user_id = callback.from_user.id
    
    db = next(get_db())
    try:
        from app.repo.bundle import BundleRepository
        from app.services.delivery import DeliveryService
        
        user_repo = UserRepository(db)
        bundle_repo = BundleRepository(db)
        
        user = user_repo.get_user_by_tg_id(user_id)
        bundle = bundle_repo.get_bundle_by_code(bundle_code)
        
        if not user or not bundle:
            await callback.answer("خطا در دریافت فایل")
            return
        
        await callback.answer("در حال ارسال فایل...")
        
        # Deliver the bundle (re-download - already in history)
        delivery_service = DeliveryService(callback.bot)
        success = await delivery_service.deliver_bundle(bundle_code, user_id)
        
        if success:
            from app.ui.fa import PersianTexts, PersianKeyboards
            delivery_text = PersianTexts.FILE_DELIVERY.format(doc_name=bundle.title)
            await callback.message.answer(
                delivery_text,
                reply_markup=PersianKeyboards.redownload_button(bundle_code)
            )
            logger.info(f"Bundle {bundle_code} re-downloaded by user {user_id}")
        else:
            await callback.message.answer(PersianTexts.ERROR_OCCURRED)
            logger.error(f"Failed to re-download bundle {bundle_code} for user {user_id}")
    
    except Exception as e:
        logger.error(f"Error in redownload: {e}")
        await callback.message.answer(PersianTexts.ERROR_OCCURRED)
    finally:
        db.close()

