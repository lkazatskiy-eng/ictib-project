from datetime import datetime
from database import db

# Таблица для связи многие-ко-многим: мероприятия-участники
event_participants = db.Table('event_participants',
                              db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                              db.Column('event_id', db.Integer, db.ForeignKey('event.id'), primary_key=True),
                              db.Column('joined_at', db.DateTime, default=datetime.utcnow)
                              )

# Таблица для связи многие-ко-многим: проект-участники
project_members = db.Table('project_members',
                           db.Column('project_id', db.Integer, db.ForeignKey('project.id'), primary_key=True),
                           db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
                           db.Column('role', db.String(100)),
                           db.Column('joined_at', db.DateTime, default=datetime.utcnow)
                           )


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    bio = db.Column(db.Text, default='')

    # Навыки и интересы храним как JSON строку для простоты
    skills = db.Column(db.Text, nullable=False, default='[]')  # JSON список
    interests = db.Column(db.Text, nullable=False, default='[]')  # JSON список

    # Статусы пользователя
    status = db.Column(db.String(50), nullable=False, default='active')
    collaboration_status = db.Column(db.String(100), default='')  # "Хочу сотрудничать", "Ищу команду" и т.д.
    looking_for_project = db.Column(db.Boolean, default=False)
    looking_for_team = db.Column(db.Boolean, default=False)

    # Рейтинг для геймификации
    rating = db.Column(db.Integer, default=100)
    achievements = db.Column(db.Text, default='[]')  # JSON список достижений

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'bio': self.bio,
            'skills': self.skills,
            'interests': self.interests,
            'status': self.status,
            'collaboration_status': self.collaboration_status,
            'looking_for_project': self.looking_for_project,
            'looking_for_team': self.looking_for_team,
            'rating': self.rating,
            'achievements': self.achievements,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_skills_list(self):
        import json
        return json.loads(self.skills) if self.skills else []

    def get_interests_list(self):
        import json
        return json.loads(self.interests) if self.interests else []


class Event(db.Model):
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), default='lecture')

    # Даты
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    registration_deadline = db.Column(db.DateTime)

    # Место проведения
    location = db.Column(db.String(200))
    online_link = db.Column(db.String(500))

    # Ограничения
    max_participants = db.Column(db.Integer, default=0)  # 0 = без ограничений
    is_public = db.Column(db.Boolean, default=True)

    # Теги для поиска
    tags = db.Column(db.Text, default='[]')  # JSON список

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    participants = db.relationship('User', secondary=event_participants,
                                   backref=db.backref('events_attending', lazy='dynamic'))

    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    organizer = db.relationship('User', backref='organized_events')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'location': self.location,
            'online_link': self.online_link,
            'max_participants': self.max_participants,
            'is_public': self.is_public,
            'tags': self.tags,
            'organizer_id': self.organizer_id,
            'participant_count': len(self.participants),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_tags_list(self):
        import json
        return json.loads(self.tags) if self.tags else []


class Project(db.Model):
    __tablename__ = 'project'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    goals = db.Column(db.Text)

    # Необходимые навыки и роли
    required_skills = db.Column(db.Text, default='[]')  # JSON список
    required_roles = db.Column(db.Text, default='[]')  # JSON список

    # Статус проекта
    status = db.Column(db.String(50), default='planning')  # planning, active, completed, archived
    is_public = db.Column(db.Boolean, default=True)

    # Контакты
    contact_info = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связи
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User', backref='owned_projects')

    tags = db.Column(db.Text, default='[]')  # JSON список

    members = db.relationship('User', secondary=project_members,
                              backref=db.backref('projects_participating', lazy='dynamic'))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'goals': self.goals,
            'required_skills': self.required_skills,
            'required_roles': self.required_roles,
            'status': self.status,
            'is_public': self.is_public,
            'contact_info': self.contact_info,
            'owner_id': self.owner_id,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class MatchScore(db.Model):
    __tablename__ = 'match_score'

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    user2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)

    # Разные типы совпадений
    skill_match = db.Column(db.Float, default=0.0)
    interest_match = db.Column(db.Float, default=0.0)
    event_match = db.Column(db.Float, default=0.0)  # Посещали одни мероприятия
    project_match = db.Column(db.Float, default=0.0)  # Участвовали в одних проектах

    # Общий балл
    total_score = db.Column(db.Float, default=0.0)

    # Причина совпадения
    match_reason = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Уникальный индекс для пары пользователей
    __table_args__ = (
        db.UniqueConstraint('user1_id', 'user2_id', name='unique_user_pair'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user1_id': self.user1_id,
            'user2_id': self.user2_id,
            'skill_match': self.skill_match,
            'interest_match': self.interest_match,
            'event_match': self.event_match,
            'project_match': self.project_match,
            'total_score': self.total_score,
            'match_reason': self.match_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Achievement(db.Model):
    __tablename__ = 'achievement'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(200))
    points = db.Column(db.Integer, default=10)
    condition = db.Column(db.String(200))  # Условие получения
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'points': self.points,
            'condition': self.condition,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserAchievement(db.Model):
    __tablename__ = 'user_achievement'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи - исправленные
    user = db.relationship('User', backref='earned_achievements_rel')
    achievement = db.relationship('Achievement', backref='user_achievements')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='unique_user_achievement'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'achievement': self.achievement.to_dict() if self.achievement else None
        }