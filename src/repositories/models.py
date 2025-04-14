from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, String, ForeignKey
from .database import Base
from uuid import uuid4
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint,CheckConstraint
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"


class Users(Base):
    __tablename__ = "users"
    id = Column(PGUUID, default=lambda: uuid4(), primary_key=True, index=True)
    bale_id = Column(Integer, unique=True, nullable=False)
    bale_username = Column(String(512), unique=False, nullable=True)
    role = Column(Enum(UserRole), index=True, default=UserRole.USER, nullable=False)
    gender = Column(Enum(Gender), nullable=True)
    first_name = Column(String(127), nullable=True)
    last_name = Column(String(127), nullable=True)
    national_id = Column(String(10), unique=True, nullable=True)
    is_active = Column(Boolean, default=True)
    created_date = Column(
        DateTime, index=True, default=lambda: datetime.now(tz=timezone.utc)
    )
    
    # Add the relationship to Register
    registers = relationship("Register", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    __table_args__ = (
        CheckConstraint("length(national_id) = 10 AND national_id ~ '^[0-9]+$'", name="check_national_id_format"),
    )
    def __repr__(self):
        return f"<User id={self.id} bale_id={self.bale_id}>"


class Courses(Base):
    __tablename__ = "courses"
    id = Column(PGUUID, default=lambda: uuid4(), primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    capacity = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(
        DateTime, index=True, default=lambda: datetime.now(tz=timezone.utc)
    )
    start_date = Column(DateTime, index=True, nullable=False)
    expired_date = Column(DateTime, index=True, nullable=False)
    updated_date = Column(
        DateTime,
        index=True,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
    
    # Add the relationship to Register
    registers = relationship("Register", back_populates="course", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="course", cascade="all, delete-orphan")
    def __str__(self):
        return str(self.id)

class Register(Base):
    __tablename__ = "register"
    id = Column(PGUUID, default=lambda: uuid4(), primary_key=True, index=True)
    user_id = Column(PGUUID, ForeignKey("users.id"), nullable=False)
    course_id = Column(PGUUID, ForeignKey("courses.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_date = Column(
        DateTime, index=True, default=lambda: datetime.now(tz=timezone.utc)
    )
    updated_date = Column(
        DateTime,
        index=True,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
    user = relationship("Users", back_populates="registers")
    course = relationship("Courses", back_populates="registers")
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='uq_user_course_registration'),
    )
    def __str__(self):
        return str(self.id)
    
class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(PGUUID, default=lambda: uuid4(), primary_key=True, index=True)
    user_id = Column(PGUUID, ForeignKey("users.id"), nullable=False)
    course_id = Column(PGUUID, ForeignKey("courses.id"), nullable=False)
    valid = Column(Boolean, default=False)
    created_date = Column(
        DateTime, index=True, default=lambda: datetime.now(tz=timezone.utc)
    )
    updated_date = Column(
        DateTime,
        index=True,
        default=lambda: datetime.now(tz=timezone.utc),
        onupdate=lambda: datetime.now(tz=timezone.utc),
    )
    @property
    def amount(self):
        return self.course.price

    user = relationship("Users", back_populates="transactions")
    course = relationship("Courses", back_populates="transactions")
    def __str__(self):
        return str(self.id)