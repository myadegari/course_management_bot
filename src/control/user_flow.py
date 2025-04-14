from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
import enum

from ..constants import BTN


class USER_CONTROL_FLOW(enum.Enum):
    EDIT_ACCOUNT = "EDIT_ACCOUNT_INFO"
    EDIT_FIRST_NAME = "EDIT_FIRST_NAME"
    EDIT_LAST_NAME = "EDIT_LAST_NAME"
    EDIT_NATIONAL_ID = "EDIT_NATIONAL_ID"


def account_info_keyboard_flow():
    account_buttons = InlineKeyboardMarkup()
    account_buttons.row(
        InlineKeyboardButton("ویرایش اطلاعات", callback_data=USER_CONTROL_FLOW.EDIT_ACCOUNT.value)
    )
    return account_buttons


def account_info_edit_keyboard_flow():
    account_buttons = InlineKeyboardMarkup()
    buttons = (
        InlineKeyboardButton("نام", callback_data=USER_CONTROL_FLOW.EDIT_FIRST_NAME.value),
        InlineKeyboardButton("نام خانوادگی", callback_data=USER_CONTROL_FLOW.EDIT_LAST_NAME.value),
        InlineKeyboardButton("کد ملی", callback_data=USER_CONTROL_FLOW.EDIT_NATIONAL_ID.value),
    )
    for button in buttons:
        account_buttons.row(button)
    return account_buttons


def register_user_data(bot, message):
    bot.send_message(
        message.from_user.id,
        "لطفا اطلاعات خود را کامل کنید",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("اطلاعات حساب", callback_data="ACCOUNT_INFO")
        ),
    )


def main_keyboard_flow():
    main_buttons = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    main_buttons.add(KeyboardButton(BTN.USER_MAIN_MENU.SHOW_COURSES))
    main_buttons.add(KeyboardButton(BTN.USER_MAIN_MENU.MY_COURSES))
    main_buttons.add(
        KeyboardButton(BTN.USER_MAIN_MENU.ACCOUNT_INFO),
        KeyboardButton(BTN.USER_MAIN_MENU.CERTIFICATE),
    )
    return main_buttons


def admin_keyboard_flow():
    main_buttons = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    main_buttons.add(KeyboardButton(BTN.ADMIN_MAIN_MENU.SHOW_COURSES))
    main_buttons.add(KeyboardButton(BTN.ADMIN_MAIN_MENU.ADD_COURSE),
                     KeyboardButton(BTN.ADMIN_MAIN_MENU.EDIT_COURSE),
                     KeyboardButton(BTN.ADMIN_MAIN_MENU.DELETE_COURSE),
                     )
    main_buttons.add(
        KeyboardButton(BTN.ADMIN_MAIN_MENU.SHOW_USERS),
        KeyboardButton(BTN.ADMIN_MAIN_MENU.SHOW_CERTIFICATES),
    )
    main_buttons.add(
        KeyboardButton(BTN.ADMIN_MAIN_MENU.SEND_MESSAGE),
        KeyboardButton(BTN.ADMIN_MAIN_MENU.ACCOUNT_INFO),
    )
    return main_buttons
