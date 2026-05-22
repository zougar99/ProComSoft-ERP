# -*- coding: utf-8 -*-
"""
إعدادات التطبيق الرئيسية
"""
import os
from pathlib import Path

# مسارات المشروع
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "database"
LOCALES_DIR = BASE_DIR / "locales"
REPORTS_DIR = BASE_DIR / "reports"
BACKUP_DIR = DATA_DIR / "backups"

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [DATA_DIR, DB_DIR, LOCALES_DIR, REPORTS_DIR, BACKUP_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# إعدادات قاعدة البيانات
DATABASE_NAME = "procomsoft.db"
DATABASE_PATH = DB_DIR / DATABASE_NAME

# إعدادات التطبيق
APP_NAME = "ProComSoft ERP"
APP_VERSION = "1.0.0"
APP_LANGUAGE = "ar"  # ar, fr, en

# إعدادات الأمان
SECRET_KEY = os.urandom(32)
PASSWORD_MIN_LENGTH = 8
SESSION_TIMEOUT = 3600  # ثانية

# إعدادات الواجهة
THEME = "light"  # light, dark
FONT_FAMILY = "Segoe UI"
FONT_SIZE = 10

# إعدادات العملة والضريبة
DEFAULT_CURRENCY = "DZD"
DEFAULT_TAX_RATE = 19.0  # TVA بالمئة

# إعدادات الطباعة
PRINTER_DEFAULT = "default"
PAPER_SIZE = "A4"

