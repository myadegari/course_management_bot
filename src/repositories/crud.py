from .models import Users, Courses
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import UUID as PGUUID

def get_user_by_bale_id(db: Session, bale_id):
    return (
            db.query(Users)
            .filter(Users.bale_id == str(bale_id))
            .first()
            )
def make_new_user(db: Session, user: Users):
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_course(db: Session, course: Courses):
    db.add(course)
    db.commit()
    db.refresh(course)
    return course

def get_all_courses(db: Session):
    return db.query(Courses).all()

def get_course_by_id(db: Session, course_id: PGUUID):
    return db.query(Courses).filter(Courses.id == course_id).first()

def update_course(db: Session, course: Courses):
    db_course = db.query(Courses).filter(Courses.id == course.id).first()
    if db_course:
        db_course.title = course.title
        db_course.description = course.description
        db_course.duration = course.duration
        db_course.price = course.price
        db.commit()
        db.refresh(db_course)
        return db_course
    return None