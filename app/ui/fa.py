"""Persian UI texts and keyboards."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional


class PersianTexts:
    """Persian text constants."""
    
    # General
    BACK = "🔙 بازگشت"
    CANCEL = "❌ لغو"
    CONFIRM = "✅ تأیید"
    DELETE = "🗑 حذف"
    EDIT = "✏️ ویرایش"
    
    # User flow
    WELCOME = "خوش آمدید! 🌟"
    INVALID_CODE = "کد وارد شده نامعتبر یا غیرفعال است. ❌"
    JOIN_REQUIRED = "برای دریافت محتوا، ابتدا باید در کانال‌های زیر عضو شوید:"
    JOIN_CHECK = "✅ جوین شدم"
    PLEASE_JOIN_ALL = "لطفاً در تمام کانال‌ها عضو شوید و دوباره تلاش کنید."
    CONTENT_DELIVERED = "محتوا با موفقیت ارسال شد! 📤"
    DOWNLOAD_AGAIN = "دانلود دوباره"
    
    # Admin panel
    ADMIN_WELCOME = "پنل مدیریت 👨‍💼"
    BUNDLES_MENU = "📦 مدیریت بسته‌ها"
    CHANNELS_MENU = "📢 کانال‌های اجباری"
    MESSAGES_MENU = "💬 پیام‌های سیستم"
    REQUESTS_MENU = "📝 درخواست‌های کاربران"
    BROADCAST_MENU = "📡 ارسال همگانی"
    BACKUP_MENU = "💾 پشتیبان‌گیری"
    STATS_MENU = "📊 آمار"
    
    # Bundle management
    BUNDLE_CREATED = "بسته جدید ایجاد شد! 🎉\n\n📦 شماره: {number}\n📝 عنوان: {title}\n🔗 لینک: {link}"
    ENTER_BUNDLE_TITLE = "عنوان بسته را وارد کنید:"
    RECORDING_STARTED = "ضبط شروع شد! پیام‌های خود را ارسال کنید و در پایان /done را بزنید."
    RECORDING_STOPPED = "ضبط متوقف شد."
    BUNDLE_SEARCH = "جستجوی بسته (کد/شماره/عنوان):"
    NO_BUNDLES_FOUND = "هیچ بسته‌ای یافت نشد."
    BUNDLE_ACTIVATED = "بسته فعال شد ✅"
    BUNDLE_DEACTIVATED = "بسته غیرفعال شد ❌"
    
    # Channel management
    ADD_CHANNEL = "➕ افزودن کانال"
    CHANNEL_LIST = "📋 لیست کانال‌ها"
    ENTER_CHANNEL_LINK = "لینک کانال را وارد کنید (t.me/username یا t.me/+invite یا ID):"
    CHANNEL_ADDED = "کانال با موفقیت اضافه شد ✅"
    CHANNEL_REMOVED = "کانال حذف شد ❌"
    INVALID_CHANNEL_LINK = "لینک کانال نامعتبر است."
    NO_CHANNELS = "هیچ کانالی تعریف نشده است."
    
    # Messages
    STARTING_MESSAGE = "پیام شروع"
    ENDING_MESSAGES = "پیام‌های پایان"
    SET_STARTING_MSG = "پیام شروع جدید را ارسال کنید:"
    STARTING_MSG_SET = "پیام شروع تنظیم شد ✅"
    ADD_ENDING_MSG = "➕ افزودن پیام پایان"
    ENDING_MSG_LIST = "📋 لیست پیام‌های پایان"
    ENTER_ENDING_NAME = "نام کوتاه برای پیام پایان وارد کنید:"
    SEND_ENDING_MSG = "پیام پایان را ارسال کنید:"
    ENDING_MSG_ADDED = "پیام پایان اضافه شد ✅"
    ENDING_MSG_DELETED = "پیام پایان حذف شد ❌"
    NO_ENDING_MESSAGES = "هیچ پیام پایانی تعریف نشده است."
    
    # Requests
    SUBMIT_REQUEST = "📝 ثبت درخواست"
    ENTER_REQUEST = "متن درخواست خود را وارد کنید:"
    REQUEST_SUBMITTED = "درخواست شما ثبت شد ✅"
    NO_REQUESTS = "هیچ درخواستی وجود ندارد."
    REQUEST_RESOLVED = "درخواست حل شد ✅"
    
    # Broadcast
    SEND_BROADCAST = "پیام همگانی را ارسال کنید:"
    BROADCAST_PREVIEW = "پیش‌نمایش پیام همگانی:\n\n{message}\n\n👥 تعداد کاربران: {count}"
    SEND_BROADCAST_BTN = "📤 ارسال"
    BROADCAST_CANCELLED = "ارسال همگانی لغو شد."
    BROADCAST_STARTED = "ارسال همگانی شروع شد..."
    BROADCAST_COMPLETED = "ارسال همگانی تکمیل شد!\n\n✅ موفق: {success}\n❌ ناموفق: {failed}"
    
    # Backup
    RUN_BACKUP = "▶️ اجرای پشتیبان‌گیری"
    BACKUP_STARTED = "پشتیبان‌گیری شروع شد..."
    BACKUP_COMPLETED = "پشتیبان‌گیری کامل شد ✅"
    BACKUP_FAILED = "پشتیبان‌گیری با خطا مواجه شد ❌"
    
    # Statistics
    STATS_WEEKLY = "📅 هفتگی"
    STATS_MONTHLY = "📅 ماهانه"
    STATS_TOTAL = "📅 کل زمان"
    
    STATS_WEEKLY_REPORT = """📊 آمار هفته گذشته (۷ روز):

📥 تعداد دانلود: {downloads}
👥 کاربران فعال: {active_users}
🏆 پربازدیدترین بسته: {top_bundle}"""

    STATS_MONTHLY_REPORT = """📊 آمار ماه گذشته (۳۰ روز):

📥 تعداد دانلود: {downloads}
👥 کاربران فعال: {active_users}
🏆 پربازدیدترین بسته: {top_bundle}"""

    STATS_TOTAL_REPORT = """📊 آمار کل:

📥 تعداد دانلود: {downloads}
👥 کل کاربران: {total_users}
📦 کل بسته‌ها: {total_bundles}
🏆 پربازدیدترین بسته: {top_bundle}"""

    # Errors
    ERROR_OCCURRED = "خطایی رخ داد. لطفاً دوباره تلاش کنید."
    ACCESS_DENIED = "دسترسی مجاز نیست."
    INVALID_INPUT = "ورودی نامعتبر است."
    
    # =============================================
    # SUBSCRIPTION SYSTEM TEXTS
    # =============================================
    
    # User Menu Buttons
    BTN_GET_TOKEN = "🎁 دریافت توکن"
    BTN_BUY_SUBSCRIPTION = "💳 خرید اشتراک"
    BTN_MY_STATUS = "📊 وضعیت اشتراک من"
    BTN_SUPPORT = "💬 پشتیبانی"
    
    # Welcome Message (Updated)
    WELCOME_NEW = """👋 سلام {first_name}!

به بات مستندات علمی خوش آمدید 🌟

🎁 شما 3 توکن دانلود رایگان دارید!
💡 با دعوت دوستان، توکن بیشتری کسب کنید"""

    WELCOME_REFERRAL = """👋 سلام {first_name}!

🎉 از طرف دوستتان دعوت شدید!

🎁 شما 3 توکن دانلود رایگان دارید!
✨ دوست شما 1 توکن دریافت کرد"""

    # Status Screen
    STATUS_SCREEN = """👤 وضعیت حساب شما

🎯 نوع اشتراک: {tier_name}
⏰ اعتبار تا: {expiry_date}
🪙 توکن‌های شما: {tokens} عدد
📥 کل دانلودها: {total_downloads}
👥 دعوت شده‌ها: {referral_count} نفر"""

    TIER_FREE = "رایگان"
    TIER_PREMIUM = "💎 پریمیوم"
    TIER_PLUS = "⭐ پلاس"
    NO_EXPIRY = "ندارد"
    
    # Token System
    TOKEN_SCREEN = """🎁 سیستم توکن رایگان

🪙 توکن‌های شما: {tokens}

💡 هر توکن = 1 دانلود مستند پریمیوم

🔗 لینک دعوت شما:
{referral_link}

کد اختصاصی: {referral_code}

با دعوت هر نفر، 1 توکن دریافت کنید! 🎉"""

    # Subscription Purchase
    SUBSCRIPTION_MENU = "💳 انتخاب پلن اشتراک"
    
    PLAN_DETAILS = """📦 {plan_name}
⏱️ مدت: {duration} روز
💰 قیمت: {price} تومان

✨ مزایا:
{benefits}"""

    BENEFITS_PREMIUM = """• دسترسی به تمام مستندات پریمیوم
• دانلود نامحدود
• به‌روزرسانی‌های منظم"""

    BENEFITS_PLUS = """• تمام مزایای پریمیوم
• دسترسی به محتوای VIP و پلاس
• اولویت پشتیبانی"""

    PAYMENT_DETAILS = """💳 مشخصات پرداخت

📦 پلن: {plan_name}
⏱️ مدت: {duration} روز
💰 مبلغ: {price} تومان

━━━━━━━━━━━━━━━━

🏦 کارت مقصد:
{card_number}
به نام: {card_holder}

پس از واریز، رسید خود را ارسال کنید."""

    SEND_SCREENSHOT = "📸 لطفاً تصویر رسید پرداخت را ارسال کنید:"
    PAYMENT_SUBMITTED = "✅ رسید شما دریافت شد و در حال بررسی است..."
    PAYMENT_PENDING = "⏳ شما یک پرداخت در حال بررسی دارید. لطفاً صبر کنید."
    
    PAYMENT_APPROVED = """🎉 اشتراک شما فعال شد!

📦 پلن: {plan_name}
⏱️ مدت: {duration} روز
📅 اعتبار تا: {expiry_date}

از خریدتان متشکریم! ✨"""

    PAYMENT_REJECTED = """❌ مشکلی در رسید شما وجود دارد.

لطفاً با پشتیبانی تماس بگیرید:
@{support_username}"""

    # Support Menu
    SUPPORT_MENU = "💬 پشتیبانی"
    SUPPORT_GUIDE = "📖 راهنمای اشتراک‌ها"
    SUPPORT_REQUEST = "📝 درخواست مستند"
    SUPPORT_CONTACT = "💭 بررسی فعالسازی و سایر سوالات"
    
    SUBSCRIPTION_GUIDE = """📚 راهنمای سیستم اشتراک

🆓 رایگان:
• دسترسی به مستندات رایگان
• 3 توکن هدیه اولیه

💎 پریمیوم:
• دسترسی به تمام مستندات پریمیوم
• دانلود نامحدود
• به‌روزرسانی‌های منظم

⭐ پلاس:
• تمام مزایای پریمیوم
• دسترسی به محتوای VIP
• اولویت پشتیبانی"""

    REQUEST_DOC_PROMPT = "📝 لطفاً نام یا توضیحات مستند مورد نظر را ارسال کنید:"
    REQUEST_DOC_SUBMITTED = "✅ درخواست شما ثبت شد. تیم پشتیبانی به زودی بررسی می‌کند."
    
    # File Delivery
    FILE_DELIVERY = """📄 {doc_name}

⚠️ فایل تا ۱۸۰ ثانیه دیگر پاک می‌شود.
آن را در Saved Messages ذخیره کنید."""

    TOKEN_WARNING = "\n\n⚠️ این آخرین توکن دانلود رایگان شماست. برای دانلود مستند جدید اشتراک تهیه کنید یا توکن دریافت کنید."
    
    # Access Denied Messages
    NEED_SUBSCRIPTION = """💎 توکن رایگان شما تمام شده است.

برای دانلود این مستند:
• اشتراک تهیه کنید
• یا با دعوت دوستان توکن دریافت کنید"""

    NEED_PLUS = """⭐ این محتوا فقط برای کاربران پلاس در دسترس است.

برای دسترسی، اشتراک پلاس تهیه کنید."""

    # Admin Texts
    ADMIN_PLANS_MENU = "💎 مدیریت پلن‌های اشتراک"
    ADMIN_PAYMENTS_MENU = "📸 تایید پرداخت‌ها"
    ADMIN_USERS_MENU = "👥 مدیریت کاربران"
    ADMIN_OFFERS_MENU = "🎁 آفرهای ویژه"
    
    PAYMENT_QUEUE_ITEM = """📸 رسید پرداخت (#{index} از {total})

👤 کاربر: {username} (ID: {user_id})
📦 پلن: {plan_name}
💰 مبلغ: {price} تومان
⏰ زمان: {submitted_at}"""

    PAYMENT_QUEUE_EMPTY = "✅ هیچ پرداختی در صف تایید نیست."
    PAYMENT_QUEUE_ALERT = "⚠️ {count} پرداخت در صف تایید"
    
    PLAN_ADDED = "✅ پلن \"{name}\" با قیمت {price} تومان اضافه شد."
    PLAN_UPDATED = "✅ پلن به‌روزرسانی شد."
    PLAN_STATUS_CHANGED = "وضعیت پلن تغییر کرد."
    
    ENTER_PLAN_NAME = "📝 نام پلن را وارد کنید:\nمثال: 15 روزه پریمیوم تخفیفی"
    ENTER_PLAN_DAYS = "📅 مدت زمان را به روز وارد کنید:\nمثال: 15"
    SELECT_PLAN_TIER = "🎯 نوع اشتراک را انتخاب کنید:"
    ENTER_PLAN_PRICE = "💰 قیمت را به تومان وارد کنید:\nمثال: 25000"
    
    SELECT_ACCESS_LEVEL = "🔒 سطح دسترسی را انتخاب کنید:"
    ACCESS_FREE = "🆓 رایگان"
    ACCESS_PREMIUM = "💎 پریمیوم"
    ACCESS_PLUS = "⭐ پلاس"
    
    USER_DETAILS = """👤 {name}
🆔 ID: {user_id}

📊 وضعیت:
🎯 اشتراک: {tier}
⏰ اعتبار: {expiry}
🪙 توکن: {tokens}
📥 دانلودها: {downloads}
👥 دعوت‌ها: {referrals}"""

    USER_NOT_FOUND = "❌ کاربر یافت نشد."
    ENTER_USER_SEARCH = "🔍 ID یا کد معرف کاربر را وارد کنید:"
    
    # Statistics (Extended)
    STATS_USERS_REPORT = """👥 آمار کاربران

📈 کل کاربران: {total:,}
🆓 رایگان: {free:,}
💎 پریمیوم فعال: {premium_active:,}
⭐ پلاس فعال: {plus_active:,}
⏰ منقضی شده: {expired:,}

امروز: +{new_today}
این هفته: +{new_week}
این ماه: +{new_month}"""

    STATS_DOWNLOADS_REPORT = """📥 آمار دانلودها

📊 کل دانلودها: {total:,}

🔝 پرطرفدارترین مستندات:
{top_list}"""

    STATS_SALES_REPORT = """💰 آمار فروش

📊 کل فروش: {total_revenue:,} تومان
✅ تایید شده: {approved_count} پرداخت
⏳ در انتظار: {pending_count} پرداخت

امروز: {today_revenue:,} ت
این هفته: {week_revenue:,} ت
این ماه: {month_revenue:,} ت"""

    DIFFERENCE_PREMIUM_PLUS = "❓ تفاوت پریمیوم و پلاس"
    
    SELECT_ACCESS_LEVEL = "🔒 سطح دسترسی بسته را انتخاب کنید:"


class PersianKeyboards:
    """Persian keyboard layouts."""
    
    @staticmethod
    def admin_main() -> InlineKeyboardMarkup:
        """Main admin panel keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.BUNDLES_MENU, callback_data="admin_bundles"),
                InlineKeyboardButton(text=PersianTexts.CHANNELS_MENU, callback_data="admin_channels")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.MESSAGES_MENU, callback_data="admin_messages"),
                InlineKeyboardButton(text=PersianTexts.REQUESTS_MENU, callback_data="admin_requests")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BROADCAST_MENU, callback_data="admin_broadcast"),
                InlineKeyboardButton(text=PersianTexts.BACKUP_MENU, callback_data="admin_backup")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.STATS_MENU, callback_data="admin_stats")
            ]
        ])
    
    @staticmethod
    def bundles_menu() -> InlineKeyboardMarkup:
        """Bundle management keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔍 جستجو", callback_data="bundle_search"),
                InlineKeyboardButton(text="📋 لیست همه", callback_data="bundle_list")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
            ]
        ])
    
    @staticmethod
    def channels_menu() -> InlineKeyboardMarkup:
        """Channels management keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.ADD_CHANNEL, callback_data="channel_add"),
                InlineKeyboardButton(text=PersianTexts.CHANNEL_LIST, callback_data="channel_list")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
            ]
        ])
    
    @staticmethod
    def messages_menu() -> InlineKeyboardMarkup:
        """Messages management keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.STARTING_MESSAGE, callback_data="msg_starting"),
                InlineKeyboardButton(text=PersianTexts.ENDING_MESSAGES, callback_data="msg_ending")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
            ]
        ])
    
    @staticmethod
    def ending_messages_menu() -> InlineKeyboardMarkup:
        """Ending messages menu keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.ADD_ENDING_MSG, callback_data="ending_add"),
                InlineKeyboardButton(text=PersianTexts.ENDING_MSG_LIST, callback_data="ending_list")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_messages")
            ]
        ])
    
    @staticmethod
    def stats_menu() -> InlineKeyboardMarkup:
        """Statistics menu keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.STATS_WEEKLY, callback_data="stats_weekly"),
                InlineKeyboardButton(text=PersianTexts.STATS_MONTHLY, callback_data="stats_monthly")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.STATS_TOTAL, callback_data="stats_total")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
            ]
        ])
    
    @staticmethod
    def backup_menu() -> InlineKeyboardMarkup:
        """Backup menu keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.RUN_BACKUP, callback_data="backup_run")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
            ]
        ])
    
    @staticmethod
    def join_check() -> InlineKeyboardMarkup:
        """Join check keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.JOIN_CHECK, callback_data="join_check")
            ]
        ])
    
    @staticmethod
    def join_channels(channels: List[dict]) -> InlineKeyboardMarkup:
        """Create keyboard with channel join buttons."""
        keyboard = []
        for channel in channels:
            join_link = channel.get('join_link')
            if not join_link and channel.get('username'):
                join_link = f"https://t.me/{channel['username']}"
            
            if join_link:
                keyboard.append([
                    InlineKeyboardButton(
                        text=channel['title'], 
                        url=join_link
                    )
                ])
            else:
                # If no link available, show channel title without URL
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"📢 {channel['title']}", 
                        callback_data=f"no_link_{channel.get('id', 0)}"
                    )
                ])
        
        keyboard.append([
            InlineKeyboardButton(text=PersianTexts.JOIN_CHECK, callback_data="join_check")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def broadcast_confirm(count: int) -> InlineKeyboardMarkup:
        """Broadcast confirmation keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.SEND_BROADCAST_BTN, callback_data="broadcast_send"),
                InlineKeyboardButton(text=PersianTexts.CANCEL, callback_data="broadcast_cancel")
            ]
        ])
    
    @staticmethod
    def bundle_actions(bundle_id: int, is_active: bool) -> InlineKeyboardMarkup:
        """Bundle action buttons."""
        status_text = "❌ غیرفعال کردن" if is_active else "✅ فعال کردن"
        status_action = "deactivate" if is_active else "activate"
        
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 کپی لینک", callback_data=f"bundle_copy_{bundle_id}"),
                InlineKeyboardButton(text=status_text, callback_data=f"bundle_{status_action}_{bundle_id}")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_bundles")
            ]
        ])
    
    @staticmethod
    def channel_actions(channel_id: int) -> InlineKeyboardMarkup:
        """Channel action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.DELETE, callback_data=f"channel_delete_{channel_id}")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_channels")
            ]
        ])
    
    @staticmethod
    def request_actions(request_id: int) -> InlineKeyboardMarkup:
        """Request action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ حل شد", callback_data=f"request_resolve_{request_id}")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_requests")
            ]
        ])
    
    @staticmethod
    def user_main() -> ReplyKeyboardMarkup:
        """User main menu keyboard with subscription options."""
        return ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=PersianTexts.BTN_GET_TOKEN),
                    KeyboardButton(text=PersianTexts.BTN_BUY_SUBSCRIPTION)
                ],
                [
                    KeyboardButton(text=PersianTexts.BTN_MY_STATUS),
                    KeyboardButton(text=PersianTexts.BTN_SUPPORT)
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    @staticmethod
    def status_actions() -> InlineKeyboardMarkup:
        """Status screen action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 تمدید اشتراک", callback_data="sub_renew"),
                InlineKeyboardButton(text="🎁 دعوت دوستان", callback_data="sub_invite")
            ]
        ])
    
    @staticmethod
    def token_actions() -> InlineKeyboardMarkup:
        """Token screen action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📋 کپی لینک", callback_data="copy_referral"),
                InlineKeyboardButton(text="📊 آمار دعوت‌ها", callback_data="referral_stats")
            ]
        ])
    
    @staticmethod
    def subscription_plans(plans: list) -> InlineKeyboardMarkup:
        """Dynamic subscription plans keyboard."""
        keyboard = []
        for plan in plans:
            price_formatted = f"{plan.price:,}"
            button_text = f"{plan.plan_name} - {price_formatted} ت"
            keyboard.append([
                InlineKeyboardButton(text=button_text, callback_data=f"plan_{plan.plan_id}")
            ])
        
        # Add help button
        keyboard.append([
            InlineKeyboardButton(text=PersianTexts.DIFFERENCE_PREMIUM_PLUS, callback_data="plan_difference")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def plan_confirmation(plan_id: str) -> InlineKeyboardMarkup:
        """Plan confirmation keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="💳 خرید این پلن", callback_data=f"buy_{plan_id}"),
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="sub_menu")
            ]
        ])
    
    @staticmethod
    def payment_actions() -> InlineKeyboardMarkup:
        """Payment screen actions."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📸 ارسال رسید", callback_data="send_receipt"),
                InlineKeyboardButton(text=PersianTexts.CANCEL, callback_data="cancel_payment")
            ]
        ])
    
    @staticmethod
    def support_menu() -> InlineKeyboardMarkup:
        """Support menu keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=PersianTexts.SUPPORT_GUIDE, callback_data="support_guide")],
            [InlineKeyboardButton(text=PersianTexts.SUPPORT_REQUEST, callback_data="support_request")],
            [InlineKeyboardButton(text=PersianTexts.SUPPORT_CONTACT, callback_data="support_contact")]
        ])
    
    @staticmethod
    def support_understood() -> InlineKeyboardMarkup:
        """Support guide understood button."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="متوجه شدم ✅", callback_data="support_back")]
        ])
    
    @staticmethod
    def redownload_button(bundle_code: str) -> InlineKeyboardMarkup:
        """Re-download button for file delivery."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 دانلود مجدد", callback_data=f"redownload_{bundle_code}")]
        ])
    
    @staticmethod
    def access_denied_buttons() -> InlineKeyboardMarkup:
        """Access denied action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.BTN_BUY_SUBSCRIPTION, callback_data="sub_menu"),
                InlineKeyboardButton(text=PersianTexts.BTN_GET_TOKEN, callback_data="get_token")
            ]
        ])
    
    # ============ ADMIN KEYBOARDS ============
    
    @staticmethod
    def admin_main_extended() -> InlineKeyboardMarkup:
        """Extended admin main panel with subscription features."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.BUNDLES_MENU, callback_data="admin_bundles"),
                InlineKeyboardButton(text=PersianTexts.CHANNELS_MENU, callback_data="admin_channels")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.ADMIN_PLANS_MENU, callback_data="admin_plans"),
                InlineKeyboardButton(text=PersianTexts.ADMIN_PAYMENTS_MENU, callback_data="admin_payments")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.ADMIN_USERS_MENU, callback_data="admin_users"),
                InlineKeyboardButton(text=PersianTexts.ADMIN_OFFERS_MENU, callback_data="admin_offers")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.STATS_MENU, callback_data="admin_stats"),
                InlineKeyboardButton(text=PersianTexts.BROADCAST_MENU, callback_data="admin_broadcast")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.MESSAGES_MENU, callback_data="admin_messages"),
                InlineKeyboardButton(text=PersianTexts.BACKUP_MENU, callback_data="admin_backup")
            ]
        ])
    
    @staticmethod
    def plans_management(plans: list) -> InlineKeyboardMarkup:
        """Plans management keyboard."""
        keyboard = []
        for plan in plans:
            status_emoji = "✅" if plan.is_active else "❌"
            keyboard.append([
                InlineKeyboardButton(
                    text=f"{status_emoji} {plan.plan_name} - {plan.price:,} ت",
                    callback_data=f"plan_edit_{plan.id}"
                )
            ])
        
        keyboard.append([
            InlineKeyboardButton(text="➕ افزودن پلن جدید", callback_data="plan_add")
        ])
        keyboard.append([
            InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def plan_edit_actions(plan_id: int, is_active: bool) -> InlineKeyboardMarkup:
        """Plan edit action buttons."""
        toggle_text = "🔴 غیرفعال کردن" if is_active else "🟢 فعال کردن"
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✏️ ویرایش", callback_data=f"plan_modify_{plan_id}"),
                InlineKeyboardButton(text=toggle_text, callback_data=f"plan_toggle_{plan_id}")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_plans")
            ]
        ])
    
    @staticmethod
    def tier_selection() -> InlineKeyboardMarkup:
        """Tier selection for new plan."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=PersianTexts.ACCESS_PREMIUM, callback_data="tier_premium"),
                InlineKeyboardButton(text=PersianTexts.ACCESS_PLUS, callback_data="tier_plus")
            ]
        ])
    
    @staticmethod
    def access_level_selection() -> InlineKeyboardMarkup:
        """Access level selection for bundle."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=PersianTexts.ACCESS_FREE, callback_data="level_free")],
            [InlineKeyboardButton(text=PersianTexts.ACCESS_PREMIUM, callback_data="level_premium")],
            [InlineKeyboardButton(text=PersianTexts.ACCESS_PLUS, callback_data="level_plus")]
        ])
    
    @staticmethod
    def payment_verification(payment_id: int, has_next: bool = False) -> InlineKeyboardMarkup:
        """Payment verification action buttons."""
        keyboard = [
            [InlineKeyboardButton(text="🖼️ مشاهده رسید", callback_data=f"pay_view_{payment_id}")],
            [
                InlineKeyboardButton(text="✅ تایید", callback_data=f"pay_approve_{payment_id}"),
                InlineKeyboardButton(text="❌ خطا", callback_data=f"pay_reject_{payment_id}")
            ]
        ]
        if has_next:
            keyboard.append([
                InlineKeyboardButton(text="⏭️ بعدی", callback_data="pay_next")
            ])
        
        keyboard.append([
            InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_payments")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def user_management_actions(user_id: int) -> InlineKeyboardMarkup:
        """User management action buttons."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="➕ افزودن اشتراک", callback_data=f"user_add_sub_{user_id}"),
                InlineKeyboardButton(text="🎁 اهدای توکن", callback_data=f"user_add_token_{user_id}")
            ],
            [
                InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_users")
            ]
        ])
    
    @staticmethod
    def stats_extended_menu() -> InlineKeyboardMarkup:
        """Extended statistics menu."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👥 آمار کاربران", callback_data="stats_users")],
            [InlineKeyboardButton(text="📥 آمار دانلودها", callback_data="stats_downloads")],
            [InlineKeyboardButton(text="💰 آمار فروش", callback_data="stats_sales")],
            [InlineKeyboardButton(text="📄 آمار مستندات", callback_data="stats_bundles")],
            [InlineKeyboardButton(text=PersianTexts.BACK, callback_data="admin_main")]
        ])

