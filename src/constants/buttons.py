from dataclasses import dataclass
from typing import Final

@dataclass(frozen=True)
class UserMainMenu:
    SHOW_COURSES: Final[str] = "📚 نمایش دوره های مرکز آموزش"
    MY_COURSES: Final[str] = "📙 دوره های ثبت نام شده"
    CERTIFICATE: Final[str] = "🏆 دریافت گواهینامه"
    ACCOUNT_INFO: Final[str] = "🧐 اطلاعات حساب کاربری"

@dataclass(frozen=True)
class AdminMainMenu:
    SHOW_COURSES: Final[str] = "📚 نمایش دوره های مرکز آموزش"
    ADD_COURSE: Final[str] = "➕ افزودن دوره"
    EDIT_COURSE: Final[str] = "✏️ ویرایش دوره"
    DELETE_COURSE: Final[str] = "❌ حذف دوره"
    SHOW_USERS: Final[str] = "👥 نمایش کاربران"
    SHOW_CERTIFICATES: Final[str] = "🏆 نمایش گواهینامه ها"
    SEND_MESSAGE: Final[str] = "📩 ارسال پیام به کاربران"
    ACCOUNT_INFO: Final[str] = "🧐 اطلاعات حساب کاربری"

# Create singleton instances
USER_MAIN_MENU = UserMainMenu()
ADMIN_MAIN_MENU = AdminMainMenu()