import sys
import sqlite3
import json
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor


class Database:
    def __init__(self, db_path: str = "collabmatch.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Получить соединение с базой данных"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Инициализировать базу данных"""
        conn = self.get_connection()
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

        # Таблица проектов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'planning',
                owner_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        ''')

        # Тестовые данные
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            # Тестовые пользователи
            test_users = [
                ('Иван Программист', 'ivan@example.com',
                 '["Python", "SQL", "AI", "Flask"]', '["биология", "нейросети", "машинное обучение"]',
                 'Хочу сотрудничать с биологами', 1),
                ('Мария Биолог', 'maria@example.com',
                 '["биоинформатика", "статистика", "R"]', '["нейросети", "генетика", "Python"]',
                 'Ищу программиста для проекта', 1),
                ('Алексей Дизайнер', 'alex@example.com',
                 '["UI/UX", "Figma", "Photoshop"]', '["стартапы", "веб-разработка", "IT"]',
                 'Открыт к коллаборациям', 1),
                ('Ольга Маркетолог', 'olga@example.com',
                 '["SMM", "Аналитика", "Копирайтинг"]', '["образование", "социальные проекты", "менеджмент"]',
                 'Готова помочь с продвижением', 0),
                ('Сергей Инженер', 'sergey@example.com',
                 '["Arduino", "электроника", "C++"]', '["робототехника", "IoT", "программирование"]',
                 'Ищу команду для хакатона', 1)
            ]

            for user in test_users:
                cursor.execute('''
                    INSERT INTO users (name, email, skills, interests, status, looking_for_project)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', user)

            # Тестовые мероприятия
            test_events = [
                ('Нейросети в биологии',
                 'Лекция о применении нейросетей в биологических исследованиях',
                 '2024-12-15 18:00', '2024-12-15 20:00',
                 'Аудитория 101', '["нейросети", "биология", "исследования"]', 50),
                ('Стартап-уикенд',
                 'Интенсив по созданию междисциплинарных проектов',
                 '2024-12-20 10:00', '2024-12-21 18:00',
                 'Коворкинг "Точка кипения"', '["стартап", "проекты", "коллаборации"]', 100),
                ('Хакатон по биоинформатике',
                 'Соревнование по созданию IT-решений для биологии',
                 '2024-12-25 09:00', '2024-12-27 21:00',
                 'Технопарк', '["хакатон", "биоинформатика", "программирование"]', 30)
            ]

            for event in test_events:
                cursor.execute('''
                    INSERT INTO events (title, description, start_date, end_date, location, tags, max_participants)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', event)

            # Тестовые проекты
            test_projects = [
                ('AI для анализа ДНК', 'Проект по созданию нейросети для анализа генетических данных', 'active', 1),
                ('EdTech платформа', 'Образовательная платформа для студентов', 'planning', 3),
                ('Робот-помощник', 'Автоматизация лабораторных работ', 'in_progress', 5)
            ]

            for project in test_projects:
                cursor.execute('''
                    INSERT INTO projects (title, description, status, owner_id)
                    VALUES (?, ?, ?, ?)
                ''', project)

        conn.commit()
        conn.close()

    def get_all_users(self):
        """Получить всех пользователей"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY name")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    def get_all_events(self):
        """Получить все мероприятия"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM events ORDER BY start_date")
        events = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return events

    def get_all_projects(self):
        """Получить все проекты"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY created_at DESC")
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return projects

    def get_user(self, user_id):
        """Получить пользователя по ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

    def add_user(self, name, email, skills, interests, collaboration_status, looking_for_project):
        """Добавить нового пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (name, email, skills, interests, status, looking_for_project)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, email, json.dumps(skills), json.dumps(interests), collaboration_status, looking_for_project))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id

    def add_event(self, title, description, start_date, end_date, location, tags, max_participants):
        """Добавить новое мероприятие"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO events (title, description, start_date, end_date, location, tags, max_participants)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, start_date, end_date, location, json.dumps(tags), max_participants))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def add_project(self, title, description, status, owner_id):
        """Добавить новый проект"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (title, description, status, owner_id)
            VALUES (?, ?, ?, ?)
        ''', (title, description, status, owner_id))
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return project_id

    def find_matches(self, user_id):
        """Найти совпадения для пользователя"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return []

        user = dict(user)
        cursor.execute("SELECT * FROM users WHERE id != ?", (user_id,))
        all_users = [dict(row) for row in cursor.fetchall()]
        conn.close()

        user_skills = set(json.loads(user['skills']))
        user_interests = set(json.loads(user['interests']))

        matches = []

        for other_user in all_users:
            other_skills = set(json.loads(other_user['skills']))
            other_interests = set(json.loads(other_user['interests']))

            common_skills = user_skills.intersection(other_skills)
            common_interests = user_interests.intersection(other_interests)

            if common_skills or common_interests:
                score = len(common_skills) * 10 + len(common_interests) * 5
                if user['looking_for_project'] and other_user['looking_for_project']:
                    score += 20

                matches.append({
                    'user': other_user,
                    'score': score,
                    'common_skills': list(common_skills),
                    'common_interests': list(common_interests)
                })

        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches

    def search(self, query):
        """Поиск по всем данным"""
        conn = self.get_connection()
        cursor = conn.cursor()

        search_pattern = f"%{query}%"

        # Поиск пользователей
        cursor.execute('''
            SELECT * FROM users 
            WHERE name LIKE ? OR email LIKE ? OR skills LIKE ? 
            OR interests LIKE ? OR status LIKE ?
            ORDER BY name
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        users = [dict(row) for row in cursor.fetchall()]

        # Поиск мероприятий
        cursor.execute('''
            SELECT * FROM events 
            WHERE title LIKE ? OR description LIKE ? OR tags LIKE ? 
            OR location LIKE ?
            ORDER BY start_date
        ''', (search_pattern, search_pattern, search_pattern, search_pattern))
        events = [dict(row) for row in cursor.fetchall()]

        # Поиск проектов
        cursor.execute('''
            SELECT * FROM projects 
            WHERE title LIKE ? OR description LIKE ? OR status LIKE ?
            ORDER BY created_at DESC
        ''', (search_pattern, search_pattern, search_pattern))
        projects = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return {
            'users': users,
            'events': events,
            'projects': projects
        }

    def get_stats(self):
        """Получить статистику"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM events")
        total_events = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM users WHERE looking_for_project = 1")
        looking_for_project = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM projects")
        total_projects = cursor.fetchone()[0]

        # Подсчет уникальных навыков
        cursor.execute("SELECT skills FROM users")
        all_skills = set()
        for row in cursor.fetchall():
            skills = json.loads(row[0])
            all_skills.update(skills)
        unique_skills = len(all_skills)

        conn.close()

        return {
            'total_users': total_users,
            'total_events': total_events,
            'looking_for_project': looking_for_project,
            'total_projects': total_projects,
            'unique_skills': unique_skills
        }


class UserCard(QFrame):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)

        layout = QVBoxLayout(self)

        # Имя и email
        name_label = QLabel(f"<h3>{self.user_data['name']}</h3>")
        layout.addWidget(name_label)

        if self.user_data['email']:
            email_label = QLabel(f"📧 {self.user_data['email']}")
            email_label.setStyleSheet("color: #666;")
            layout.addWidget(email_label)

        # Навыки
        skills = json.loads(self.user_data['skills'])
        if skills:
            skills_label = QLabel(f"<b>Навыки:</b> {', '.join(skills[:5])}")
            skills_label.setWordWrap(True)
            layout.addWidget(skills_label)

        # Интересы
        interests = json.loads(self.user_data['interests'])
        if interests:
            interests_label = QLabel(f"<b>Интересы:</b> {', '.join(interests[:5])}")
            interests_label.setWordWrap(True)
            layout.addWidget(interests_label)

        # Статус
        status = self.user_data['status']
        if status:
            status_label = QLabel(f"💬 {status}")
            status_label.setStyleSheet("color: #2ecc71; font-style: italic;")
            layout.addWidget(status_label)

        # Ищет проект
        if self.user_data['looking_for_project']:
            project_label = QLabel("🔍 Ищет проект для коллаборации")
            project_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(project_label)

        layout.addStretch()


class EventCard(QFrame):
    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #2ecc71;
            }
        """)

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel(f"<h3>{self.event_data['title']}</h3>")
        layout.addWidget(title_label)

        # Описание
        description = self.event_data['description']
        if description:
            desc_label = QLabel(description[:150] + "..." if len(description) > 150 else description)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Даты
        start_date = self.event_data['start_date']
        if start_date:
            date_label = QLabel(f"📅 {start_date}")
            layout.addWidget(date_label)

        # Место
        location = self.event_data['location']
        if location:
            loc_label = QLabel(f"📍 {location}")
            layout.addWidget(loc_label)

        # Теги
        tags = json.loads(self.event_data['tags'])
        if tags:
            tags_text = "🏷️ " + ", ".join(tags[:3])
            tags_label = QLabel(tags_text)
            tags_label.setStyleSheet("color: #3498db;")
            layout.addWidget(tags_label)

        layout.addStretch()


class ProjectCard(QFrame):
    def __init__(self, project_data, parent=None):
        super().__init__(parent)
        self.project_data = project_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #9b59b6;
            }
        """)

        layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel(f"<h3>{self.project_data['title']}</h3>")
        layout.addWidget(title_label)

        # Описание
        description = self.project_data['description']
        if description:
            desc_label = QLabel(description[:150] + "..." if len(description) > 150 else description)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Статус
        status = self.project_data['status']
        status_label = QLabel(f"📊 Статус: {status}")
        if status == 'active':
            status_label.setStyleSheet("color: #2ecc71; font-weight: bold;")
        elif status == 'planning':
            status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        elif status == 'in_progress':
            status_label.setStyleSheet("color: #3498db; font-weight: bold;")
        layout.addWidget(status_label)

        layout.addStretch()


class CollabMatchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.setWindowTitle("CollabMatch - Поиск команды по интересам")
        self.setGeometry(100, 100, 1100, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Заголовок
        header = QLabel("🤝 CollabMatch")
        header_font = QFont()
        header_font.setPointSize(24)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)

        # Подзаголовок
        subtitle = QLabel("Найди команду для проекта по интересам и навыкам")
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(subtitle)

        # Панель статистики
        stats_widget = self.create_stats_widget()
        main_layout.addWidget(stats_widget)

        # Панель поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск пользователей, мероприятий, навыков...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_button = QPushButton("Поиск")
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка 1: Пользователи
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tab_widget.addTab(self.users_tab, "👥 Пользователи")

        # Вкладка 2: Мероприятия
        self.events_tab = QWidget()
        self.setup_events_tab()
        self.tab_widget.addTab(self.events_tab, "📅 Мероприятия")

        # Вкладка 3: Совпадения
        self.matches_tab = QWidget()
        self.setup_matches_tab()
        self.tab_widget.addTab(self.matches_tab, "💫 Совпадения")

        # Вкладка 4: Результаты поиска
        self.search_results_tab = QWidget()
        self.setup_search_results_tab()
        self.tab_widget.addTab(self.search_results_tab, "🔍 Результаты")

        main_layout.addWidget(self.tab_widget)

        # Статистика в статусбаре
        self.stats_label = QLabel()
        self.statusBar().addWidget(self.stats_label)
        self.update_stats()

    def create_stats_widget(self):
        """Создать виджет статистики"""
        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)

        # Инициализируем метки
        self.total_users_label = QLabel("0")
        self.total_events_label = QLabel("0")
        self.looking_label = QLabel("0")
        self.projects_label = QLabel("0")
        self.skills_label = QLabel("0")

        stats_data = [
            ("👥 Пользователей", self.total_users_label),
            ("📅 Мероприятий", self.total_events_label),
            ("🔍 Ищут проект", self.looking_label),
            ("🚀 Проектов", self.projects_label),
            ("🛠️ Навыков", self.skills_label)
        ]

        for text, value_label in stats_data:
            stat_widget = QWidget()
            stat_layout = QVBoxLayout(stat_widget)

            value_font = QFont()
            value_font.setPointSize(16)
            value_font.setBold(True)
            value_label.setFont(value_font)
            value_label.setAlignment(Qt.AlignCenter)
            value_label.setStyleSheet("color: #3498db;")

            text_label = QLabel(text)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")

            stat_layout.addWidget(value_label)
            stat_layout.addWidget(text_label)

            stats_layout.addWidget(stat_widget)

        return stats_widget

    def setup_users_tab(self):
        """Настроить вкладку пользователей"""
        layout = QVBoxLayout(self.users_tab)

        # Кнопка добавления пользователя
        add_user_btn = QPushButton("➕ Добавить нового пользователя")
        add_user_btn.clicked.connect(self.show_add_user_dialog)
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addWidget(add_user_btn)

        # Прокручиваемая область для пользователей
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.users_layout = QVBoxLayout(scroll_widget)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Заголовок
        title = QLabel("Все пользователи:")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        self.users_layout.addWidget(title)

        # Сюда будут добавляться карточки пользователей
        self.users_cards_container = QWidget()
        self.users_cards_layout = QVBoxLayout(self.users_cards_container)
        self.users_layout.addWidget(self.users_cards_container)

        self.users_layout.addStretch()
        layout.addWidget(scroll_area)

    def setup_events_tab(self):
        """Настроить вкладку мероприятий"""
        layout = QVBoxLayout(self.events_tab)

        # Кнопка добавления мероприятия
        add_event_btn = QPushButton("➕ Добавить новое мероприятие")
        add_event_btn.clicked.connect(self.show_add_event_dialog)
        add_event_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        layout.addWidget(add_event_btn)

        # Таблица мероприятий (ТОЛЬКО ДЛЯ ЧТЕНИЯ)
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels(
            ['Название', 'Описание', 'Дата начала', 'Дата окончания', 'Место', 'Теги'])

        # Запрещаем редактирование
        self.events_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Настройка таблицы
        self.events_table.horizontalHeader().setStretchLastSection(True)
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setStyleSheet("""
            QTableWidget {
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)

        layout.addWidget(self.events_table)

    def setup_matches_tab(self):
        """Настроить вкладку совпадений"""
        layout = QVBoxLayout(self.matches_tab)

        # Выбор пользователя
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Выберите пользователя для поиска совпадений:"))

        self.user_combo = QComboBox()
        select_layout.addWidget(self.user_combo)

        find_btn = QPushButton("🔍 Найти совпадения")
        find_btn.clicked.connect(self.find_matches)
        find_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        select_layout.addWidget(find_btn)

        select_layout.addStretch()
        layout.addLayout(select_layout)

        # Область результатов
        self.matches_scroll = QScrollArea()
        self.matches_widget = QWidget()
        self.matches_layout = QVBoxLayout(self.matches_widget)
        self.matches_scroll.setWidget(self.matches_widget)
        self.matches_scroll.setWidgetResizable(True)

        layout.addWidget(self.matches_scroll)

    def setup_search_results_tab(self):
        """Настроить вкладку результатов поиска"""
        layout = QVBoxLayout(self.search_results_tab)

        # Заголовок
        self.search_title = QLabel("Результаты поиска")
        self.search_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.search_title)

        # Прокручиваемая область
        self.search_scroll = QScrollArea()
        self.search_widget = QWidget()
        self.search_results_layout = QVBoxLayout(self.search_widget)
        self.search_scroll.setWidget(self.search_widget)
        self.search_scroll.setWidgetResizable(True)

        layout.addWidget(self.search_scroll)

    def load_data(self):
        """Загрузка всех данных из базы"""
        # Загрузка пользователей
        users = self.db.get_all_users()
        self.display_users(users)

        # Загрузка в комбобокс
        self.user_combo.clear()
        self.user_combo.addItem("-- Выберите пользователя --", -1)
        for user in users:
            self.user_combo.addItem(f"{user['name']} (ID: {user['id']})", user['id'])

        # Загрузка мероприятий
        self.display_events()

        # Обновление статистики
        self.update_stats()

    def display_users(self, users):
        """Отображение пользователей на вкладке"""
        # Очищаем старые карточки
        for i in reversed(range(self.users_cards_layout.count())):
            widget = self.users_cards_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not users:
            label = QLabel("Пользователей пока нет")
            label.setStyleSheet("color: #7f8c8d; font-size: 14px; padding: 20px; text-align: center;")
            self.users_cards_layout.addWidget(label)
            return

        for user in users:
            card = UserCard(user)
            self.users_cards_layout.addWidget(card)

    def display_events(self):
        """Отображение мероприятий в таблице"""
        events = self.db.get_all_events()
        self.events_table.setRowCount(len(events))

        for row, event in enumerate(events):
            # Название
            title_item = QTableWidgetItem(event['title'])
            self.events_table.setItem(row, 0, title_item)

            # Описание
            description = event['description'] or ""
            desc_item = QTableWidgetItem(description[:100] + "..." if len(description) > 100 else description)
            self.events_table.setItem(row, 1, desc_item)

            # Даты
            start_item = QTableWidgetItem(event['start_date'] or "")
            end_item = QTableWidgetItem(event['end_date'] or "")
            self.events_table.setItem(row, 2, start_item)
            self.events_table.setItem(row, 3, end_item)

            # Место
            location_item = QTableWidgetItem(event['location'] or "")
            self.events_table.setItem(row, 4, location_item)

            # Теги
            tags = json.loads(event['tags'])
            tags_item = QTableWidgetItem(", ".join(tags))
            self.events_table.setItem(row, 5, tags_item)

        # Автоматически подгоняем ширину колонок
        self.events_table.resizeColumnsToContents()

    def find_matches(self):
        """Поиск совпадений для выбранного пользователя"""
        user_id = self.user_combo.currentData()
        if user_id == -1:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя для поиска совпадений")
            return

        # Очищаем предыдущие результаты
        for i in reversed(range(self.matches_layout.count())):
            widget = self.matches_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        matches = self.db.find_matches(user_id)

        if not matches:
            # Показываем сообщение, что совпадений нет
            label = QLabel(
                "🤷‍♂️ Совпадений не найдено\n\nПопробуйте выбрать другого пользователя или добавьте больше навыков и интересов в профиль.")
            label.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    color: #7f8c8d;
                    padding: 40px;
                    text-align: center;
                    line-height: 1.5;
                }
            """)
            label.setAlignment(Qt.AlignCenter)
            self.matches_layout.addWidget(label)
            return

        # Заголовок
        user = self.db.get_user(user_id)
        user_name = user['name'] if user else "Неизвестный пользователь"
        title = QLabel(f"🎯 Найдено {len(matches)} совпадений для {user_name}:")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        self.matches_layout.addWidget(title)

        # Отображаем совпадения
        for match in matches[:15]:  # Показываем первые 15
            match_widget = self.create_match_widget(match)
            self.matches_layout.addWidget(match_widget)

        self.matches_layout.addStretch()

    def create_match_widget(self, match_data):
        """Создание виджета для отображения совпадения"""
        user = match_data['user']

        widget = QFrame()
        widget.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 2px solid #e0e0e0;
                padding: 15px;
                margin: 10px;
            }
            QFrame:hover {
                border-color: #3498db;
                background-color: #f8f9fa;
            }
        """)

        layout = QVBoxLayout(widget)

        # Заголовок с баллами
        header = QHBoxLayout()

        name_label = QLabel(f"<b>{user['name']}</b>")
        name_label.setStyleSheet("font-size: 16px;")

        score_label = QLabel(f"🏆 {match_data['score']} баллов")
        score_label.setStyleSheet("""
            QLabel {
                background-color: #3498db;
                color: white;
                padding: 5px 15px;
                border-radius: 15px;
                font-weight: bold;
            }
        """)

        header.addWidget(name_label)
        header.addStretch()
        header.addWidget(score_label)
        layout.addLayout(header)

        # Email
        if user['email']:
            email_label = QLabel(f"📧 {user['email']}")
            email_label.setStyleSheet("color: #666;")
            layout.addWidget(email_label)

        # Общие навыки
        common_skills = match_data['common_skills']
        if common_skills:
            skills_text = f"<b>Общие навыки:</b> {', '.join(common_skills)}"
            skills_label = QLabel(skills_text)
            skills_label.setWordWrap(True)
            layout.addWidget(skills_label)

        # Общие интересы
        common_interests = match_data['common_interests']
        if common_interests:
            interests_text = f"<b>Общие интересы:</b> {', '.join(common_interests)}"
            interests_label = QLabel(interests_text)
            interests_label.setWordWrap(True)
            layout.addWidget(interests_label)

        # Статус
        if user['status']:
            status_label = QLabel(f"💬 {user['status']}")
            status_label.setStyleSheet("color: #2ecc71;")
            layout.addWidget(status_label)

        # Ищет проект
        if user['looking_for_project']:
            project_label = QLabel("🔍 Ищет проект для коллаборации")
            project_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(project_label)

        return widget

    def perform_search(self):
        """Выполнение поиска"""
        query = self.search_input.text().strip()

        if not query:
            QMessageBox.information(self, "Поиск", "Введите поисковый запрос")
            return

        # Переходим на вкладку результатов
        self.tab_widget.setCurrentIndex(3)

        # Очищаем предыдущие результаты
        for i in reversed(range(self.search_results_layout.count())):
            widget = self.search_results_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Выполняем поиск
        results = self.db.search(query)

        # Обновляем заголовок
        self.search_title.setText(f"Результаты поиска: '{query}'")

        # Отображаем результаты
        total_results = len(results['users']) + len(results['events']) + len(results['projects'])

        if total_results == 0:
            label = QLabel(f"По запросу '{query}' ничего не найдено")
            label.setStyleSheet("font-size: 16px; color: #7f8c8d; padding: 40px; text-align: center;")
            label.setAlignment(Qt.AlignCenter)
            self.search_results_layout.addWidget(label)
            return

        # Пользователи
        if results['users']:
            users_label = QLabel(f"👥 Пользователи ({len(results['users'])})")
            users_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
            self.search_results_layout.addWidget(users_label)

            for user in results['users']:
                card = UserCard(user)
                self.search_results_layout.addWidget(card)

        # Мероприятия
        if results['events']:
            events_label = QLabel(f"📅 Мероприятия ({len(results['events'])})")
            events_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
            self.search_results_layout.addWidget(events_label)

            for event in results['events']:
                card = EventCard(event)
                self.search_results_layout.addWidget(card)

        # Проекты
        if results['projects']:
            projects_label = QLabel(f"🚀 Проекты ({len(results['projects'])})")
            projects_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-top: 20px;")
            self.search_results_layout.addWidget(projects_label)

            for project in results['projects']:
                card = ProjectCard(project)
                self.search_results_layout.addWidget(card)

        self.search_results_layout.addStretch()

    def show_add_user_dialog(self):
        """Показать диалог добавления пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить нового пользователя")
        dialog.setModal(True)
        dialog.resize(500, 400)

        layout = QVBoxLayout(dialog)

        # Форма
        form = QFormLayout()

        name_input = QLineEdit()
        email_input = QLineEdit()
        skills_input = QLineEdit()
        skills_input.setPlaceholderText("Python, SQL, Дизайн...")
        interests_input = QLineEdit()
        interests_input.setPlaceholderText("ИИ, Биология, Стартапы...")
        status_input = QLineEdit()
        status_input.setPlaceholderText("Хочу сотрудничать...")
        looking_check = QCheckBox("Ищет проект")

        form.addRow("Имя *:", name_input)
        form.addRow("Email:", email_input)
        form.addRow("Навыки:", skills_input)
        form.addRow("Интересы:", interests_input)
        form.addRow("Статус:", status_input)
        form.addRow("", looking_check)

        layout.addLayout(form)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_new_user(
            dialog, name_input.text(), email_input.text(),
            skills_input.text(), interests_input.text(),
            status_input.text(), looking_check.isChecked()
        ))
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.exec()

    def save_new_user(self, dialog, name, email, skills_text, interests_text, status, looking):
        """Сохранение нового пользователя"""
        if not name.strip():
            QMessageBox.warning(dialog, "Ошибка", "Введите имя пользователя")
            return

        skills = [s.strip() for s in skills_text.split(',') if s.strip()]
        interests = [i.strip() for i in interests_text.split(',') if i.strip()]

        try:
            user_id = self.db.add_user(
                name.strip(),
                email.strip(),
                skills,
                interests,
                status.strip(),
                looking
            )

            QMessageBox.information(dialog, "Успех", f"Пользователь добавлен с ID: {user_id}")
            dialog.accept()
            self.load_data()

        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить пользователя: {str(e)}")

    def show_add_event_dialog(self):
        """Показать диалог добавления мероприятия"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить новое мероприятие")
        dialog.setModal(True)
        dialog.resize(600, 400)

        layout = QVBoxLayout(dialog)

        # Форма
        form = QFormLayout()

        title_input = QLineEdit()
        description_input = QTextEdit()
        description_input.setMaximumHeight(100)
        start_date_input = QLineEdit()
        start_date_input.setPlaceholderText("ГГГГ-ММ-ДД ЧЧ:ММ")
        end_date_input = QLineEdit()
        end_date_input.setPlaceholderText("ГГГГ-ММ-ДД ЧЧ:ММ")
        location_input = QLineEdit()
        tags_input = QLineEdit()
        tags_input.setPlaceholderText("нейросети, биология, лекция...")

        form.addRow("Название *:", title_input)
        form.addRow("Описание:", description_input)
        form.addRow("Дата начала *:", start_date_input)
        form.addRow("Дата окончания *:", end_date_input)
        form.addRow("Место:", location_input)
        form.addRow("Теги:", tags_input)

        layout.addLayout(form)

        # Кнопки
        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_new_event(
            dialog, title_input.text(), description_input.toPlainText(),
            start_date_input.text(), end_date_input.text(),
            location_input.text(), tags_input.text()
        ))
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(dialog.reject)

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        dialog.exec()

    def save_new_event(self, dialog, title, description, start_date, end_date, location, tags_text):
        """Сохранение нового мероприятия"""
        if not title.strip():
            QMessageBox.warning(dialog, "Ошибка", "Введите название мероприятия")
            return

        if not start_date.strip() or not end_date.strip():
            QMessageBox.warning(dialog, "Ошибка", "Введите даты начала и окончания")
            return

        tags = [t.strip() for t in tags_text.split(',') if t.strip()]

        try:
            event_id = self.db.add_event(
                title.strip(),
                description.strip(),
                start_date.strip(),
                end_date.strip(),
                location.strip(),
                tags,
                0
            )

            QMessageBox.information(dialog, "Успех", f"Мероприятие добавлено с ID: {event_id}")
            dialog.accept()
            self.load_data()

        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить мероприятие: {str(e)}")

    def update_stats(self):
        """Обновление статистики"""
        try:
            stats = self.db.get_stats()

            # Обновляем значения в виджетах статистики
            self.total_users_label.setText(str(stats.get('total_users', 0)))
            self.total_events_label.setText(str(stats.get('total_events', 0)))
            self.looking_label.setText(str(stats.get('looking_for_project', 0)))
            self.projects_label.setText(str(stats.get('total_projects', 0)))
            self.skills_label.setText(str(stats.get('unique_skills', 0)))

            # Обновляем статусбар
            stats_text = (
                f"👥 Пользователей: {stats.get('total_users', 0)} | "
                f"📅 Мероприятий: {stats.get('total_events', 0)} | "
                f"🔍 Ищут проект: {stats.get('looking_for_project', 0)} | "
                f"🚀 Проектов: {stats.get('total_projects', 0)} | "
                f"🛠️ Уникальных навыков: {stats.get('unique_skills', 0)}"
            )

            self.stats_label.setText(stats_text)
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {e}")
            # Устанавливаем значения по умолчанию при ошибке
            self.total_users_label.setText("0")
            self.total_events_label.setText("0")
            self.looking_label.setText("0")
            self.projects_label.setText("0")
            self.skills_label.setText("0")

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        reply = QMessageBox.question(
            self, 'Выход',
            'Вы уверены, что хотите выйти?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    # Настройка стиля
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f7fa;
        }
        QTabWidget::pane {
            border: 1px solid #d1d8e0;
            background-color: white;
        }
        QTabBar::tab {
            background-color: #eef2f7;
            padding: 10px 20px;
            border: 1px solid #d1d8e0;
            margin-right: 2px;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #3498db;
        }
        QLineEdit, QTextEdit {
            padding: 8px;
            border: 1px solid #d1d8e0;
            border-radius: 4px;
        }
        QPushButton {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QScrollArea {
            border: none;
            background-color: #f8f9fa;
        }
        QTableWidget {
            background-color: white;
        }
        QTableWidget::item {
            padding: 6px;
        }
        QHeaderView::section {
            background-color: #3498db;
            color: white;
            padding: 8px;
            border: none;
            font-weight: bold;
        }
    """)

    window = CollabMatchApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()