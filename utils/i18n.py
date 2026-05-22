# -*- coding: utf-8 -*-
"""
نظام الترجمة متعدد اللغات
"""
import json
from pathlib import Path
from config.settings import LOCALES_DIR, APP_LANGUAGE

# ترجمات افتراضية
TRANSLATIONS = {
    'ar': {
        'app_name': 'نظام ProComSoft ERP',
        'login': 'تسجيل الدخول',
        'username': 'اسم المستخدم',
        'password': 'كلمة المرور',
        'dashboard': 'لوحة التحكم',
        'customers': 'العملاء',
        'products': 'المنتجات',
        'sales': 'المبيعات',
        'purchases': 'المشتريات',
        'inventory': 'المخزون',
        'reports': 'التقارير',
        'settings': 'الإعدادات',
        'logout': 'تسجيل الخروج',
        'add': 'إضافة',
        'edit': 'تعديل',
        'delete': 'حذف',
        'save': 'حفظ',
        'cancel': 'إلغاء',
        'search': 'بحث',
        'name': 'الاسم',
        'code': 'الكود',
        'price': 'السعر',
        'quantity': 'الكمية',
        'total': 'الإجمالي',
        'date': 'التاريخ',
        'status': 'الحالة',
        'user': 'المستخدم',
        'unknown': 'غير معروف',
    },
    'fr': {
        'app_name': 'Système ProComSoft ERP',
        'login': 'Connexion',
        'username': "Nom d'utilisateur",
        'password': 'Mot de passe',
        'dashboard': 'Tableau de bord',
        'customers': 'Clients',
        'products': 'Produits',
        'sales': 'Ventes',
        'purchases': 'Achats',
        'inventory': 'Inventaire',
        'reports': 'Rapports',
        'settings': 'Paramètres',
        'logout': 'Déconnexion',
        'add': 'Ajouter',
        'edit': 'Modifier',
        'delete': 'Supprimer',
        'save': 'Enregistrer',
        'cancel': 'Annuler',
        'search': 'Rechercher',
        'name': 'Nom',
        'code': 'Code',
        'price': 'Prix',
        'quantity': 'Quantité',
        'total': 'Total',
        'date': 'Date',
        'status': 'Statut',
        'user': 'Utilisateur',
        'unknown': 'Inconnu',
    },
    'en': {
        'app_name': 'ProComSoft ERP System',
        'login': 'Login',
        'username': 'Username',
        'password': 'Password',
        'dashboard': 'Dashboard',
        'customers': 'Customers',
        'products': 'Products',
        'sales': 'Sales',
        'purchases': 'Purchases',
        'inventory': 'Inventory',
        'reports': 'Reports',
        'settings': 'Settings',
        'logout': 'Logout',
        'add': 'Add',
        'edit': 'Edit',
        'delete': 'Delete',
        'save': 'Save',
        'cancel': 'Cancel',
        'search': 'Search',
        'name': 'Name',
        'code': 'Code',
        'price': 'Price',
        'quantity': 'Quantity',
        'total': 'Total',
        'date': 'Date',
        'status': 'Status',
        'user': 'User',
        'unknown': 'Unknown',
    }
}

_current_language = APP_LANGUAGE


def set_language(lang: str):
    """تعيين اللغة الحالية"""
    global _current_language
    if lang in TRANSLATIONS:
        _current_language = lang
    else:
        _current_language = 'ar'


def get_language() -> str:
    """الحصول على اللغة الحالية"""
    return _current_language


def t(key: str, lang: str = None) -> str:
    """الحصول على الترجمة"""
    lang = lang or _current_language
    return TRANSLATIONS.get(lang, TRANSLATIONS['ar']).get(key, key)


def load_translations_from_file(lang: str) -> dict:
    """تحميل الترجمات من ملف JSON"""
    file_path = LOCALES_DIR / f"{lang}.json"
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_translations_to_file(lang: str, translations: dict):
    """حفظ الترجمات إلى ملف JSON"""
    file_path = LOCALES_DIR / f"{lang}.json"
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(translations, f, ensure_ascii=False, indent=2)

