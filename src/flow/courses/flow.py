from repositories import crud
from .process import process_edit_course,process_create_course

def create_course(bot,call,db):
    msg = bot.send_message(
        call.from_user.id,
        "لطفا اطلاعات دوره را به فرمت زیر وارد کنید:\n\n"
        "عنوان دوره\nتوضیحات دوره\nمدت زمان دوره\nهزینه دوره"
    )
    bot.register_next_step_handler(bot,msg, process_create_course)
        
def edit_course(bot, call, db):
    course_id = call.data.split("_")[-1]
    course = crud.get_course_by_id(db, course_id)
    if course:
        msg = bot.send_message(
            call.from_user.id,
            f"ویرایش دوره: {course.title}\n\n"
            "اطلاعات جدید را به فرمت زیر وارد کنید:\n\n"
            "عنوان دوره\nتوضیحات دوره\nتاریخ شروع دوره\nمدت زمان دوره\nهزینه دوره\n\n"
            f"مقادیر فعلی:\n"
            f"عنوان: {course.title}\n"
            f"توضیحات: {course.description}\n"
            f"تاریخ شروع : {course.start_date}\n"
            f"مدت زمان: {course.duration}\n"
            f"هزینه: {course.price}",
        )
        bot.register_next_step_handler(bot, msg, process_edit_course, course_id)
def get_courses(bot,call,db):
    courses = crud.get_all_courses(db)
    if courses:
        message = "لیست دوره ها:\n\n"
        for course in courses:
            message += (
                f"عنوان: {course.title}\n"
                f"توضیحات: {course.description}\n"
                f"تاریخ شروع : {course.start_date}\n"
                f"مدت زمان: {course.duration}\n"
                f"هزینه: {course.price}\n\n"
            )
        bot.send_message(call.from_user.id, message)
    else:
        bot.send_message(call.from_user.id, "هیچ دوره ای وجود ندارد.")
