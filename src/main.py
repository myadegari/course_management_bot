#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import logging
import os
import pathlib
import re
from xmlrpc.client import boolean
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

import telebot
from dotenv import load_dotenv

# from repositories.utils import get_db
from sqlalchemy.orm import Session

from src.utils import jalali

from .constants import BTN, MSG
from .control import USER_CONTROL_FLOW, user_flow
from .repositories import crud, models
from .repositories.database import engine
from .repositories.utils import get_db
from .utils.dependency import Dependency, inject

models.Base.metadata.create_all(bind=engine)


BASE_DIR = pathlib.Path(__file__).parent.absolute()
load_dotenv(BASE_DIR / ".env")

bot_token = os.getenv("BOT_TOKEN")
if not bot_token:
    raise ValueError("BOT_TOKEN not found in environment variables")
bot = telebot.TeleBot(bot_token)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log",
)


@bot.message_handler(commands=["start"])
@inject
def send_welcome(message: telebot.types.Message, db: Session = Dependency(get_db)):
    try:
        user: crud.Users | None = crud.get_user_by_bale_id(
            db, bale_id=str(message.from_user.id)
        )

        if not user:
            new_user = models.Users(
                bale_id=str(message.from_user.id),
                bale_username=message.from_user.full_name,
            )
            crud.make_new_user(db, new_user)
            user_flow.register_user_data(bot, message)
            return

        if user.role == models.UserRole.USER:
            if not any((user.first_name, user.last_name, user.national_id)):
                user_flow.register_user_data(bot, message)

            else:
                bot.send_message(
                    message.from_user.id,
                    MSG.GREATING(user),
                    reply_markup=user_flow.main_keyboard_flow(),
                )

        elif user.role == models.UserRole.ADMIN:
            bot.send_message(
                message.from_user.id,
                MSG.ADMIN_GREETING(user),
                reply_markup=user_flow.admin_keyboard_flow(),
            )

    except Exception as e:
        bot.reply_to(message, MSG.ERRORS["GENERAL_ERROR"])
        logging.error(f"[USER-{message.from_user.id}] Error in send_welcome: {e}")


# @bot.pre_checkout_query_handler(func=lambda query: True)
# @inject
# def process_pre_checkout_query(pre_checkout_query: telebot.types.PreCheckoutQuery, db: Session = Dependency(get_db)):
#     ...


def process_account_info_step_1(
    message: telebot.types.Message, db: Session, single: boolean = False
):
    try:
        user: models.Users | None = crud.get_user_by_bale_id(
            db, bale_id=str(message.from_user.id)
        )
        if not user:
            bot.reply_to(message, MSG.ERRORS["USER_NOT_FOUND"])
            logging.error(f"[USER-{message.from_user.id}] User not found in database.")
            return

        cleaned = re.sub(r"[0-9\W_]+", " ", message.text.strip(), flags=re.UNICODE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned or len(cleaned) < 2:  # Added minimum length check
            logging.error(
                f"[USER-{message.from_user.id}] Invalid input: {message.text}"
            )
            msg = bot.reply_to(message, MSG.ERRORS["INVALID_FIRST_NAME"])
            bot.register_next_step_handler(msg, process_account_info_step_1, db)
            return

        user.first_name = cleaned
        db.add(user)  # Explicitly add the user object
        if single:
            db.commit()
            bot.reply_to(message, MSG.USER["ACCOUNT_INFO"]["COMPLETE"])
            return
        msg = bot.reply_to(message, MSG.USER["ACCOUNT_INFO"]["LAST_NAME"])
        bot.register_next_step_handler(msg, process_account_info_step_2, user, db)

    except Exception as e:
        bot.reply_to(message, MSG.ERRORS["GENERAL_ERROR"])
        logging.error(
            f"[USER-{message.from_user.id}] Error in process_account_info_step_1: {str(e)}"
        )
        db.rollback()


def process_account_info_step_2(
    message: telebot.types.Message,
    user: models.Users,
    db: Session,
    single: boolean = False,
):
    try:
        cleaned = re.sub(r"[0-9\W_]+", " ", message.text.strip(), flags=re.UNICODE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if not cleaned or len(cleaned) < 2:  # Added minimum length check
            logging.error(
                f"[USER-{message.from_user.id}] Invalid input: {message.text}"
            )
            msg = bot.reply_to(message, MSG.ERRORS["INVALID_LAST_NAME"])
            bot.register_next_step_handler(msg, process_account_info_step_2, user, db)
            return

        user.last_name = cleaned
        db.add(user)
        if single:
            db.commit()
            bot.reply_to(message, MSG.USER["ACCOUNT_INFO"]["COMPLETE"])
            return  # Explicitly add the user object
        msg = bot.reply_to(message, MSG.USER["ACCOUNT_INFO"]["NATIONAL_ID"])
        bot.register_next_step_handler(msg, process_account_info_step_3, user, db)

    except Exception as e:
        bot.reply_to(message, MSG.ERRORS["GENERAL_ERROR"])
        logging.error(
            f"[USER-{message.from_user.id}] Error in process_account_info_step_2: {str(e)}"
        )
        db.rollback()


def process_account_info_step_3(
    message: telebot.types.Message,
    user: models.Users,
    db: Session,
    single: boolean = False,
):
    try:
        # Clean and validate national ID
        input_text = message.text.strip()
        # Convert Persian/Arabic numerals to ASCII digits
        persian_to_english = {
            "۰": "0",
            "۱": "1",
            "۲": "2",
            "۳": "3",
            "۴": "4",
            "۵": "5",
            "۶": "6",
            "۷": "7",
            "۸": "8",
            "۹": "9",
            "٠": "0",
            "١": "1",
            "٢": "2",
            "٣": "3",
            "٤": "4",
            "٥": "5",
            "٦": "6",
            "٧": "7",
            "٨": "8",
            "٩": "9",
        }

        cleaned = input_text
        for persian, english in persian_to_english.items():
            cleaned = cleaned.replace(persian, english)
        cleaned = re.sub(r"\D+", "", cleaned.strip(), flags=re.UNICODE)
        if not cleaned or len(cleaned) != 10 or not cleaned.isdigit():
            logging.error(
                f"[USER-{message.from_user.id}] Invalid input: {message.text}"
            )
            msg = bot.reply_to(message, MSG.ERRORS["INVALID_NATIONAL_ID"])
            bot.register_next_step_handler(msg, process_account_info_step_3, user, db)
            return

        user.national_id = cleaned  # Store cleaned version

        # Validate all required fields
        if not all([user.first_name, user.last_name, user.national_id]):
            raise ValueError("Incomplete user information")

        db.add(user)
        db.commit()

        bot.reply_to(message, MSG.USER["ACCOUNT_INFO"]["COMPLETE"])
        if single:
            return
        bot.send_message(
            message.from_user.id,
            MSG.GREATING(user),
            reply_markup=user_flow.main_keyboard_flow(),
        )

    except ValueError as ve:
        db.rollback()
        bot.reply_to(message, MSG.ERRORS["INVALID_DATA"])
        logging.error(f"[USER-{message.from_user.id}] Validation error: {str(ve)}")
    except Exception as e:
        db.rollback()
        bot.reply_to(message, MSG.ERRORS["GENERAL_ERROR"])
        logging.error(
            f"[USER-{message.from_user.id}] Error in process_account_info_step_3: {str(e)}"
        )


# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.callback_query_handler(func=lambda call: True)
@inject
def start_callback(call, db: Session = Dependency(get_db)):
    # if call.data == "SHOW_COURSES":
    #     courses = crud.get_all_courses(db)
    #     if courses:
    #         for course in courses:
    #             course_buttons = InlineKeyboardMarkup()
    #             if course.is_active:
    #                 course_buttons.row(InlineKeyboardButton(f"{course.title},", callback_data=f"COURSE_{course.id}"))
    #         bot.send_message(call.from_user.id, "لیست دوره های مرکز", reply_markup=course_buttons)
    #     else:
    #         bot.send_message(call.from_user.id, "هیچ دوره ای وجود ندارد.")

    # if call.data.startswith("BUY_COURSE_"):
    #     course_id = call.data.split("_")[-1]
    #     course = crud.get_course_by_id(db, course_id)
    #     if course and course.is_active:
    #          transaction = crud.create_transaction(db, course_id, call.from_user.id)
    #          bot.send_invoice(
    #                 message.from_user.id,
    #                 title="پرداخت هزینه دوره",
    #                 description=course.title,
    #                 provider_token="WALLET-TEST-1111111111111111",
    #                 prices=[
    #                     telebot.types.LabeledPrice(
    #                         label="هزینه دوره", amount=course.price*10
    #                     )
    #                 ],
    #                 currency="IRR",
    #                 invoice_payload=transaction.id,
    #             )
    #     else:
    #         bot.send_message(
    #             call.from_user.id, "دوره یافت نشد.", reply_markup=user_flow.main_keyboard_flow()
    #         )
    # if call.data == "MY_COURSES":
    #     print("hello")
    #     bot.send_message(
    #         call.from_user.id,
    #         "Выберите режим голоса, после чего отправьте нам текст песни.",
    #     )
    if call.data == "ACCOUNT_INFO":
        user = crud.get_user_by_bale_id(db, bale_id=str(call.from_user.id))
        if any((user.first_name, user.last_name, user.national_id)):
            bot.send_message(
                call.from_user.id,
                (
                    "🤖 اطلاعات شما:\n"
                    f"نام: {user.first_name}\n"
                    f"نام خانوادگی: {user.last_name}\n"
                ),
                reply_markup=user_flow.account_info_keyboard_flow(),
            )

        else:
            # get user first name, last name and national id from user input
            msg = bot.reply_to(call.message, MSG.USER["ACCOUNT_INFO"]["FIRST_NAME"])
            bot.register_next_step_handler(msg, process_account_info_step_1, db)

    if call.data == USER_CONTROL_FLOW.EDIT_ACCOUNT.value:
        bot.send_message(
            call.from_user.id,
            " کدام بخش از اطلاعات خود را می خواهید ویرایش کنید؟",
            reply_markup=user_flow.account_info_edit_keyboard_flow(),
        )
    if call.data == USER_CONTROL_FLOW.EDIT_FIRST_NAME.value:
        user = crud.get_user_by_bale_id(db, bale_id=str(call.from_user.id))
        msg = bot.send_message(
            call.from_user.id,
            "لطفا نام خود را وارد کنید:",
        )
        bot.register_next_step_handler(
            msg, process_account_info_step_1, db, single=True
        )
    if call.data == USER_CONTROL_FLOW.EDIT_LAST_NAME.value:
        user = crud.get_user_by_bale_id(db, bale_id=str(call.from_user.id))
        msg = bot.send_message(
            call.from_user.id,
            "لطفا نام خانوادگی خود را وارد کنید:",
        )
        bot.register_next_step_handler(
            msg, process_account_info_step_2, user, db, single=True
        )
    if call.data == USER_CONTROL_FLOW.EDIT_NATIONAL_ID.value:
        user = crud.get_user_by_bale_id(db, bale_id=str(call.from_user.id))
        msg = bot.send_message(
            call.from_user.id,
            "لطفا شماره ملی خود را وارد کنید:",
        )
        bot.register_next_step_handler(
            msg, process_account_info_step_3, user, db, single=True
        )

    # if call.data == "MY_C
    # if call.data == "CERTIFICATE":
    #     print("hello")
    #     bot.send_message(
    #         call.from_user.id, "Эта функция пока находится на разбработке."
    #     )

    # if call.data == "CREATE_COURSE":
    #     msg = bot.send_message(
    #         call.from_user.id,
    #         "لطفا اطلاعات دوره را به فرمت زیر وارد کنید:\n\n"
    #         "عنوان دوره\nتوضیحات دوره\nمدت زمان دوره\nهزینه دوره"
    #     )
    #     bot.register_next_step_handler(msg, process_create_course)

    # if call.data == "EDIT_COURSE":
    #     courses = crud.get_all_courses(db)
    #     if courses:
    #         keyboard = InlineKeyboardMarkup()
    #         for course in courses:
    #             keyboard.add(InlineKeyboardButton(
    #                 course.title,
    #                 callback_data=f"EDIT_COURSE_{course.id}"
    #             ))
    #         bot.send_message(
    #             call.from_user.id,
    #             "لطفا دوره مورد نظر برای ویرایش را انتخاب کنید:",
    #             reply_markup=keyboard
    #         )
    #     else:
    #         bot.send_message(call.from_user.id, "هیچ دوره ای وجود ندارد.")

    # if call.data.startswith("EDIT_COURSE_"):
    #     COURSE_FLOW.handle_edit_course(bot, call, db)
    # if call.data == "LIST_COURSES":
    #     courses = crud.get_all_courses(db)
    #     if courses:
    #         message = "لیست دوره ها:\n\n"
    #         for course in courses:
    #             message += (
    #                 f"عنوان: {course.title}\n"
    #                 f"توضیحات: {course.description}\n"
    #                 f"تاریخ شروع : {course.start_date}\n"
    #                 f"مدت زمان: {course.duration}\n"
    #                 f"هزینه: {course.price}\n\n"
    #             )
    #         bot.send_message(call.from_user.id, message)
    #     else:
    #         bot.send_message(call.from_user.id, "هیچ دوره ای وجود ندارد.")


# def process_create_course(message: telebot.types.Message, db: Session = Dependency(get_db)):
#     try:
#         data = message.text.split('\n')
#         if len(data) < 5:
#             bot.reply_to(message, "لطفا تمام اطلاعات را به صورت کامل وارد کنید.")
#             return

#         title, description,start_date, duration, price = data[0], data[1], data[2], data[3],data[4]
#         new_course = models.Courses(
#             title=title,
#             description=description,
#             start_date = start_date,
#             # expired_date =
#             duration=duration,
#             price=price
#         )
#         crud.create_course(db, new_course)
#         bot.reply_to(message, "دوره با موفقیت ایجاد شد.")

#     except Exception as e:
#         bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
#         print(f"Error in process_create_course: {e}")


@bot.message_handler(func=lambda message: True)
@inject
def handle_system_message(message, db: Session = Dependency(get_db)):
    match message.text:
        case BTN.USER_MAIN_MENU.ACCOUNT_INFO:
            user = crud.get_user_by_bale_id(db, bale_id=str(message.from_user.id))
            if any((user.first_name, user.last_name, user.national_id)):
                bot.send_message(
                    message.from_user.id,
                    (
                        "🤖 اطلاعات شما:\n"
                        f"نام: {user.first_name}\n"
                        f"نام خانوادگی: {user.last_name}\n"
                    ),
                    reply_markup=user_flow.account_info_keyboard_flow(),
                )
        case BTN.ADMIN_MAIN_MENU.ADD_COURSE:
            bot.send_message(
                message.from_user.id,
                ("لطفا اطلاعات دوره را وارد کنید:\n" "عنوان دوره\n"),
            )
            bot.register_next_step_handler(message, process_create_course_step_1, db)
        case BTN.ADMIN_MAIN_MENU.LIST_COURSES:
            courses = crud.get_all_courses(db)
            if courses:
                message = (
                    "لیست دوره ها:\n"
                    "برای مشاهده جزئیات دوره، روی عنوان آن کلیک کنید:\n\n"
                )
                keys = InlineKeyboardMarkup()
                for course in courses:
                    keys.add(
                        InlineKeyboardButton(
                            course.title,
                            callback_data=f"COURSE_{course.id}",
                        )
                    )
                bot.send_message(message.from_user.id, message, reply_markup=keys)
            else:
                bot.send_message(message.from_user.id, "هیچ دوره ای وجود ندارد.")


def process_create_course_step_1(message: telebot.types.Message, db: Session):
    try:
        # Extract course details from the message text
        title = message.text.strip()
        if not title:
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Title: {message.text}"
            )
            msg = bot.reply_to(message, "عنوان دوره نمی تواند خالی باشد.")
            bot.register_next_step_handler(msg, process_create_course_step_1, db)
            return
        course = models.Courses(title=title)
        msg = bot.reply_to(message, "لطفا توضیحات دوره را وارد کنید:")
        bot.register_next_step_handler(msg, process_create_course_step_2, course, db)

    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_1: {e}")


def process_create_course_step_2(
    message: telebot.types.Message,
    course: models.Courses,
    db: Session,
):
    try:
        description = message.text.strip()
        if not description:
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Description: {message.text}"
            )
            msg = bot.reply_to(message, "توضیحات دوره نمی تواند خالی باشد.")
            bot.register_next_step_handler(
                msg, process_create_course_step_2, course, db
            )
            return
        course.description = description
        msg = bot.reply_to(message, "لطفا هزینه دوره را به ریال وارد کنید:")
        bot.register_next_step_handler(msg, process_create_course_step_3, course, db)

    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_2: {e}")


def process_create_course_step_3(
    message: telebot.types.Message,
    course: models.Courses,
    db: Session,
):
    try:
        price = message.text.strip()
        if not price.isdigit():
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Price: {message.text}"
            )
            msg = bot.reply_to(message, "قیمت دوره باید یک عدد صحیح باشد.")
            bot.register_next_step_handler(
                msg, process_create_course_step_3, course, db
            )
            return
        course.price = int(price)
        msg = bot.reply_to(message, "لطفا ظرفیت دوره را وارد کنید:")
        bot.register_next_step_handler(msg, process_create_course_step_4, course, db)
    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_3: {e}")


def process_create_course_step_4(
    message: telebot.types.Message,
    course: models.Courses,
    db: Session,
):
    try:
        capacity = message.text.strip()
        if not capacity.isdigit():
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Capacity: {message.text}"
            )
            msg = bot.reply_to(message, "ظرفیت دوره باید یک عدد صحیح باشد.")
            bot.register_next_step_handler(
                msg, process_create_course_step_4, course, db
            )
            return
        course.capacity = int(capacity)
        msg = bot.reply_to(
            message,
            (
                "لطفا تاریخ شروع دوره را وارد کنید (فرمت صحیح تاریخ yyyy-mm-dd):\n"
                "مثال:1404-01-01\n"
            ),
        )
        bot.register_next_step_handler(msg, process_create_course_step_5, course, db)
    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_4: {e}")


def process_create_course_step_5(
    message: telebot.types.Message,
    course: models.Courses,
    db: Session,
):
    try:
        start_date = message.text.strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", start_date):
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Start Date: {message.text}"
            )
            msg = bot.reply_to(message, "تاریخ شروع دوره باید به فرمت yyyy-mm-dd باشد.")
            bot.register_next_step_handler(
                msg, process_create_course_step_5, course, db
            )
            return
        course.start_date = jalali.Persian(start_date).to_gregorian()
        msg = bot.reply_to(message, ("لطفا مدت دوره را به روز وارد کنید\n"))
        bot.register_next_step_handler(msg, process_create_course_step_6, course, db)
    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_5: {e}")


def process_create_course_step_6(
    message: telebot.types.Message,
    course: models.Courses,
    db: Session,
):
    try:
        duration = message.text.strip()
        if not duration.isdigit():
            logging.error(
                f"[USER-{message.from_user.id}] Invalid Course Duration: {message.text}"
            )
            msg = bot.reply_to(message, "مدت دوره باید یک عدد صحیح باشد.")
            bot.register_next_step_handler(
                msg, process_create_course_step_6, course, db
            )
            return
        course.duration = int(duration)
        course.expired_date = (
            jalali.Persian(course.start_date).add_days(course.duration).to_gregorian()
        )
        db.add(course)
        db.commit()
        bot.reply_to(message, "دوره با موفقیت ایجاد شد.")
    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        logging.error(f"Error in process_create_course_step_6: {e}")


bot.infinity_polling()
