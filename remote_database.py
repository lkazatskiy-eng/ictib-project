# remote_database.py
import sqlite3
import json
import urllib.request
import io
from datetime import datetime
import tempfile
import os


class RemoteDatabase:
    """Класс для работы с удаленной SQLite базой через SSH/WebDAV"""

    def __init__(self, db_url=None, local_cache=True):
        """
        db_url: URL к файлу базы данных на сервере
               Может быть: http://, https://, ftp://, или путь на диске
        local_cache: Кэшировать ли базу локально
        """
        self.db_url = db_url or "http://ваш-сервер.aeza.net/db/collabmatch.db"
        self.local_cache = local_cache
        self.local_db_path = None

        # Если включено кэширование, создаем временный файл
        if local_cache:
            self.local_db_path = tempfile.mktemp(suffix='.db')
            self.download_database()

    def download_database(self):
        """Скачать базу данных с сервера"""
        try:
            if self.db_url.startswith(('http://', 'https://')):
                # HTTP/HTTPS загрузка
                response = urllib.request.urlopen(self.db_url)
                data = response.read()

            elif self.db_url.startswith('ftp://'):
                # FTP загрузка (упрощенная)
                import ftplib
                from urllib.parse import urlparse

                parsed = urlparse(self.db_url)
                ftp = ftplib.FTP(parsed.hostname)
                ftp.login(parsed.username or 'anonymous', parsed.password or '')

                with open(self.local_db_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {parsed.path}', f.write)
                ftp.quit()
                return

            else:
                # Предполагаем, что это локальный путь (если код выполняется на сервере)
                with open(self.db_url, 'rb') as f:
                    data = f.read()

            # Сохраняем скачанные данные
            with open(self.local_db_path, 'wb') as f:
                f.write(data)

            print(f"База данных скачана: {self.local_db_path}")

        except Exception as e:
            print(f"Ошибка загрузки базы данных: {e}")
            # Создаем пустую базу, если не удалось скачать
            self.create_empty_database()

    def upload_database(self):
        """Загрузить базу данных обратно на сервер"""
        try:
            if self.db_url.startswith('ftp://'):
                import ftplib
                from urllib.parse import urlparse

                parsed = urlparse(self.db_url)
                ftp = ftplib.FTP(parsed.hostname)
                ftp.login(parsed.username, parsed.password)

                with open(self.local_db_path, 'rb') as f:
                    ftp.storbinary(f'STOR {parsed.path}', f)
                ftp.quit()

            else:
                # Для HTTP нужен специальный endpoint для загрузки
                print("Загрузка через HTTP не реализована")

        except Exception as e:
            print(f"Ошибка загрузки базы на сервер: {e}")

    def create_empty_database(self):
        """Создать пустую базу данных"""
        conn = sqlite3.connect(self.local_db_path)
        cursor = conn.cursor()

        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                skills TEXT DEFAULT '[]',
                interests TEXT DEFAULT '[]',
                status TEXT DEFAULT '',
                looking_for_project INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Таблица мероприятий
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                location TEXT,
                tags TEXT DEFAULT '[]',
                max_participants INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def get_connection(self):
        """Получить соединение с базой данных"""
        if self.local_cache and self.local_db_path:
            conn = sqlite3.connect(self.local_db_path)
            conn.row_factory = sqlite3.Row
            return conn
        else:
            # Прямое подключение к удаленной базе (если поддерживается)
            raise Exception("Прямое подключение к удаленной SQLite не поддерживается")

    def sync(self):
        """Синхронизировать изменения с сервером"""
        if self.local_cache:
            self.upload_database()
            # После загрузки можно обновить локальную копию
            self.download_database()

    # Все методы из оригинального Database класса

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY name")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    def add_user(self, name, email, skills, interests, status, looking_for_project):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, skills, interests, status, looking_for_project)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, json.dumps(skills), json.dumps(interests), status, looking_for_project))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Автосинхронизация
        self.sync()
        return user_id
