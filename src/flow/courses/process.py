from telebot import types as TELEBOT_TYPES
from utils.dependency import Dependency, inject
from repositories.models import Courses
from repositories import crud
from sqlalchemy.orm import Session
from repositories.utils import get_db
from utils import jalali
from datetime import datetime,timezone
from dateutil.relativedelta import relativedelta

@inject
def process_edit_course(bot,message: TELEBOT_TYPES.Message, course_id: int, db: Session = Dependency(get_db)):
    try:
        data = message.text.split('\n')
        if len(data) < 4:
            bot.reply_to(message, "لطفا تمام اطلاعات را به صورت کامل وارد کنید.")
            return
            
        title, description, duration, price = data[0], data[1], data[2], data[3]
        updated_course = Courses(
            id=course_id,
            title=title,
            description=description,
            duration=duration,
            price=price
        )
        crud.update_course(db, updated_course)
        bot.reply_to(message, "دوره با موفقیت ویرایش شد.")
        
    except Exception as e:
        bot.reply_to(message, "خطایی در ویرایش دوره رخ داده است.")
        print(f"Error in process_edit_course: {e}")

@inject
def process_create_course(bot,message: TELEBOT_TYPES.Message, db: Session = Dependency(get_db)):
    try:
        data = message.text.split('\n')
        if len(data) < 5:
            bot.reply_to(message, "لطفا تمام اطلاعات را به صورت کامل وارد کنید.")
            return
            
        title, description,start_date, duration, price = data[0], data[1], data[2], data[3],data[4]
        start_date = datetime(jalali.Persian(start_date).gregorian_string()).astimezone(tz=timezone.utc)
        new_course = Courses(
            title=title,
            description=description,
            start_date = start_date,
            expired_date = start_date+relativedelta(days=int(duration)),
            duration=duration,
            price=price
        )
        crud.create_course(db, new_course)
        bot.reply_to(message, "دوره با موفقیت ایجاد شد.")
        
    except Exception as e:
        bot.reply_to(message, "خطایی در ایجاد دوره رخ داده است.")
        print(f"Error in process_create_course: {e}")
