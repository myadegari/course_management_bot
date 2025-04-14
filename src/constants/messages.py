def GREATING(user):
    return f"سلام {user.first_name}\nچه کمکی میتونم بهتون کنم؟"


def ADMIN_GREETING(user):
    return f"سلام {user.first_name}\nبه پنل مدیریت خوش آمدید\nچه کمکی میتونم بهتون کنم؟"


USER={
    "ACCOUNT_INFO" :{
        "FIRST_NAME":"نام خود را وارد کنید:",
        "LAST_NAME":"نام خانوادگی خود را وارد کنید:",
        "NATIONAL_ID":"کد ملی خود را وارد کنید:",
        "COMPLETE":"اطلاعات شما با موفقیت ثبت شد.",
    }
}

ERRORS={
    "GENERAL_ERROR":"خطایی رخ داده است.",
    "INVALID_FIRST_NAME":"نام خود را به درستی وارد کنید (فقط حروف مجاز است):",
    "INVALID_LAST_NAME":"نام خانوادگی خود را به درستی وارد کنید (فقط حروف مجاز است):",
    "INVALID_NATIONAL_ID":"کد ملی خود را به درستی وارد کنید (کد ملی 10 رقمی است):",
    "USER_NOT_FOUND":"کاربری با این شناسه یافت نشد.",
}