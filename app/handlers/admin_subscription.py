"""Admin handlers for subscription management, payments, and plans."""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.config import settings
from app.models.base import get_db
from app.repo.subscription_plan import SubscriptionPlanRepository
from app.repo.payment_queue import PaymentQueueRepository
from app.repo.user import UserRepository
from app.services.subscription import SubscriptionService
from app.ui.fa import PersianTexts, PersianKeyboards
from app.utils.jalali import format_jalali_datetime

logger = logging.getLogger(__name__)
router = Router()


class AdminSubscriptionStates(StatesGroup):
    """States for admin subscription operations."""
    adding_plan_name = State()
    adding_plan_days = State()
    adding_plan_tier = State()
    adding_plan_price = State()
    searching_user = State()
    adding_user_tokens = State()
    # Scheduled broadcast states
    broadcast_message = State()
    broadcast_schedule_time = State()
    # Offer states
    offer_duration = State()


# Store temporary data
admin_temp_data = {}


def is_admin(user_id: int) -> bool:
    """Check if user is admin."""
    return user_id in settings.admin_ids_list


# ============ ADMIN MAIN PANEL (EXTENDED) ============

@router.callback_query(F.data == "admin_main")
async def admin_main_extended(callback: CallbackQuery):
    """Show extended admin main menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.message.edit_text(
        PersianTexts.ADMIN_WELCOME,
        reply_markup=PersianKeyboards.admin_main_extended()
    )


# ============ PLAN MANAGEMENT ============

@router.callback_query(F.data == "admin_plans")
async def show_plans_menu(callback: CallbackQuery):
    """Show plans management menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plans = plan_repo.get_all_plans()
        
        text = PersianTexts.ADMIN_PLANS_MENU + "\n\n📋 پلن‌های موجود:"
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.plans_management(plans)
        )
    finally:
        db.close()


@router.callback_query(F.data == "plan_add")
async def add_plan_start(callback: CallbackQuery, state: FSMContext):
    """Start adding a new plan."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminSubscriptionStates.adding_plan_name)
    await callback.answer()
    await callback.message.edit_text(PersianTexts.ENTER_PLAN_NAME)


@router.message(AdminSubscriptionStates.adding_plan_name)
async def receive_plan_name(message: Message, state: FSMContext):
    """Receive plan name."""
    plan_name = message.text.strip()
    
    if not plan_name:
        await message.reply("نام پلن نمی‌تواند خالی باشد.")
        return
    
    admin_temp_data[message.from_user.id] = {"name": plan_name}
    
    await state.set_state(AdminSubscriptionStates.adding_plan_days)
    await message.reply(PersianTexts.ENTER_PLAN_DAYS)


@router.message(AdminSubscriptionStates.adding_plan_days)
async def receive_plan_days(message: Message, state: FSMContext):
    """Receive plan duration."""
    try:
        days = int(message.text.strip())
        if days <= 0:
            raise ValueError()
    except ValueError:
        await message.reply("لطفاً یک عدد معتبر وارد کنید.")
        return
    
    admin_temp_data[message.from_user.id]["days"] = days
    
    await state.set_state(AdminSubscriptionStates.adding_plan_tier)
    await message.reply(
        PersianTexts.SELECT_PLAN_TIER,
        reply_markup=PersianKeyboards.tier_selection()
    )


@router.callback_query(F.data.startswith("tier_"))
async def receive_plan_tier(callback: CallbackQuery, state: FSMContext):
    """Receive plan tier."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    tier = callback.data.replace("tier_", "")
    admin_temp_data[callback.from_user.id]["tier"] = tier
    
    await state.set_state(AdminSubscriptionStates.adding_plan_price)
    await callback.answer()
    await callback.message.edit_text(PersianTexts.ENTER_PLAN_PRICE)


@router.message(AdminSubscriptionStates.adding_plan_price)
async def receive_plan_price(message: Message, state: FSMContext):
    """Receive plan price and create plan."""
    try:
        price = int(message.text.strip().replace(",", ""))
        if price <= 0:
            raise ValueError()
    except ValueError:
        await message.reply("لطفاً یک عدد معتبر وارد کنید.")
        return
    
    admin_id = message.from_user.id
    data = admin_temp_data.get(admin_id, {})
    
    if not data:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        
        # Generate plan_id from name
        plan_id = data["name"].replace(" ", "_").lower()[:20]
        plan_id = f"{plan_id}_{int(datetime.now().timestamp())}"
        
        # Get next display order
        display_order = plan_repo.get_next_display_order()
        
        plan = plan_repo.create_plan(
            plan_id=plan_id,
            plan_name=data["name"],
            duration_days=data["days"],
            tier=data["tier"],
            price=price,
            display_order=display_order
        )
        
        await message.reply(
            PersianTexts.PLAN_ADDED.format(name=plan.plan_name, price=f"{price:,}")
        )
        logger.info(f"Plan {plan_id} created by admin {admin_id}")
        
    finally:
        db.close()
        await state.clear()
        if admin_id in admin_temp_data:
            del admin_temp_data[admin_id]


@router.callback_query(F.data.startswith("plan_edit_"))
async def show_plan_edit(callback: CallbackQuery):
    """Show plan edit options."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    plan_pk = int(callback.data.replace("plan_edit_", ""))
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        plan = plan_repo.get_plan_by_pk(plan_pk)
        
        if not plan:
            await callback.answer("پلن یافت نشد")
            return
        
        tier_text = "پریمیوم" if plan.tier == "premium" else "پلاس"
        status_text = "فعال" if plan.is_active else "غیرفعال"
        
        text = f"""📦 {plan.plan_name}

⏱️ مدت: {plan.duration_days} روز
🎯 نوع: {tier_text}
💰 قیمت: {plan.price:,} تومان
📊 وضعیت: {status_text}"""
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.plan_edit_actions(plan.id, plan.is_active)
        )
    finally:
        db.close()


@router.callback_query(F.data.startswith("plan_toggle_"))
async def toggle_plan_status(callback: CallbackQuery):
    """Toggle plan active status."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    plan_pk = int(callback.data.replace("plan_toggle_", ""))
    
    db = next(get_db())
    try:
        plan_repo = SubscriptionPlanRepository(db)
        new_status = plan_repo.toggle_plan_status(plan_pk)
        
        if new_status is not None:
            status_text = "فعال شد ✅" if new_status else "غیرفعال شد ❌"
            await callback.answer(f"پلن {status_text}")
            
            # Refresh view
            await show_plans_menu(callback)
        else:
            await callback.answer("خطا در تغییر وضعیت")
    finally:
        db.close()


# ============ PAYMENT VERIFICATION ============

@router.callback_query(F.data == "admin_payments")
async def show_payments_queue(callback: CallbackQuery):
    """Show pending payments queue."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        payment_repo = PaymentQueueRepository(db)
        pending = payment_repo.get_pending_payments()
        
        if not pending:
            await callback.answer()
            await callback.message.edit_text(
                PersianTexts.PAYMENT_QUEUE_EMPTY,
                reply_markup=PersianKeyboards.admin_main_extended()
            )
            return
        
        # Show first pending payment
        payment = pending[0]
        plan_repo = SubscriptionPlanRepository(db)
        plan = plan_repo.get_plan_by_id(payment.plan_id)
        
        text = PersianTexts.PAYMENT_QUEUE_ITEM.format(
            index=1,
            total=len(pending),
            username=f"ID:{payment.user_id}",
            user_id=payment.user_id,
            plan_name=plan.plan_name if plan else payment.plan_id,
            price=f"{plan.price:,}" if plan else "نامشخص",
            submitted_at=format_jalali_datetime(int(payment.submitted_at.timestamp()))
        )
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.payment_verification(payment.id, len(pending) > 1)
        )
    finally:
        db.close()


@router.callback_query(F.data.startswith("pay_view_"))
async def view_payment_screenshot(callback: CallbackQuery):
    """View payment screenshot."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    payment_id = int(callback.data.replace("pay_view_", ""))
    
    db = next(get_db())
    try:
        payment_repo = PaymentQueueRepository(db)
        payment = payment_repo.get_payment_by_id(payment_id)
        
        if not payment:
            await callback.answer("پرداخت یافت نشد")
            return
        
        # Send screenshot as photo
        await callback.answer("در حال ارسال رسید...")
        await callback.message.answer_photo(
            payment.screenshot_file_id,
            caption=f"📸 رسید پرداخت کاربر {payment.user_id}"
        )
    finally:
        db.close()


@router.callback_query(F.data.startswith("pay_approve_"))
async def approve_payment(callback: CallbackQuery):
    """Approve payment and activate subscription."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    payment_id = int(callback.data.replace("pay_approve_", ""))
    admin_username = callback.from_user.username or str(callback.from_user.id)
    
    db = next(get_db())
    try:
        payment_repo = PaymentQueueRepository(db)
        payment = payment_repo.get_payment_by_id(payment_id)
        
        if not payment:
            await callback.answer("پرداخت یافت نشد")
            return
        
        if payment.status != "pending":
            await callback.answer("این پرداخت قبلاً پردازش شده")
            return
        
        # Get user and plan
        user_repo = UserRepository(db)
        plan_repo = SubscriptionPlanRepository(db)
        
        user = user_repo.get_user_by_tg_id(payment.user_id)
        plan = plan_repo.get_plan_by_id(payment.plan_id)
        
        if not user or not plan:
            await callback.answer("کاربر یا پلن یافت نشد")
            return
        
        # Activate subscription
        success = SubscriptionService.activate_subscription(user, payment.plan_id, db)
        
        if not success:
            await callback.answer("خطا در فعالسازی اشتراک")
            return
        
        # Update payment status
        payment_repo.approve_payment(payment_id, admin_username)
        
        # Notify user
        from app.utils.jalali import format_jalali_date
        expiry_date = format_jalali_date(user.expiry_date)
        
        try:
            await callback.bot.send_message(
                payment.user_id,
                PersianTexts.PAYMENT_APPROVED.format(
                    plan_name=plan.plan_name,
                    duration=plan.duration_days,
                    expiry_date=expiry_date
                )
            )
        except Exception as e:
            logger.warning(f"Failed to notify user {payment.user_id}: {e}")
        
        await callback.answer("اشتراک فعال شد ✅")
        logger.info(f"Payment {payment_id} approved by {admin_username}")
        
        # Show next payment or queue
        await show_payments_queue(callback)
        
    finally:
        db.close()


@router.callback_query(F.data.startswith("pay_reject_"))
async def reject_payment(callback: CallbackQuery):
    """Reject payment."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    payment_id = int(callback.data.replace("pay_reject_", ""))
    admin_username = callback.from_user.username or str(callback.from_user.id)
    
    db = next(get_db())
    try:
        payment_repo = PaymentQueueRepository(db)
        payment = payment_repo.get_payment_by_id(payment_id)
        
        if not payment:
            await callback.answer("پرداخت یافت نشد")
            return
        
        # Reject payment
        payment_repo.reject_payment(payment_id, admin_username)
        
        # Notify user
        try:
            await callback.bot.send_message(
                payment.user_id,
                PersianTexts.PAYMENT_REJECTED.format(support_username="techuebepro")
            )
        except Exception as e:
            logger.warning(f"Failed to notify user {payment.user_id}: {e}")
        
        await callback.answer("پرداخت رد شد ❌")
        logger.info(f"Payment {payment_id} rejected by {admin_username}")
        
        # Show next payment
        await show_payments_queue(callback)
        
    finally:
        db.close()


@router.callback_query(F.data == "pay_next")
async def next_payment(callback: CallbackQuery):
    """Show next pending payment."""
    await show_payments_queue(callback)


# ============ USER MANAGEMENT ============

@router.callback_query(F.data == "admin_users")
async def show_users_menu(callback: CallbackQuery, state: FSMContext):
    """Show user management menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminSubscriptionStates.searching_user)
    await callback.answer()
    await callback.message.edit_text(PersianTexts.ENTER_USER_SEARCH)


@router.message(AdminSubscriptionStates.searching_user)
async def search_user(message: Message, state: FSMContext):
    """Search for user."""
    query = message.text.strip()
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        users = user_repo.search_users(query)
        
        if not users:
            await message.reply(PersianTexts.USER_NOT_FOUND)
            return
        
        user = users[0]
        
        # Get user details
        tier = "رایگان"
        if user.is_subscription_active:
            tier = PersianTexts.TIER_PLUS if user.subscription_tier == "plus" else PersianTexts.TIER_PREMIUM
        
        from app.utils.jalali import format_jalali_date
        expiry = format_jalali_date(user.expiry_date) if user.expiry_date else "ندارد"
        referral_count = user_repo.get_referral_count(user.referral_code or "")
        
        text = PersianTexts.USER_DETAILS.format(
            name=f"ID: {user.tg_user_id}",
            user_id=user.tg_user_id,
            tier=tier,
            expiry=expiry,
            tokens=user.referral_tokens,
            downloads=user.total_downloads,
            referrals=referral_count
        )
        
        await message.reply(
            text,
            reply_markup=PersianKeyboards.user_management_actions(user.tg_user_id)
        )
        
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data.startswith("user_add_token_"))
async def add_user_tokens(callback: CallbackQuery, state: FSMContext):
    """Start adding tokens to user."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    user_id = int(callback.data.replace("user_add_token_", ""))
    admin_temp_data[callback.from_user.id] = {"target_user": user_id}
    
    await state.set_state(AdminSubscriptionStates.adding_user_tokens)
    await callback.answer()
    await callback.message.edit_text("تعداد توکن را وارد کنید:")


@router.message(AdminSubscriptionStates.adding_user_tokens)
async def receive_token_count(message: Message, state: FSMContext):
    """Receive token count and add to user."""
    try:
        tokens = int(message.text.strip())
        if tokens <= 0:
            raise ValueError()
    except ValueError:
        await message.reply("لطفاً یک عدد معتبر وارد کنید.")
        return
    
    admin_id = message.from_user.id
    data = admin_temp_data.get(admin_id, {})
    target_user_id = data.get("target_user")
    
    if not target_user_id:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        user = user_repo.get_user_by_tg_id(target_user_id)
        
        if not user:
            await message.reply(PersianTexts.USER_NOT_FOUND)
            return
        
        user.referral_tokens += tokens
        db.commit()
        
        await message.reply(f"✅ {tokens} توکن به کاربر {target_user_id} اضافه شد.")
        logger.info(f"Admin {admin_id} added {tokens} tokens to user {target_user_id}")
        
    finally:
        db.close()
        await state.clear()
        if admin_id in admin_temp_data:
            del admin_temp_data[admin_id]


# ============ EXTENDED STATISTICS ============

@router.callback_query(F.data == "admin_stats")
async def show_stats_menu(callback: CallbackQuery):
    """Show extended statistics menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.answer()
    await callback.message.edit_text(
        "📊 آمار و گزارشات",
        reply_markup=PersianKeyboards.stats_extended_menu()
    )


@router.callback_query(F.data == "stats_users")
async def show_user_stats(callback: CallbackQuery):
    """Show user statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        counts = user_repo.get_subscription_counts()
        
        new_today = user_repo.get_new_users_count(1)
        new_week = user_repo.get_new_users_count(7)
        new_month = user_repo.get_new_users_count(30)
        
        text = PersianTexts.STATS_USERS_REPORT.format(
            total=counts['total'],
            free=counts['free'],
            premium_active=counts['premium_active'],
            plus_active=counts['plus_active'],
            expired=counts['expired'],
            new_today=new_today,
            new_week=new_week,
            new_month=new_month
        )
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.stats_extended_menu()
        )
    finally:
        db.close()


@router.callback_query(F.data == "stats_sales")
async def show_sales_stats(callback: CallbackQuery):
    """Show sales statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        payment_repo = PaymentQueueRepository(db)
        
        total_revenue = payment_repo.get_total_revenue()
        approved_count = payment_repo.get_approved_count()
        pending_count = payment_repo.get_pending_count()
        
        today_revenue = payment_repo.get_total_revenue(1)
        week_revenue = payment_repo.get_total_revenue(7)
        month_revenue = payment_repo.get_total_revenue(30)
        
        text = PersianTexts.STATS_SALES_REPORT.format(
            total_revenue=total_revenue,
            approved_count=approved_count,
            pending_count=pending_count,
            today_revenue=today_revenue,
            week_revenue=week_revenue,
            month_revenue=month_revenue
        )
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.stats_extended_menu()
        )
    finally:
        db.close()


@router.callback_query(F.data == "stats_downloads")
async def show_download_stats(callback: CallbackQuery):
    """Show download statistics with top 10."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        from app.repo.download_history import DownloadHistoryRepository
        history_repo = DownloadHistoryRepository(db)
        
        total = history_repo.get_download_count()
        top_bundles = history_repo.get_top_bundles(10)
        
        # Format top list
        if top_bundles:
            emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
            top_list = "\n".join([
                f"{emojis[i]} {bundle.title[:30]} - {count} دانلود"
                for i, (bundle, count) in enumerate(top_bundles)
            ])
        else:
            top_list = "هنوز دانلودی ثبت نشده"
        
        text = PersianTexts.STATS_DOWNLOADS_REPORT.format(
            total=total,
            top_list=top_list
        )
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.stats_extended_menu()
        )
    finally:
        db.close()


@router.callback_query(F.data == "stats_bundles")
async def show_bundle_stats(callback: CallbackQuery):
    """Show bundle statistics."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    from app.repo.bundle import BundleRepository
    
    db = next(get_db())
    try:
        bundle_repo = BundleRepository(db)
        total = bundle_repo.get_bundle_count()
        
        # Count by access level
        from sqlalchemy import func
        from app.models.bundle import Bundle
        
        level_counts = db.query(
            Bundle.access_level, func.count(Bundle.id)
        ).group_by(Bundle.access_level).all()
        
        level_dict = {level: count for level, count in level_counts}
        
        text = f"""📄 آمار مستندات

📊 کل مستندات: {total}

سطح دسترسی:
🆓 رایگان: {level_dict.get('free', 0)}
💎 پریمیوم: {level_dict.get('premium', 0)}
⭐ پلاس: {level_dict.get('plus', 0)}"""
        
        await callback.answer()
        await callback.message.edit_text(
            text,
            reply_markup=PersianKeyboards.stats_extended_menu()
        )
    finally:
        db.close()


# ============ SCHEDULED BROADCAST ============

@router.callback_query(F.data == "admin_broadcast")
async def show_broadcast_menu(callback: CallbackQuery):
    """Show broadcast menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📤 پخش فوری", callback_data="broadcast_now")],
        [InlineKeyboardButton(text="⏰ پخش زمان‌بندی شده", callback_data="broadcast_schedule")],
        [InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")]
    ])
    
    await callback.answer()
    await callback.message.edit_text(
        "📢 مدیریت پیام همگانی\n\nنوع ارسال را انتخاب کنید:",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "broadcast_schedule")
async def start_scheduled_broadcast(callback: CallbackQuery, state: FSMContext):
    """Start scheduled broadcast flow."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await state.set_state(AdminSubscriptionStates.broadcast_message)
    await callback.answer()
    await callback.message.edit_text(
        "📝 پیام همگانی را ارسال کنید:\n\n(متن، عکس، ویدیو یا هر نوع پیام)"
    )


@router.message(AdminSubscriptionStates.broadcast_message)
async def receive_broadcast_message(message: Message, state: FSMContext):
    """Receive broadcast message."""
    admin_id = message.from_user.id
    
    # Store message info for broadcast
    admin_temp_data[admin_id] = {
        "broadcast_message_id": message.message_id,
        "broadcast_chat_id": message.chat.id
    }
    
    await state.set_state(AdminSubscriptionStates.broadcast_schedule_time)
    await message.reply(
        "⏰ زمان ارسال را مشخص کنید:\n\n"
        "فرمت: ساعت:دقیقه (مثال: 14:30)\n"
        "یا تعداد دقیقه تا ارسال (مثال: 60)"
    )


@router.message(AdminSubscriptionStates.broadcast_schedule_time)
async def schedule_broadcast(message: Message, state: FSMContext):
    """Schedule the broadcast."""
    admin_id = message.from_user.id
    time_input = message.text.strip()
    
    import re
    from datetime import datetime, timedelta
    
    # Parse time input
    if ":" in time_input:
        # Time format HH:MM
        match = re.match(r"(\d{1,2}):(\d{2})", time_input)
        if not match:
            await message.reply("فرمت نامعتبر. مثال: 14:30")
            return
        hour, minute = int(match.group(1)), int(match.group(2))
        now = datetime.now()
        scheduled_time = now.replace(hour=hour, minute=minute, second=0)
        if scheduled_time <= now:
            scheduled_time += timedelta(days=1)  # Schedule for tomorrow
    else:
        # Minutes from now
        try:
            minutes = int(time_input)
            if minutes <= 0:
                raise ValueError()
            scheduled_time = datetime.now() + timedelta(minutes=minutes)
        except ValueError:
            await message.reply("عدد نامعتبر. تعداد دقیقه را وارد کنید.")
            return
    
    data = admin_temp_data.get(admin_id, {})
    if not data:
        await message.reply(PersianTexts.ERROR_OCCURRED)
        await state.clear()
        return
    
    # Schedule broadcast job
    from app.jobs import get_scheduler
    scheduler = get_scheduler()
    
    if scheduler:
        job_id = f"broadcast_{admin_id}_{int(scheduled_time.timestamp())}"
        scheduler.add_job(
            _execute_broadcast,
            'date',
            run_date=scheduled_time,
            args=[message.bot, data["broadcast_chat_id"], data["broadcast_message_id"]],
            id=job_id
        )
        
        from app.utils.jalali import format_jalali_datetime
        formatted_time = format_jalali_datetime(int(scheduled_time.timestamp()))
        
        await message.reply(f"✅ پخش زمان‌بندی شد\n\n⏰ زمان: {formatted_time}")
        logger.info(f"Broadcast scheduled by {admin_id} for {scheduled_time}")
    else:
        await message.reply("خطا در زمان‌بندی. سرویس زمان‌بندی در دسترس نیست.")
    
    await state.clear()
    if admin_id in admin_temp_data:
        del admin_temp_data[admin_id]


async def _execute_broadcast(bot, chat_id: int, message_id: int):
    """Execute scheduled broadcast."""
    from app.repo.user import UserRepository
    from app.models.base import get_db
    
    db = next(get_db())
    try:
        user_repo = UserRepository(db)
        users = user_repo.get_all_users()
        
        success_count = 0
        for user in users:
            try:
                await bot.copy_message(
                    chat_id=user.tg_user_id,
                    from_chat_id=chat_id,
                    message_id=message_id
                )
                success_count += 1
            except Exception:
                pass
        
        logger.info(f"Scheduled broadcast completed: {success_count}/{len(users)} sent")
    finally:
        db.close()


# ============ OFFER MANAGEMENT ============

@router.callback_query(F.data == "admin_offers")
async def show_offers_menu(callback: CallbackQuery):
    """Show offers management menu."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    db = next(get_db())
    try:
        from app.repo.offer import OfferRepository
        offer_repo = OfferRepository(db)
        active_offers = offer_repo.get_active_offers()
        
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard_buttons = []
        
        # Show active offers
        if active_offers:
            text = "🎁 مدیریت آفرها\n\n📌 آفرهای فعال:\n"
            for offer in active_offers:
                text += f"• بسته {offer.bundle_id}: تا {offer.end_time}\n"
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"🔴 توقف آفر {offer.bundle_id}",
                        callback_data=f"offer_end_{offer.id}"
                    )
                ])
        else:
            text = "🎁 مدیریت آفرها\n\nهیچ آفر فعالی وجود ندارد."
        
        keyboard_buttons.append([
            InlineKeyboardButton(text="➕ ایجاد آفر جدید", callback_data="offer_create")
        ])
        keyboard_buttons.append([
            InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
        ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await callback.answer()
        await callback.message.edit_text(text, reply_markup=keyboard)
    finally:
        db.close()


@router.callback_query(F.data == "offer_create")
async def start_offer_creation(callback: CallbackQuery, state: FSMContext):
    """Start offer creation - ask for bundle search."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    await callback.answer()
    await callback.message.edit_text(
        "🔍 کد یا شماره بسته را وارد کنید:"
    )
    await state.set_state(AdminSubscriptionStates.offer_duration)


@router.message(AdminSubscriptionStates.offer_duration)
async def receive_offer_bundle(message: Message, state: FSMContext):
    """Receive bundle for offer and create it."""
    query = message.text.strip()
    
    db = next(get_db())
    try:
        from app.repo.bundle import BundleRepository
        from app.repo.offer import OfferRepository
        
        bundle_repo = BundleRepository(db)
        bundles = bundle_repo.search_bundles(query)
        
        if not bundles:
            await message.reply("بسته‌ای یافت نشد. دوباره تلاش کنید:")
            return
        
        bundle = bundles[0]
        
        # Create 24-hour offer
        offer_repo = OfferRepository(db)
        from datetime import datetime, timedelta
        
        end_time = datetime.now() + timedelta(hours=24)
        
        offer = offer_repo.create_offer_backup(
            bundle_id=bundle.id,
            original_level=bundle.access_level,
            end_time=end_time
        )
        
        # Change bundle to free
        bundle.access_level = "free"
        db.commit()
        
        from app.utils.jalali import format_jalali_datetime
        end_formatted = format_jalali_datetime(int(end_time.timestamp()))
        
        await message.reply(
            f"✅ آفر ایجاد شد!\n\n"
            f"📦 بسته: {bundle.title}\n"
            f"⏰ پایان: {end_formatted}\n\n"
            f"🆓 این بسته تا پایان آفر رایگان است."
        )
        logger.info(f"Offer created for bundle {bundle.id} until {end_time}")
        
    finally:
        db.close()
        await state.clear()


@router.callback_query(F.data.startswith("offer_end_"))
async def end_offer(callback: CallbackQuery):
    """End an active offer."""
    if not is_admin(callback.from_user.id):
        await callback.answer(PersianTexts.ACCESS_DENIED)
        return
    
    offer_id = int(callback.data.replace("offer_end_", ""))
    
    db = next(get_db())
    try:
        from app.repo.offer import OfferRepository
        from app.repo.bundle import BundleRepository
        
        offer_repo = OfferRepository(db)
        bundle_repo = BundleRepository(db)
        
        offer = offer_repo.get_offer_by_id(offer_id)
        if not offer:
            await callback.answer("آفر یافت نشد")
            return
        
        # Restore original access level
        bundle = bundle_repo.get_bundle_by_id(offer.bundle_id)
        if bundle:
            bundle.access_level = offer.original_level
        
        # Deactivate offer
        offer_repo.deactivate_offer(offer_id)
        
        await callback.answer("آفر متوقف شد ✅")
        logger.info(f"Offer {offer_id} ended by admin")
        
        # Refresh menu
        await show_offers_menu(callback)
        
    finally:
        db.close()

