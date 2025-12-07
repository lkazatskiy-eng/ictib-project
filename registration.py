import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import random
import os

ICTIB_COLORS = {
    'primary': '#0056b3', 'primary_light': '#1a6bc4', 'primary_dark': '#004a99',
    'secondary': '#00a8ff', 'accent': '#ff6b6b', 'success': '#28a745',
    'warning': '#ffc107', 'light': '#f8f9fa', 'lighter': '#ffffff',
    'dark': '#212529', 'gray': '#6c757d',
}

class FastAnimatedBackground:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.particles = []
        self.create_fast_gradient()
        self.create_particles(15)
        self.animate()
    
    def create_fast_gradient(self):
        color1 = '#0056b3'
        color2 = '#00a8ff'
        steps = 10
        
        for i in range(steps):
            ratio = i / steps
            r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
            r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
            r = int(r1 * (1 - ratio) + r2 * ratio)
            g = int(g1 * (1 - ratio) + g2 * ratio)
            b = int(b1 * (1 - ratio) + b2 * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            y1 = i * (self.height // steps)
            y2 = (i + 1) * (self.height // steps)
            self.canvas.create_rectangle(0, y1, self.width, y2, fill=color, outline='')
    
    def create_particles(self, count):
        colors = ['#0056b3', '#1a6bc4', '#00a8ff']
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(2, 5)
            color = random.choice(colors)
            speed_x = random.uniform(-0.3, 0.3)
            speed_y = random.uniform(-0.3, 0.3)
            particle = self.canvas.create_oval(x-size, y-size, x+size, y+size, fill=color, outline='')
            self.particles.append({
                'id': particle, 'x': x, 'y': y, 'size': size,
                'speed_x': speed_x, 'speed_y': speed_y
            })
    
    def animate(self):
        for particle in self.particles:
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['speed_x'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['speed_y'] *= -1
            self.canvas.coords(particle['id'],
                particle['x'] - particle['size'],
                particle['y'] - particle['size'],
                particle['x'] + particle['size'],
                particle['y'] + particle['size'])
        self.canvas.after(50, self.animate)

class EnhancedDatabase:
    def __init__(self):
        # Используем файловую базу данных для сохранения данных
        db_path = "student_collab.db"
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.init_db()
    
    def init_db(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                email TEXT UNIQUE,
                password_hash TEXT,
                password_salt TEXT,
                direction TEXT,
                skills TEXT,
                avatar TEXT DEFAULT '👤',
                bio TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                skills TEXT,
                author_id INTEGER,
                category TEXT DEFAULT 'Другое',
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (author_id) REFERENCES users (id)
            )
            ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_id INTEGER,
                message TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(project_id, user_id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_id INTEGER,
                role TEXT DEFAULT 'member',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                user_id INTEGER,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        self.conn.commit()
    
    def create_user(self, username, email, password, direction, skills='', avatar='👤', bio=''):
        try:
            # Генерируем соль и хешируем пароль
            salt = os.urandom(32).hex()
            password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            
            self.cursor.execute('''
                INSERT INTO users (username, email, password_hash, password_salt, direction, skills, avatar, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, email, password_hash, salt, direction, skills, avatar, bio))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
    
    def verify_password(self, email, password):
        user = self.get_user_by_email(email)
        if not user:
            return False
        
        password_hash = user[3]
        salt = user[4]
        
        # Хешируем введенный пароль с той же солью
        hashed_input = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        
        return hashed_input == password_hash
    
    def get_user_by_email(self, email):
        self.cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        return self.cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        self.cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        return self.cursor.fetchone()
    
    def update_user(self, user_id, username=None, direction=None, skills=None, bio=None):
        try:
            updates = []
            params = []
            
            if username:
                updates.append("username = ?")
                params.append(username)
            if direction:
                updates.append("direction = ?")
                params.append(direction)
            if skills is not None:
                updates.append("skills = ?")
                params.append(skills)
            if bio is not None:
                updates.append("bio = ?")
                params.append(bio)
            
            if not updates:
                return False
            
            params.append(user_id)
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            self.cursor.execute(query, tuple(params))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False
    
    def get_all_projects(self, search_query="", category_filter="all", skills_filter=""):
        query = '''
            SELECT p.*, u.username as author_name 
            FROM projects p 
            LEFT JOIN users u ON p.author_id = u.id 
            WHERE p.status = "open"
        '''
        params = []
        
        if search_query:
            query += " AND (p.title LIKE ? OR p.description LIKE ? OR p.skills LIKE ?)"
            search_term = f"%{search_query}%"
            params.extend([search_term, search_term, search_term])
        
        if category_filter != "all":
            query += " AND p.category = ?"
            params.append(category_filter)
        
        if skills_filter:
            query += " AND p.skills LIKE ?"
            params.append(f"%{skills_filter}%")
        
        query += " ORDER BY p.created_at DESC"
        
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()
    
    def get_all_categories(self):
        self.cursor.execute('SELECT DISTINCT category FROM projects WHERE category IS NOT NULL ORDER BY category')
        categories = [row[0] for row in self.cursor.fetchall()]
        return ['Все категории'] + categories
    
    def create_project(self, title, description, skills, author_id):
        category = self.detect_category(title, description, skills)
        self.cursor.execute('''
            INSERT INTO projects (title, description, skills, author_id, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, skills, author_id, category))
        self.conn.commit()
        project_id = self.cursor.lastrowid
        self.add_project_member(project_id, author_id, 'creator')
        return project_id
    
    def detect_category(self, title, description, skills):
        text = f"{title} {description} {skills}".lower()
        categories = {
            'Веб-разработка': ['веб', 'web', 'сайт', 'frontend', 'backend', 'fullstack', 'html', 'css', 'javascript'],
            'Мобильная разработка': ['мобильн', 'android', 'ios', 'flutter', 'react native', 'приложени'],
            'Дизайн': ['дизайн', 'ui', 'ux', 'figma', 'photoshop', 'графическ', 'интерфейс'],
            'Анализ данных': ['анализ', 'data', 'данн', 'python', 'pandas', 'numpy', 'статистик'],
            'Программирование': ['программир', 'код', 'алгоритм', 'разработк', 'java', 'c++', 'python'],
            'Игры': ['игр', 'unity', 'unreal', 'гейм', 'game'],
            'ИИ и ML': ['ии', 'ai', 'машин', 'нейрон', 'ml', 'tensorflow'],
        }
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in text:
                    return category
        return 'Другое'
    
    def apply_to_project(self, project_id, user_id, message=""):
        try:
            # Проверяем, не подана ли уже заявка
            self.cursor.execute('SELECT id FROM applications WHERE project_id = ? AND user_id = ?', 
                              (project_id, user_id))
            if self.cursor.fetchone():
                return False
                
            self.cursor.execute('''
                INSERT INTO applications (project_id, user_id, message)
                VALUES (?, ?, ?)
            ''', (project_id, user_id, message))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error applying to project: {e}")
            return False
    
    def get_project_members(self, project_id):
        self.cursor.execute('''
            SELECT u.id, u.username, u.avatar, u.direction, pm.role, pm.joined_at
            FROM project_members pm
            JOIN users u ON pm.user_id = u.id
            WHERE pm.project_id = ?
            ORDER BY pm.joined_at
        ''', (project_id,))
        return self.cursor.fetchall()
    
    def add_project_member(self, project_id, user_id, role='member'):
        try:
            self.cursor.execute('''
                INSERT INTO project_members (project_id, user_id, role)
                VALUES (?, ?, ?)
            ''', (project_id, user_id, role))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_project_messages(self, project_id, limit=50):
        self.cursor.execute('''
            SELECT m.*, u.username, u.avatar
            FROM messages m
            JOIN users u ON m.user_id = u.id
            WHERE m.project_id = ?
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (project_id, limit))
        return self.cursor.fetchall()
    
    def add_message(self, project_id, user_id, message):
        try:
            self.cursor.execute('''
                INSERT INTO messages (project_id, user_id, message)
                VALUES (?, ?, ?)
            ''', (project_id, user_id, message))
            self.conn.commit()
            return True
        except:
            return False
    
    def get_user_projects(self, user_id):
        self.cursor.execute('SELECT * FROM projects WHERE author_id = ? ORDER BY created_at DESC', (user_id,))
        return self.cursor.fetchall()
    
    def get_user_applications(self, user_id):
        self.cursor.execute('''
            SELECT 
                a.id,
                a.project_id,
                a.user_id,
                a.message,
                a.status,
                a.created_at,
                p.title,
                p.status as project_status,
                u.username as author_name
            FROM applications a
            JOIN projects p ON a.project_id = p.id
            JOIN users u ON p.author_id = u.id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
        ''', (user_id,))
        return self.cursor.fetchall()

class StudentCollabApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 StudentCollab | ИКТИБ ЮФУ")
        self.root.geometry("1200x700")
        self.db = EnhancedDatabase()
        self.current_user = None
        self.current_user_id = None
        self.colors = ICTIB_COLORS
        
        self.setup_background()
        self.main_container = tk.Frame(self.root, bg='')
        self.main_container.pack(fill='both', expand=True)
        self.show_start_screen()
    
    def setup_background(self):
        self.bg_canvas = tk.Canvas(self.root, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Отложенная инициализация анимации
        self.root.after(100, self.init_background_animation)
        self.root.bind('<Configure>', self.on_resize)
    
    def init_background_animation(self):
        self.bg_animation = FastAnimatedBackground(
            self.bg_canvas, self.root.winfo_width(), self.root.winfo_height()
        )
    
    def on_resize(self, event):
        if event.widget == self.root:
            self.bg_canvas.delete('all')
            self.bg_animation = FastAnimatedBackground(self.bg_canvas, event.width, event.height)
    
    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
    
    def show_start_screen(self):
        self.clear_screen()
        content = tk.Frame(self.main_container, bg='white')
        content.place(relx=0.5, rely=0.5, anchor='center', width=900, height=550)
        
        tk.Label(content, text="🎓 STUDENT COLLAB", font=('Arial', 32, 'bold'),
                bg='white', fg=self.colors['primary']).pack(pady=(30, 10))
        tk.Label(content, text="Фриланс-платформа для студентов ИКТИБ ЮФУ",
                font=('Arial', 14), bg='white', fg=self.colors['dark']).pack(pady=(0, 40))
        
        features = [
            ("👥 Найди команду", "Математик найдет физика"),
            ("💻 Реальные проекты", "Опыт для портфолио"),
            ("💬 Встроенный чат", "Общайтесь в проектах"),
            ("👤 Профили", "Смотрите кто в проекте"),
            ("🎓 Только студенты", "Безопасная среда"),
            ("🚀 Старт карьеры", "Практика в университете")
        ]
        
        for i, (title, desc) in enumerate(features):
            card = tk.Frame(content, bg=self.colors['light'], relief='raised', bd=1)
            card.place(x=50 + (i%3)*280, y=170 + (i//3)*110, width=250, height=90)
            tk.Label(card, text=title, font=('Arial', 11, 'bold'), bg=self.colors['light']).pack(pady=(10, 5))
            tk.Label(card, text=desc, font=('Arial', 9), bg=self.colors['light']).pack()
        
        tk.Button(content, text="🚀 НАЧАТЬ РАБОТУ", font=('Arial', 14, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=40, pady=15,
                 cursor='hand2', command=self.show_login_screen).place(x=350, y=430)
    
    def show_login_screen(self):
        self.clear_screen()
        card = tk.Frame(self.main_container, bg='white', relief='raised', bd=2)
        card.place(relx=0.5, rely=0.5, anchor='center', width=400, height=450)
        
        tk.Label(card, text="🔐 Вход в систему", font=('Arial', 20, 'bold'),
                bg='white', fg=self.colors['primary']).pack(pady=30)
        
        tk.Label(card, text="Email:", font=('Arial', 11), bg='white').pack(anchor='w', padx=50, pady=(10, 5))
        self.email_entry = tk.Entry(card, font=('Arial', 12), width=30)
        self.email_entry.pack(pady=5)
        
        tk.Label(card, text="Пароль:", font=('Arial', 11), bg='white').pack(anchor='w', padx=50, pady=(15, 5))
        self.password_entry = tk.Entry(card, font=('Arial', 12), width=30, show='•')
        self.password_entry.pack(pady=5)
        
        tk.Button(card, text="ВОЙТИ", font=('Arial', 12, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=30, pady=10,
                 command=self.login).pack(pady=20)
        
        tk.Button(card, text="📝 РЕГИСТРАЦИЯ", font=('Arial', 11),
                 bg=self.colors['light'], fg=self.colors['dark'],
                 command=self.show_register_screen).pack(pady=10)

        tk.Button(card, text="← Назад", font=('Arial', 10),
                 bg='white', fg=self.colors['gray'],
                 command=self.show_start_screen).pack(pady=10)
    
    def show_register_screen(self):
        self.clear_screen()
        card = tk.Frame(self.main_container, bg='white', relief='raised', bd=2)
        card.place(relx=0.5, rely=0.5, anchor='center', width=500, height=550)
        
        tk.Label(card, text="📝 Регистрация", font=('Arial', 20, 'bold'),
                bg='white', fg=self.colors['primary']).pack(pady=20)
        
        fields = [("Имя пользователя:", "username"), ("Email:", "email"),
                 ("Пароль:", "password"), ("Направление:", "direction"), ("Навыки:", "skills")]
        
        self.reg_entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(card, text=label, font=('Arial', 11), bg='white').pack(anchor='w', padx=50, pady=(10, 5))
            if key == 'skills':
                entry = tk.Text(card, height=3, font=('Arial', 11), width=40)
                entry.pack(pady=5)
            elif key == 'password':
                entry = tk.Entry(card, font=('Arial', 11), width=40, show='•')
                entry.pack(pady=5)
            else:
                entry = tk.Entry(card, font=('Arial', 11), width=40)
                entry.pack(pady=5)
            self.reg_entries[key] = entry
        
        tk.Button(card, text="✅ ЗАРЕГИСТРИРОВАТЬСЯ", font=('Arial', 12, 'bold'),
                 bg=self.colors['success'], fg='white', padx=30, pady=10,
                 command=self.register).pack(pady=20)
        
        tk.Button(card, text="Отмена", font=('Arial', 11),
                 bg=self.colors['light'], fg=self.colors['dark'],
                 command=self.show_login_screen).pack(pady=5)
    
    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showwarning("Ошибка", "Заполните все поля!")
            return
        
        if self.db.verify_password(email, password):
            user = self.db.get_user_by_email(email)
            self.current_user = user[1]
            self.current_user_id = user[0]
            self.show_main_screen()
        else:
            messagebox.showerror("Ошибка", "Неверные данные! Создайте аккаунт.")
    
    def register(self):
        data = {}
        for key, entry in self.reg_entries.items():
            if key == 'skills':
                data[key] = entry.get("1.0", tk.END).strip()
            else:
                data[key] = entry.get().strip()
        
        required = ['username', 'email', 'password', 'direction']
        for field in required:
            if not data[field]:
                messagebox.showerror("Ошибка", f"Заполните {field}!")
                return
        
        if len(data['password']) < 6:
            messagebox.showerror("Ошибка", "Пароль < 6 символов!")
            return
        
        user_id = self.db.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            direction=data['direction'],
            skills=data.get('skills', '')
        )
        
        if user_id:
            self.current_user = data['username']
            self.current_user_id = user_id
            self.show_main_screen()
            messagebox.showinfo("Успех", "Регистрация завершена!")
        else:
            messagebox.showerror("Ошибка", "Email или имя пользователя уже используется!")
    
    def show_main_screen(self):
        self.clear_screen()
        
        header = tk.Frame(self.main_container, bg=self.colors['primary'], height=60)
        header.pack(fill='x')
        
        tk.Label(header, text=f"👋 {self.current_user} | ИКТИБ ЮФУ",
                font=('Arial', 14, 'bold'), bg=self.colors['primary'],
                fg='white').pack(side='left', padx=20, pady=20)
        
        tk.Button(header, text="👤 Профиль", font=('Arial', 10),
                 bg='white', fg=self.colors['primary'],
                 command=self.show_profile).pack(side='right', padx=5, pady=20)
        
        tk.Button(header, text="Выйти", font=('Arial', 10),
                 bg='white', fg=self.colors['primary'],
                 command=self.show_start_screen).pack(side='right', padx=20, pady=20)
        
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.create_projects_tab()
        self.create_messenger_tab()
        self.create_my_tab()
        self.create_new_tab()
    
    def show_profile(self):
        if not self.current_user_id:
            return
        
        user_data = self.db.get_user_by_id(self.current_user_id)
        if not user_data:
            return
        
        profile_window = tk.Toplevel(self.root)
        profile_window.title("👤 Мой профиль")
        profile_window.geometry("400x500")
        profile_window.configure(bg='white')
        profile_window.resizable(False, False)
        
        # Основная информация (только для чтения)
        tk.Label(profile_window, text=user_data[1], font=('Arial', 20, 'bold'),
                bg='white', fg=self.colors['primary']).pack(pady=20)
        
        tk.Label(profile_window, text=f"Email: {user_data[2]}",
                font=('Arial', 11), bg='white').pack(pady=5)
        tk.Label(profile_window, text=f"Дата регистрации: {user_data[9].split()[0]}",
                font=('Arial', 11), bg='white').pack(pady=5)
        
        # Редактируемые поля
        edit_frame = tk.Frame(profile_window, bg='white')
        edit_frame.pack(pady=20, padx=20, fill='x')
        
        # Направление
        tk.Label(edit_frame, text="Направление:", font=('Arial', 11), bg='white').pack(anchor='w')
        direction_var = tk.StringVar(value=user_data[5] if user_data[5] else '')
        direction_entry = tk.Entry(edit_frame, font=('Arial', 11), textvariable=direction_var, width=40)
        direction_entry.pack(fill='x', pady=(5, 15))
        
        # Навыки
        tk.Label(edit_frame, text="Навыки:", font=('Arial', 11), bg='white').pack(anchor='w')
        skills_text = tk.Text(edit_frame, height=4, font=('Arial', 11), width=40)
        skills_text.insert('1.0', user_data[6] if user_data[6] else '')
        skills_text.pack(fill='x', pady=(5, 15))
        
        # О себе
        tk.Label(edit_frame, text="О себе:", font=('Arial', 11), bg='white').pack(anchor='w')
        bio_text = tk.Text(edit_frame, height=4, font=('Arial', 11), width=40)
        bio_text.insert('1.0', user_data[8] if user_data[8] else '')
        bio_text.pack(fill='x', pady=(5, 15))
        
        def save_changes():
            direction = direction_var.get().strip()
            skills = skills_text.get("1.0", tk.END).strip()
            bio = bio_text.get("1.0", tk.END).strip()
            
            success = self.db.update_user(
                user_id=self.current_user_id,
                direction=direction,
                skills=skills,
                bio=bio
            )
            
            if success:
                messagebox.showinfo("Успех", "Изменения сохранены!")
                profile_window.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось сохранить изменения!")
        
        tk.Button(profile_window, text="💾 Сохранить изменения", font=('Arial', 12),
                 bg=self.colors['success'], fg='white',
                 command=save_changes).pack(pady=20)
        
        # Статистика
        stats_frame = tk.Frame(profile_window, bg=self.colors['light'], relief='raised', bd=1)
        stats_frame.pack(pady=20, padx=20, fill='x')
        
        projects = self.db.get_user_projects(self.current_user_id)
        applications = self.db.get_user_applications(self.current_user_id)
        
        tk.Label(stats_frame, text=f"📁 Создано проектов: {len(projects)}",
                font=('Arial', 11), bg=self.colors['light']).pack(pady=5)
        tk.Label(stats_frame, text=f"📝 Подано заявок: {len(applications)}",
                font=('Arial', 11), bg=self.colors['light']).pack(pady=5)
    
    def create_projects_tab(self):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text='🔍 Проекты')
        
        # Панель поиска и фильтров
        filter_frame = tk.Frame(tab, bg=self.colors['light'], height=60)
        filter_frame.pack(fill='x', padx=10, pady=10)
        filter_frame.pack_propagate(False)
        
        # Поисковая строка
        search_frame = tk.Frame(filter_frame, bg=self.colors['light'])
        search_frame.pack(side='left', padx=(20, 10), pady=10)
        
        tk.Label(search_frame, text="Поиск:", font=('Arial', 11), bg=self.colors['light']).pack(side='left')
        self.search_entry = tk.Entry(search_frame, font=('Arial', 11), width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<Return>', lambda e: self.refresh_projects_tab())
        
        # Фильтр по категориям
        category_frame = tk.Frame(filter_frame, bg=self.colors['light'])
        category_frame.pack(side='left', padx=10, pady=10)
        
        tk.Label(category_frame, text="Категория:", font=('Arial', 11), bg=self.colors['light']).pack(side='left')
        self.category_var = tk.StringVar(value="Все категории")
        categories = self.db.get_all_categories()
        category_menu = ttk.Combobox(category_frame, textvariable=self.category_var, 
                                    values=categories, state='readonly', width=20)
        category_menu.pack(side='left', padx=5)
        category_menu.bind('<<ComboboxSelected>>', lambda e: self.refresh_projects_tab())
        
        # Фильтр по навыкам
        skills_frame = tk.Frame(filter_frame, bg=self.colors['light'])
        skills_frame.pack(side='left', padx=10, pady=10)
        
        tk.Label(skills_frame, text="Навыки:", font=('Arial', 11), bg=self.colors['light']).pack(side='left')
        self.skills_entry = tk.Entry(skills_frame, font=('Arial', 11), width=20)
        self.skills_entry.pack(side='left', padx=5)
        self.skills_entry.bind('<Return>', lambda e: self.refresh_projects_tab())
        
        # Кнопка поиска
        tk.Button(filter_frame, text="🔍 Поиск", font=('Arial', 11),
                  bg=self.colors['primary'], fg='white',
                 command=self.refresh_projects_tab).pack(side='left', padx=10, pady=10)
        
        # Кнопка сброса
        tk.Button(filter_frame, text="❌ Сброс", font=('Arial', 11),
                 bg=self.colors['light'], fg=self.colors['dark'],
                 command=self.reset_filters).pack(side='left', padx=10, pady=10)
        
        # Контейнер для проектов
        self.projects_container = tk.Frame(tab, bg='white')
        self.projects_container.pack(fill='both', expand=True)
        
        self.refresh_projects_tab()
    
    def refresh_projects_tab(self):
        # Очищаем контейнер
        for widget in self.projects_container.winfo_children():
            widget.destroy()
        
        # Получаем фильтры
        search_query = self.search_entry.get().strip()
        category_filter = self.category_var.get()
        skills_filter = self.skills_entry.get().strip()
        
        if category_filter == "Все категории":
            category_filter = "all"
        
        # Получаем проекты с фильтрами
        projects = self.db.get_all_projects(search_query, category_filter, skills_filter)
        
        if not projects:
            no_projects_frame = tk.Frame(self.projects_container, bg='white')
            no_projects_frame.place(relx=0.5, rely=0.5, anchor='center')
            
            tk.Label(no_projects_frame, text="📭 Проекты не найдены",
                    font=('Arial', 16), bg='white').pack(pady=10)
            tk.Label(no_projects_frame, text="Попробуйте изменить параметры поиска",
                    font=('Arial', 12), bg='white', fg=self.colors['gray']).pack()
            return
        
        # Создаем Canvas для прокрутки
        canvas = tk.Canvas(self.projects_container, bg='white')
        scrollbar = tk.Scrollbar(self.projects_container, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='white')
        
        scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Группируем проекты по категориям
        projects_by_category = {}
        for project in projects:
            pid, title, desc, skills, author_id, category, status, created_at, author_name = project
            if category not in projects_by_category:
                projects_by_category[category] = []
            projects_by_category[category].append(project)
        
        # Отображаем проекты по категориям
        for category, category_projects in projects_by_category.items():
            tk.Label(scroll_frame, text=f"📂 {category}",
                    font=('Arial', 14, 'bold'), bg='white').pack(anchor='w', padx=20, pady=(20, 10))
            
            row_frame = None
            for i, project in enumerate(category_projects):
                if i % 2 == 0:
                    row_frame = tk.Frame(scroll_frame, bg='white')
                    row_frame.pack(fill='x', padx=20, pady=5)
                
                pid, title, desc, skills, author_id, category, status, created_at, author_name = project
                
                card = tk.Frame(row_frame, bg='white', relief='raised', bd=1, width=350, height=120)
                card.pack(side='left', padx=5, pady=5)
                card.pack_propagate(False)
                
                tk.Label(card, text=title[:30] + "..." if len(title) > 30 else title,
                        font=('Arial', 12, 'bold'), bg='white',
                        fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(10, 5))
                
                tk.Label(card, text=desc[:60] + "..." if len(desc) > 60 else desc,
                        font=('Arial', 9), bg='white', wraplength=300).pack(anchor='w', padx=10)
                
                tk.Label(card, text=f"👤 {author_name} | 📅 {created_at.split()[0]}",
                        font=('Arial', 9), bg='white', fg=self.colors['gray']).pack(anchor='w', padx=10, pady=5)
                
                skills_label = tk.Label(card, text=f"🛠️ {skills[:40]}..." if len(skills) > 40 else f"🛠️ {skills}",
                                      font=('Arial', 8), bg='white', fg=self.colors['secondary'])
                skills_label.pack(anchor='w', padx=10)
                
                if self.current_user_id:
                    tk.Button(card, text="Подать заявку", bg=self.colors['success'],
                             fg='white', font=('Arial', 9),
                             command=lambda p=pid: self.apply_to_project(p)).pack(side='right', padx=10, pady=5)
        
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def reset_filters(self):
        self.search_entry.delete(0, tk.END)
        self.category_var.set("Все категории")
        self.skills_entry.delete(0, tk.END)
        self.refresh_projects_tab()
    
    def create_messenger_tab(self):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text='💬 Чат')
        
        self.messenger_tab = tab
        
        # Панель с проектами слева
        left_panel = tk.Frame(tab, bg=self.colors['light'], width=250)
        left_panel.pack(side='left', fill='y')
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Мои проекты:", font=('Arial', 12, 'bold'),
                bg=self.colors['light'], fg=self.colors['dark']).pack(pady=10)
        
        # Контейнер для списка проектов
        self.projects_list_frame = tk.Frame(left_panel, bg=self.colors['light'])
        self.projects_list_frame.pack(fill='both', expand=True, padx=10)
        
        # Правая панель - чат
        self.chat_panel = tk.Frame(tab, bg='white')
        self.chat_panel.pack(side='right', fill='both', expand=True)
        
        # Загружаем список проектов пользователя
        self.load_messenger_projects()
    
    def load_messenger_projects(self):
        """Загружает список проектов в мессенджер"""
        # Очищаем старый список
        for widget in self.projects_list_frame.winfo_children():
            widget.destroy()
        
        # Очищаем панель чата
        for widget in self.chat_panel.winfo_children():
            widget.destroy()
        
        if not self.current_user_id:
            tk.Label(self.projects_list_frame,
                    text="Войдите в систему",
                    font=('Arial', 10), bg=self.colors['light'],
                    fg=self.colors['gray']).pack(pady=20)
            
            tk.Label(self.chat_panel,
                    text="Войдите в систему для доступа к чату",
                    font=('Arial', 14), bg='white', fg=self.colors['gray']).place(relx=0.5, rely=0.5, anchor='center')
            return
        
        # Получаем проекты пользователя
        user_projects = self.db.get_user_projects(self.current_user_id)
        
        if user_projects:
            for project in user_projects:
                pid, title, desc, skills, author_id, category, status, created_at = project
                
                btn = tk.Button(self.projects_list_frame,
                               text=f"📁 {title[:20]}..." if len(title) > 20 else f"📁 {title}",
                               font=('Arial', 10), bg='white', fg=self.colors['dark'],
                               relief='flat', cursor='hand2',
                               command=lambda p=pid, t=title: self.load_project_chat(p, t))
                btn.pack(fill='x', pady=5, padx=5)
        else:
            tk.Label(self.projects_list_frame,
                    text="У вас нет проектов",
                    font=('Arial', 10), bg=self.colors['light'],
                    fg=self.colors['gray']).pack(pady=20)
            tk.Label(self.projects_list_frame,
                    text="Создайте проект, чтобы начать общение",
                    font=('Arial', 9), bg=self.colors['light'],
                    fg=self.colors['gray']).pack()
        
        # Показываем сообщение по умолчанию в чате
        self.show_default_chat_message()
    
    def show_default_chat_message(self):
        """Показывает сообщение по умолчанию в чате"""
        # Очищаем панель чата
        for widget in self.chat_panel.winfo_children():
            widget.destroy()
        
        tk.Label(self.chat_panel,
                text="Выберите проект для общения",
                font=('Arial', 14), bg='white', fg=self.colors['gray']).place(relx=0.5, rely=0.5, anchor='center')
    
    def load_project_chat(self, project_id, project_title):
        """Загружает чат выбранного проекта"""
        # Очищаем панель чата
        for widget in self.chat_panel.winfo_children():
            widget.destroy()
        
        # Заголовок чата
        chat_header = tk.Frame(self.chat_panel, bg=self.colors['primary_light'])
        chat_header.pack(fill='x', pady=(0, 5))
        
        tk.Label(chat_header,
                text=f"💬 Чат проекта: {project_title}",
                font=('Arial', 12, 'bold'),
                bg=self.colors['primary_light'],
                fg='white',
                pady=10).pack()
        
        # Область сообщений
        messages_frame = tk.Frame(self.chat_panel, bg='white')
        messages_frame.pack(fill='both', expand=True)
        
        # Контейнер для сообщений с прокруткой
        messages_canvas = tk.Canvas(messages_frame, bg='white')
        messages_scrollbar = tk.Scrollbar(messages_frame, orient='vertical', command=messages_canvas.yview)
        messages_container = tk.Frame(messages_canvas, bg='white')
        
        messages_canvas.create_window((0, 0), window=messages_container, anchor='nw')
        messages_canvas.configure(yscrollcommand=messages_scrollbar.set)
        
        messages_canvas.pack(side='left', fill='both', expand=True)
        messages_scrollbar.pack(side='right', fill='y')
        
        # Загружаем сообщения
        messages = self.db.get_project_messages(project_id)
        
        if messages:
            for msg in reversed(messages):
                msg_id, project_id, user_id, message, created_at, username, avatar = msg
                
                if user_id == self.current_user_id:
                    bg_color = self.colors['primary_light']
                    fg_color = 'white'
                    anchor = 'e'
                else:
                    bg_color = self.colors['light']
                    fg_color = self.colors['dark']
                    anchor = 'w'
                
                # Создаем фрейм сообщения
                message_frame = tk.Frame(messages_container, bg='white')
                message_frame.pack(fill='x', padx=10, pady=5, anchor=anchor)
                
                inner_frame = tk.Frame(message_frame, bg=bg_color, relief='raised', bd=1)
                inner_frame.pack()
                
                header_frame = tk.Frame(inner_frame, bg=bg_color)
                header_frame.pack(fill='x', padx=10, pady=(5, 0))
                
                tk.Label(header_frame, text=avatar, font=('Arial', 12),
                        bg=bg_color, fg=fg_color).pack(side='left')
                
                tk.Label(header_frame, text=username, font=('Arial', 10, 'bold'),
                        bg=bg_color, fg=fg_color).pack(side='left', padx=5)
                
                time_str = created_at.split()[1][:5] if ' ' in created_at else created_at[:5]
                tk.Label(header_frame, text=time_str,
                        font=('Arial', 9), bg=bg_color, fg=fg_color).pack(side='right')
                
                tk.Label(inner_frame, text=message, font=('Arial', 11),
                        bg=bg_color, fg=fg_color, wraplength=400).pack(padx=10, pady=5)
        else:
            tk.Label(messages_container,
                    text="В чате пока нет сообщений",
                    font=('Arial', 12), bg='white',
                    fg=self.colors['gray']).pack(pady=20)
        
        # Панель ввода сообщения
        input_frame = tk.Frame(self.chat_panel, bg=self.colors['light'])
        input_frame.pack(fill='x', pady=(5, 0))
        
        # Кнопка скрепки
        def show_whiteboard_popup():
            popup = tk.Toplevel(self.root)
            popup.title("Интерактивная доска")
            popup.geometry("300x150")
            popup.configure(bg='white')
            
            tk.Label(popup, text="🖌️ Интерактивная доска", 
                    font=('Arial', 14, 'bold'), bg='white',
                    fg=self.colors['primary']).pack(pady=20)
            
            tk.Label(popup, text="Функция в разработке", 
                    font=('Arial', 12), bg='white').pack(pady=10)
            
            tk.Button(popup, text="Закрыть", font=('Arial', 11),
                     bg=self.colors['primary'], fg='white',
                     command=popup.destroy).pack(pady=10)
        
        tk.Button(input_frame, text="📎", font=('Arial', 14),
                 bg=self.colors['light'], fg=self.colors['dark'],
                 relief='flat', cursor='hand2',
                 command=show_whiteboard_popup).pack(side='left', padx=5, pady=5)
        
        message_entry = tk.Entry(input_frame, font=('Arial', 11), bg='white')
        message_entry.pack(side='left', fill='x', expand=True, padx=(5, 0), pady=5)
        message_entry.bind('<Return>', lambda e: self.send_chat_message(project_id, message_entry))
        
        tk.Button(input_frame, text="Отправить", font=('Arial', 11),
                 bg=self.colors['primary'], fg='white',
                 command=lambda: self.send_chat_message(project_id, message_entry)).pack(side='right', padx=5, pady=5)
    
    def send_chat_message(self, project_id, message_entry):
        """Отправляет сообщение в чат"""
        if not self.current_user_id:
            messagebox.showwarning("Ошибка", "Войдите в систему!")
            return
        
        message = message_entry.get().strip()
        if not message:
            return
        
        # Сохраняем в БД
        success = self.db.add_message(project_id, self.current_user_id, message)
        
        if success:
            message_entry.delete(0, tk.END)
            # Перезагружаем чат с текущим проектом
            projects = self.db.get_user_projects(self.current_user_id)
            for project in projects:
                if project[0] == project_id:
                    self.load_project_chat(project_id, project[1])
                    break
    
    def create_my_tab(self):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text='📁 Мои')
        
        # Создаем контейнер для контента
        my_content = tk.Frame(tab, bg='white')
        my_content.pack(fill='both', expand=True)
        
        if not self.current_user_id:
            tk.Label(my_content, text="Войдите в систему",
                    font=('Arial', 14), bg='white').place(relx=0.5, rely=0.5, anchor='center')
            return
        
        # Вкладки внутри "Мои"
        my_notebook = ttk.Notebook(my_content)
        my_notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Мои проекты
        my_projects_tab = tk.Frame(my_notebook)
        my_notebook.add(my_projects_tab, text='Мои проекты')
        
        projects = self.db.get_user_projects(self.current_user_id)
        if projects:
            canvas = tk.Canvas(my_projects_tab, bg='white')
            scrollbar = tk.Scrollbar(my_projects_tab, orient='vertical', command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg='white')
            
            scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for project in projects:
                pid, title, desc, skills, author_id, category, status, created_at = project
                
                card = tk.Frame(scroll_frame, bg='white', relief='raised', bd=1)
                card.pack(fill='x', padx=20, pady=10)
                
                tk.Label(card, text=title, font=('Arial', 14, 'bold'),
                        bg='white', fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(10, 5))
                
                tk.Label(card, text=desc[:100] + "..." if len(desc) > 100 else desc,
                        font=('Arial', 11), bg='white', wraplength=700).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(card, text=f"📂 {category} | 📅 {created_at.split()[0]} | 📊 {status}",
                        font=('Arial', 10), bg='white', fg=self.colors['gray']).pack(anchor='w', padx=10, pady=(0, 10))
                
                # Кнопка для открытия чата проекта
                tk.Button(card, text="💬 Открыть чат", bg=self.colors['secondary'],
                         fg='white', command=lambda p=pid, t=title: self.open_project_chat(p, t)).pack(side='right', padx=10, pady=(0, 10))
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        else:
            tk.Label(my_projects_tab, text="🎯 Вы пока не создали проектов",
                    font=('Arial', 14), bg='white').pack(pady=50)
            
            tk.Label(my_projects_tab, text="💡 Создайте свой первый проект!",
                    font=('Arial', 12), bg='white', fg=self.colors['gray']).pack(pady=10)
            
            tk.Button(my_projects_tab, text="➡️ Создать проект",
                     font=('Arial', 12), bg=self.colors['primary'], fg='white',
                     command=lambda: self.notebook.select(3)).pack(pady=10)
        
        # Мои заявки
        my_apps_tab = tk.Frame(my_notebook)
        my_notebook.add(my_apps_tab, text='Мои заявки')
        
        applications = self.db.get_user_applications(self.current_user_id)
        if applications:
            canvas = tk.Canvas(my_apps_tab, bg='white')
            scrollbar = tk.Scrollbar(my_apps_tab, orient='vertical', command=canvas.yview)
            scroll_frame = tk.Frame(canvas, bg='white')
            
            scroll_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
            canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
            canvas.configure(yscrollcommand=scrollbar.set)
            
            for app in applications:
                # Распаковываем кортеж с правильными индексами
                app_id = app[0]
                project_id = app[1]
                user_id = app[2]
                message = app[3]
                status = app[4]
                created_at = app[5]
                project_title = app[6]
                project_status = app[7]
                author_name = app[8]
                
                card = tk.Frame(scroll_frame, bg='white', relief='raised', bd=1)
                card.pack(fill='x', padx=20, pady=10)
                
                if status == 'accepted':
                    status_color = self.colors['success']
                elif status == 'rejected':
                    status_color = self.colors['accent']
                else:
                    status_color = self.colors['warning']
                
                tk.Label(card, text=f"Проект: {project_title}", 
                        font=('Arial', 14, 'bold'), bg='white',
                        fg=self.colors['primary']).pack(anchor='w', padx=10, pady=(10, 5))
                
                tk.Label(card, text=f"Автор: {author_name}",
                        font=('Arial', 11), bg='white').pack(anchor='w', padx=10, pady=5)
                
                if message:
                    tk.Label(card, text=f"Ваше сообщение: {message}",
                            font=('Arial', 11), bg='white', wraplength=700).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(card, text=f"📅 Подана: {created_at.split()[0]} | 📊 Статус: {status}",
                        font=('Arial', 10), bg='white', fg=status_color).pack(anchor='w', padx=10, pady=(0, 10))
            
            canvas.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')
        else:
            tk.Label(my_apps_tab, text="📝 У вас пока нет заявок",
                    font=('Arial', 14), bg='white').pack(pady=50)
            
            tk.Label(my_apps_tab, text="💡 Подайте заявку на интересный проект!",
                    font=('Arial', 12), bg='white', fg=self.colors['gray']).pack(pady=10)
    
    def open_project_chat(self, project_id, project_title):
        """Открывает чат проекта"""
        # Переключаемся на вкладку чата
        self.notebook.select(1)  # Вкладка чата
        
        # Загружаем чат проекта
        self.load_project_chat(project_id, project_title)
    
    def create_new_tab(self):
        tab = tk.Frame(self.notebook)
        self.notebook.add(tab, text='➕ Создать')
        
        tk.Label(tab, text="Создание проекта", font=('Arial', 16, 'bold'),
                fg=self.colors['primary']).pack(pady=20)
        
        tk.Label(tab, text="Название:", font=('Arial', 12)).pack(anchor='w', padx=50, pady=(10, 5))
        title_entry = tk.Entry(tab, font=('Arial', 12), width=50)
        title_entry.pack(pady=5)
        
        tk.Label(tab, text="Описание:", font=('Arial', 12)).pack(anchor='w', padx=50, pady=(10, 5))
        desc_text = tk.Text(tab, height=8, font=('Arial', 11), width=50)
        desc_text.pack(pady=5)

        tk.Label(tab, text="Навыки (через запятую):", font=('Arial', 12)).pack(anchor='w', padx=50, pady=(10, 5))
        skills_entry = tk.Entry(tab, font=('Arial', 12), width=50)
        skills_entry.pack(pady=5)
        
        def create_project():
            title = title_entry.get().strip()
            desc = desc_text.get("1.0", tk.END).strip()
            skills = skills_entry.get().strip()
            
            if not title or not desc:
                messagebox.showerror("Ошибка", "Заполните название и описание!")
                return
            
            # Создаем проект
            project_id = self.db.create_project(title, desc, skills, self.current_user_id)
            
            if project_id:
                # Очищаем форму
                title_entry.delete(0, tk.END)
                desc_text.delete('1.0', tk.END)
                skills_entry.delete(0, tk.END)
                
                # Показываем сообщение об успехе
                messagebox.showinfo("Успех", f"Проект '{title}' создан!")
                
                # Обновляем все вкладки
                self.refresh_all_tabs()
                
                # Переключаемся на вкладку "Мои проекты"
                self.notebook.select(2)  # Вкладка "Мои"
            else:
                messagebox.showerror("Ошибка", "Не удалось создать проект!")
        
        tk.Button(tab, text="🚀 ОПУБЛИКОВАТЬ", font=('Arial', 14, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=30, pady=15,
                 command=create_project).pack(pady=30)
    
    def apply_to_project(self, project_id):
        if not self.current_user_id:
            messagebox.showwarning("Ошибка", "Войдите в систему!")
            return
        
        # Проверяем, существует ли проект
        self.db.cursor.execute('SELECT id FROM projects WHERE id = ?', (project_id,))
        if not self.db.cursor.fetchone():
            messagebox.showerror("Ошибка", "Проект не найден!")
            return
        
        success = self.db.apply_to_project(project_id, self.current_user_id, "Хочу участвовать!")
        if success:
            messagebox.showinfo("Успех", "Заявка подана!")
            self.refresh_all_tabs()
        else:
            messagebox.showwarning("Внимание", "Вы уже подали заявку на этот проект!")
    
    def refresh_all_tabs(self):
        """Обновляет все вкладки главного окна"""
        # Сохраняем текущую вкладку
        current_tab = self.notebook.index("current")
        
        # Удаляем все вкладки
        for i in range(self.notebook.index("end") - 1, -1, -1):
            self.notebook.forget(i)
        
        # Создаем новые вкладки
        self.create_projects_tab()
        self.create_messenger_tab()
        self.create_my_tab()
        self.create_new_tab()
        
        # Восстанавливаем выбранную вкладку
        if current_tab < self.notebook.index("end"):
            self.notebook.select(current_tab)
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = StudentCollabApp()
    app.run()