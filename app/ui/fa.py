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
        """User main menu keyboard."""
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=PersianTexts.SUBMIT_REQUEST)]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
