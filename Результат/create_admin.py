"""Создание администратора (логин Conf2027, пароль Demo77). Запуск: python create_admin.py"""
import config
from db import Database, init_db
from repositories import UserRepository

init_db(config.DATABASE)
users = UserRepository(Database(config.DATABASE))
if users.login_exists("Conf2027"):
    print("Администратор уже существует")
else:
    users.create("Conf2027", "Demo77", "Администратор портала",
                 "8(000)000-00-00", "admin@conf.ru", "admin")
    print("Администратор создан: Conf2027 / Demo77")