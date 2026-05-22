# -*- coding: utf-8 -*-
"""
أدوات الأمان: تشفير كلمات المرور والمصادقة
"""
import bcrypt
from datetime import datetime
from database.models import User, Session


def hash_password(password: str) -> str:
    """تشفير كلمة المرور"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """التحقق من كلمة المرور"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def authenticate_user(username: str, password: str) -> User:
    """مصادقة المستخدم"""
    session = Session()
    try:
        user = session.query(User).filter(User.username == username).first()
        if user and user.is_active:
            if verify_password(password, user.password_hash):
                user.last_login = datetime.now()
                session.commit()
                return user
        return None
    finally:
        session.close()


def create_user(username: str, password: str, email: str = None, 
                full_name: str = None, role: str = 'user') -> User:
    """إنشاء مستخدم جديد"""
    session = Session()
    try:
        # التحقق من عدم وجود مستخدم بنفس الاسم
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            raise ValueError("اسم المستخدم موجود بالفعل")
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

