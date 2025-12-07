import sys
import json
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPainter, QPen, QColor, QPixmap, QFontMetrics
from database import Database


class SimpleDrawingCanvas(QWidget):
    """Холст для рисования и текста"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ddd;
            }
        """)

        # Настройки рисования
        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor(0, 0, 255)  # Синий
        self.pen_width = 3

        # Настройки текста
        self.text_mode = False
        self.current_text = ""
        self.text_position = QPoint()
        self.text_color = QColor(0, 0, 0)  # Черный для текста по умолчанию
        self.text_font = QFont("Arial", 16)
        self.text_input_active = False

        # Инициализация холста
        self.canvas = QPixmap(self.size())
        self.canvas.fill(Qt.GlobalColor.white)

    def paintEvent(self, event):
        """Отрисовка холста"""
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.canvas)

        # Если в режиме ввода текста, показываем курсор
        if self.text_mode and self.text_input_active:
            painter.setPen(QPen(QColor(0, 0, 0), 1))
            painter.drawRect(self.text_position.x(), self.text_position.y(),
                             self.get_text_width(self.current_text), 20)

    def mousePressEvent(self, event):
        """Начало рисования или размещения текста"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.text_mode:
                # В режиме текста - устанавливаем позицию для текста
                self.text_position = event.pos()
                self.text_input_active = True
                self.show_text_input_dialog()
            else:
                # В режиме рисования - начинаем рисовать
                self.drawing = True
                pos = event.pos()
                self.last_point = QPoint(pos.x(), pos.y())

    def mouseMoveEvent(self, event):
        """Рисование при движении мыши"""
        if not self.text_mode and self.drawing and event.buttons() & Qt.MouseButton.LeftButton:
            current_point = event.pos()

            painter = QPainter(self.canvas)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

            pen = QPen(self.pen_color, self.pen_width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)

            painter.drawLine(self.last_point, current_point)
            painter.end()

            self.last_point = current_point
            self.update()

    def mouseReleaseEvent(self, event):
        """Завершение рисования"""
        if event.button() == Qt.MouseButton.LeftButton and not self.text_mode:
            self.drawing = False
            self.update()

    def clear(self):
        """Очистить холст"""
        self.canvas = QPixmap(self.size())
        self.canvas.fill(Qt.GlobalColor.white)
        self.update()

    def resizeEvent(self, event):
        """Обработчик изменения размера"""
        old_canvas = self.canvas
        self.canvas = QPixmap(self.size())
        self.canvas.fill(Qt.GlobalColor.white)

        painter = QPainter(self.canvas)
        painter.drawPixmap(0, 0, old_canvas)
        painter.end()

        super().resizeEvent(event)

    def set_color(self, color):
        """Установить цвет пера"""
        self.pen_color = QColor(color)

    def set_width(self, width):
        """Установить толщину пера"""
        self.pen_width = width

    def set_text_mode(self, enabled):
        """Включить/выключить режим текста"""
        self.text_mode = enabled
        self.text_input_active = False

    def add_text(self, text, position=None, color=None, font_size=None):
        """Добавить текст на холст"""
        if position is None:
            position = self.text_position

        if color is None:
            color = self.text_color

        if font_size is not None:
            font = QFont(self.text_font)
            font.setPointSize(font_size)
        else:
            font = self.text_font

        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Устанавливаем цвет и шрифт для текста
        painter.setPen(QPen(QColor(color)))
        painter.setFont(font)

        # Рисуем текст
        painter.drawText(position, text)
        painter.end()

        self.update()

    def set_text_color(self, color):
        """Установить цвет текста"""
        self.text_color = QColor(color)

    def set_text_font_size(self, size):
        """Установить размер шрифта текста"""
        self.text_font.setPointSize(size)

    def get_text_width(self, text):
        """Получить ширину текста в пикселях"""
        metrics = QFontMetrics(self.text_font)
        return metrics.horizontalAdvance(text)

    def show_text_input_dialog(self):
        """Показать диалог ввода текста"""
        dialog = TextInputDialog(self)
        if dialog.exec():
            text = dialog.get_text()
            if text:
                # Получаем настройки из диалога
                font_size = dialog.get_font_size()
                color = dialog.get_color()
                # Добавляем текст с настройками
                self.add_text(text, self.text_position, color, font_size)
        self.text_input_active = False


class TextInputDialog(QDialog):
    """Диалог для ввода текста"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите текст")
        self.setModal(True)
        self.resize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Поле ввода текста
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст здесь...")
        self.text_edit.setMaximumHeight(100)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)

        # Настройки текста
        settings_layout = QHBoxLayout()

        # Выбор размера шрифта
        settings_layout.addWidget(QLabel("Размер:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(["12", "14", "16", "18", "20", "24", "28", "32"])
        self.font_size_combo.setCurrentText("16")
        settings_layout.addWidget(self.font_size_combo)

        # Выбор цвета текста
        settings_layout.addWidget(QLabel("Цвет:"))
        self.color_combo = QComboBox()

        # Добавляем цвета с иконками
        colors = [
            ("⚫ Черный", "#000000"),
            ("🔴 Красный", "#FF0000"),
            ("🔵 Синий", "#0000FF"),
            ("🟢 Зеленый", "#00FF00"),
            ("🟣 Фиолетовый", "#800080"),
            ("🟠 Оранжевый", "#FFA500"),
            ("🟡 Желтый", "#FFFF00"),
            ("🔶 Коричневый", "#8B4513")
        ]

        for name, hex_color in colors:
            # Создаем иконку цвета
            pixmap = QPixmap(16, 16)
            pixmap.fill(QColor(hex_color))
            icon = QIcon(pixmap)
            self.color_combo.addItem(icon, name, hex_color)

        self.color_combo.setCurrentIndex(0)  # Черный по умолчанию
        settings_layout.addWidget(self.color_combo)

        settings_layout.addStretch()
        layout.addLayout(settings_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Добавить текст")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Стилизация кнопок
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

    def get_text(self):
        """Получить введенный текст"""
        return self.text_edit.toPlainText().strip()

    def get_font_size(self):
        """Получить выбранный размер шрифта"""
        return int(self.font_size_combo.currentText())

    def get_color(self):
        """Получить выбранный цвет"""
        # Получаем hex-код цвета из данных комбобокса
        hex_color = self.color_combo.currentData()
        if hex_color:
            return hex_color
        return "#000000"  # Черный по умолчанию


class WhiteboardTab(QWidget):
    """Вкладка с интерактивной доской"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель инструментов
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Группа инструментов
        tools_group = QButtonGroup(self)

        # Кнопка инструмента "Рисование"
        self.draw_btn = QPushButton("✏️ Рисовать")
        self.draw_btn.setCheckable(True)
        self.draw_btn.setChecked(True)
        self.draw_btn.setFixedSize(120, 40)
        self.draw_btn.clicked.connect(self.set_draw_mode)
        tools_group.addButton(self.draw_btn)

        # Кнопка инструмента "Текст"
        self.text_btn = QPushButton("🔤 Текст")
        self.text_btn.setCheckable(True)
        self.text_btn.setFixedSize(100, 40)
        self.text_btn.clicked.connect(self.set_text_mode)
        tools_group.addButton(self.text_btn)

        toolbar.addWidget(self.draw_btn)
        toolbar.addWidget(self.text_btn)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #ddd; width: 1px; margin: 0 10px;")
        toolbar.addWidget(separator)

        # Кнопки цвета для рисования
        colors_data = [
            ("🔴", "#FF0000", "Красный"),
            ("🟢", "#00FF00", "Зеленый"),
            ("🔵", "#0000FF", "Синий"),
            ("⚫", "#000000", "Черный"),
            ("🟣", "#800080", "Фиолетовый"),
            ("🟠", "#FFA500", "Оранжевый")
        ]

        # Создаем кнопки цветов
        for emoji, hex_color, tooltip in colors_data:
            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.setToolTip(tooltip)

            def make_color_handler(color_hex):
                def handler():
                    color = QColor(color_hex)
                    self.set_color(color)

                return handler

            btn.clicked.connect(make_color_handler(hex_color))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    color: white;
                    border-radius: 20px;
                    font-size: 16px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    border: 2px solid #3498db;
                }}
            """)
            toolbar.addWidget(btn)

        # Кнопки толщины
        widths_data = [("1px", 1), ("3px", 3), ("5px", 5), ("8px", 8), ("12px", 12)]

        for text, width in widths_data:
            btn = QPushButton(text)
            btn.setFixedSize(60, 40)

            def make_width_handler(w):
                def handler():
                    self.set_width(w)

                return handler

            btn.clicked.connect(make_width_handler(width))

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            toolbar.addWidget(btn)

        toolbar.addStretch()

        # Кнопка очистки
        self.clear_btn = QPushButton("🧹 Очистить")
        self.clear_btn.clicked.connect(self.clear_board)
        self.clear_btn.setFixedSize(120, 40)
        toolbar.addWidget(self.clear_btn)

        layout.addLayout(toolbar)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #ddd; height: 1px; margin: 5px 0;")
        layout.addWidget(line)

        # Холст для рисования
        self.canvas_widget = SimpleDrawingCanvas()
        self.canvas_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 4px;
            }
        """)

        # Область с прокруткой
        scroll = QScrollArea()
        scroll.setWidget(self.canvas_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(500)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(scroll)

        # Панель статуса
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Режим: Рисование. Выберите цвет и толщину.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 8px;
                font-size: 12px;
                background-color: #f8f8f8;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
        """)
        status_layout.addWidget(self.status_label)

        # Инструкция
        instruction = QLabel("💡 Инструкция: Для добавления текста выберите инструмент 'Текст' и кликните на доске")
        instruction.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        instruction.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(instruction)

        layout.addLayout(status_layout)

        # Стилизация кнопок инструментов
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:checked {
                background-color: #2980b9;
                border-color: #1c6ea4;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.text_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:checked {
                background-color: #8e44ad;
                border-color: #7d3c98;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)

        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
        """)

    def set_draw_mode(self):
        """Установить режим рисования"""
        self.canvas_widget.set_text_mode(False)
        self.status_label.setText("Режим: Рисование. Выберите цвет и толщину.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                padding: 8px;
                font-size: 12px;
                background-color: #ebf5fb;
                border-radius: 4px;
                border: 1px solid #d6eaf8;
            }
        """)

    def set_text_mode(self):
        """Установить режим текста"""
        self.canvas_widget.set_text_mode(True)
        self.status_label.setText("Режим: Текст. Кликните на доске, чтобы разместить текст.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #9b59b6;
                padding: 8px;
                font-size: 12px;
                background-color: #f4ecf7;
                border-radius: 4px;
                border: 1px solid #e8daef;
            }
        """)

    def clear_board(self):
        """Очистить доску"""
        reply = QMessageBox.question(self, "Очистка доски",
                                     "Вы уверены, что хотите очистить доску?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.canvas_widget.clear()
            self.status_label.setText("Доска очищена ✓")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    padding: 8px;
                    font-size: 12px;
                    background-color: #e8f8f0;
                    border-radius: 4px;
                    border: 1px solid #d5f4e6;
                }
            """)

    def set_color(self, color):
        """Установить цвет пера"""
        try:
            self.canvas_widget.set_color(color)

            color_names = {
                QColor(255, 0, 0): "Красный",
                QColor(0, 255, 0): "Зеленый",
                QColor(0, 0, 255): "Синий",
                QColor(0, 0, 0): "Черный",
                QColor(128, 0, 128): "Фиолетовый",
                QColor(255, 165, 0): "Оранжевый"
            }

            name = "Синий"
            for qcolor, color_name in color_names.items():
                if qcolor.rgb() == color.rgb():
                    name = color_name
                    break

            self.status_label.setText(f"Цвет: {name} (режим рисования)")
        except Exception as e:
            print(f"Ошибка при установке цвета: {e}")

    def set_width(self, width):
        """Установить толщину"""
        try:
            self.canvas_widget.set_width(width)
            self.status_label.setText(f"Толщина: {width}px (режим рисования)")
        except Exception as e:
            print(f"Ошибка при установке толщины: {e}")

    def set_text_mode(self, enabled):
        """Включить/выключить режим текста"""
        self.text_mode = enabled
        self.text_input_active = False

    def add_text(self, text, position=None):
        """Добавить текст на холст"""
        if position is None:
            position = self.text_position

        painter = QPainter(self.canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Устанавливаем цвет и шрифт для текста
        painter.setPen(QPen(self.text_color))
        painter.setFont(self.text_font)

        # Рисуем текст
        painter.drawText(position, text)
        painter.end()

        self.update()

    def set_text_color(self, color):
        """Установить цвет текста"""
        self.text_color = QColor(color)

    def set_text_font_size(self, size):
        """Установить размер шрифта текста"""
        self.text_font.setPointSize(size)

    def get_text_width(self, text):
        """Получить ширину текста в пикселях"""
        metrics = QFontMetrics(self.text_font)
        return metrics.horizontalAdvance(text)

    def show_text_input_dialog(self):
        """Показать диалог ввода текста"""
        dialog = TextInputDialog(self)
        if dialog.exec():
            text = dialog.get_text()
            if text:
                self.add_text(text, self.text_position)
        self.text_input_active = False


class TextInputDialog(QDialog):
    """Диалог для ввода текста"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Введите текст")
        self.setModal(True)
        self.resize(400, 200)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Поле ввода текста
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Введите текст здесь...")
        self.text_edit.setMaximumHeight(100)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #3498db;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
        """)
        layout.addWidget(QLabel("Текст:"))
        layout.addWidget(self.text_edit)

        # Настройки текста
        settings_layout = QHBoxLayout()

        # Выбор размера шрифта
        settings_layout.addWidget(QLabel("Размер:"))
        self.font_size = QComboBox()
        self.font_size.addItems(["12", "14", "16", "18", "20", "24", "28", "32"])
        self.font_size.setCurrentText("16")
        settings_layout.addWidget(self.font_size)

        # Выбор цвета текста
        settings_layout.addWidget(QLabel("Цвет:"))
        self.color_combo = QComboBox()
        colors = [
            ("Черный", "#000000"),
            ("Красный", "#FF0000"),
            ("Синий", "#0000FF"),
            ("Зеленый", "#00FF00"),
            ("Фиолетовый", "#800080")
        ]
        for name, hex_color in colors:
            self.color_combo.addItem(name, hex_color)
        settings_layout.addWidget(self.color_combo)

        settings_layout.addStretch()
        layout.addLayout(settings_layout)

        # Кнопки
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Добавить")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Отмена")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        # Стилизация кнопок
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

    def get_text(self):
        """Получить введенный текст"""
        return self.text_edit.toPlainText().strip()

    def get_font_size(self):
        """Получить выбранный размер шрифта"""
        return int(self.font_size.currentText())

    def get_color(self):
        """Получить выбранный цвет"""
        return self.color_combo.currentData()


class WhiteboardTab(QWidget):
    """Вкладка с интерактивной доской"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Панель инструментов
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        # Группа инструментов
        tools_group = QButtonGroup(self)

        # Кнопка инструмента "Рисование"
        self.draw_btn = QPushButton("✏️ Рисовать")
        self.draw_btn.setCheckable(True)
        self.draw_btn.setChecked(True)
        self.draw_btn.setFixedSize(120, 40)
        self.draw_btn.clicked.connect(self.set_draw_mode)
        tools_group.addButton(self.draw_btn)

        # Кнопка инструмента "Текст"
        self.text_btn = QPushButton("🔤 Текст")
        self.text_btn.setCheckable(True)
        self.text_btn.setFixedSize(100, 40)
        self.text_btn.clicked.connect(self.set_text_mode)
        tools_group.addButton(self.text_btn)

        toolbar.addWidget(self.draw_btn)
        toolbar.addWidget(self.text_btn)

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setStyleSheet("background-color: #ddd; width: 1px; margin: 0 10px;")
        toolbar.addWidget(separator)

        # Кнопки цвета для рисования
        colors_data = [
            ("🔴", "#FF0000", "Красный"),
            ("🟢", "#00FF00", "Зеленый"),
            ("🔵", "#0000FF", "Синий"),
            ("⚫", "#000000", "Черный"),
            ("🟣", "#800080", "Фиолетовый"),
            ("🟠", "#FFA500", "Оранжевый")
        ]

        # Создаем кнопки цветов
        for emoji, hex_color, tooltip in colors_data:
            btn = QPushButton(emoji)
            btn.setFixedSize(40, 40)
            btn.setToolTip(tooltip)

            def make_color_handler(color_hex):
                def handler():
                    color = QColor(color_hex)
                    self.set_color(color)

                return handler

            btn.clicked.connect(make_color_handler(hex_color))

            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {hex_color};
                    color: white;
                    border-radius: 20px;
                    font-size: 16px;
                    border: 2px solid transparent;
                }}
                QPushButton:hover {{
                    border: 2px solid #3498db;
                }}
            """)
            toolbar.addWidget(btn)

        # Кнопки толщины
        widths_data = [("1px", 1), ("3px", 3), ("5px", 5), ("8px", 8), ("12px", 12)]

        for text, width in widths_data:
            btn = QPushButton(text)
            btn.setFixedSize(60, 40)

            def make_width_handler(w):
                def handler():
                    self.set_width(w)

                return handler

            btn.clicked.connect(make_width_handler(width))

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #f0f0f0;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    color: #333;
                }
                QPushButton:hover {
                    background-color: #e0e0e0;
                }
            """)
            toolbar.addWidget(btn)

        toolbar.addStretch()

        # Кнопка очистки
        self.clear_btn = QPushButton("🧹 Очистить")
        self.clear_btn.clicked.connect(self.clear_board)
        self.clear_btn.setFixedSize(120, 40)
        toolbar.addWidget(self.clear_btn)

        layout.addLayout(toolbar)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #ddd; height: 1px; margin: 5px 0;")
        layout.addWidget(line)

        # Холст для рисования
        self.canvas_widget = SimpleDrawingCanvas()
        self.canvas_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 4px;
            }
        """)

        # Область с прокруткой
        scroll = QScrollArea()
        scroll.setWidget(self.canvas_widget)
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(500)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f5f5;
            }
        """)
        layout.addWidget(scroll)

        # Панель статуса
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Режим: Рисование. Выберите цвет и толщину.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #666;
                padding: 8px;
                font-size: 12px;
                background-color: #f8f8f8;
                border-radius: 4px;
                border: 1px solid #e0e0e0;
            }
        """)
        status_layout.addWidget(self.status_label)

        # Инструкция
        instruction = QLabel("💡 Инструкция: Для добавления текста выберите инструмент 'Текст' и кликните на доске")
        instruction.setStyleSheet("color: #7f8c8d; font-size: 11px; padding: 5px;")
        instruction.setAlignment(Qt.AlignmentFlag.AlignRight)
        status_layout.addWidget(instruction)

        layout.addLayout(status_layout)

        # Стилизация кнопок инструментов
        self.draw_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:checked {
                background-color: #2980b9;
                border-color: #1c6ea4;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.text_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:checked {
                background-color: #8e44ad;
                border-color: #7d3c98;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)

        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                border: 2px solid transparent;
            }
            QPushButton:hover {
                background-color: #c0392b;
                border-color: #a93226;
            }
        """)

    def set_draw_mode(self):
        """Установить режим рисования"""
        self.canvas_widget.set_text_mode(False)
        self.status_label.setText("Режим: Рисование. Выберите цвет и толщину.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #3498db;
                padding: 8px;
                font-size: 12px;
                background-color: #ebf5fb;
                border-radius: 4px;
                border: 1px solid #d6eaf8;
            }
        """)

    def set_text_mode(self):
        """Установить режим текста"""
        self.canvas_widget.set_text_mode(True)
        self.status_label.setText("Режим: Текст. Кликните на доске, чтобы разместить текст.")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #9b59b6;
                padding: 8px;
                font-size: 12px;
                background-color: #f4ecf7;
                border-radius: 4px;
                border: 1px solid #e8daef;
            }
        """)

    def clear_board(self):
        """Очистить доску"""
        reply = QMessageBox.question(self, "Очистка доски",
                                     "Вы уверены, что хотите очистить доску?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.canvas_widget.clear()
            self.status_label.setText("Доска очищена ✓")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    padding: 8px;
                    font-size: 12px;
                    background-color: #e8f8f0;
                    border-radius: 4px;
                    border: 1px solid #d5f4e6;
                }
            """)

    def set_color(self, color):
        """Установить цвет пера"""
        try:
            self.canvas_widget.set_color(color)

            color_names = {
                QColor(255, 0, 0): "Красный",
                QColor(0, 255, 0): "Зеленый",
                QColor(0, 0, 255): "Синий",
                QColor(0, 0, 0): "Черный",
                QColor(128, 0, 128): "Фиолетовый",
                QColor(255, 165, 0): "Оранжевый"
            }

            name = "Синий"
            for qcolor, color_name in color_names.items():
                if qcolor.rgb() == color.rgb():
                    name = color_name
                    break

            self.status_label.setText(f"Цвет: {name} (режим рисования)")
        except Exception as e:
            print(f"Ошибка при установке цвета: {e}")

    def set_width(self, width):
        """Установить толщину"""
        try:
            self.canvas_widget.set_width(width)
            self.status_label.setText(f"Толщина: {width}px (режим рисования)")
        except Exception as e:
            print(f"Ошибка при установке толщины: {e}")

class UserCard(QFrame):
    """Виджет карточки пользователя"""

    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #3498db;
            }
        """)

        layout = QVBoxLayout(self)

        # Имя
        name_label = QLabel(f"<h3>{self.user_data['name']}</h3>")
        layout.addWidget(name_label)

        # Email
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
        status = self.user_data.get('status', '')
        if status:
            status_label = QLabel(f"💬 {status}")
            status_label.setStyleSheet("color: #2ecc71;")
            layout.addWidget(status_label)

        # Ищет проект
        if self.user_data.get('looking_for_project', 0):
            project_label = QLabel("🔍 Ищет проект для коллаборации")
            project_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(project_label)


class EventCard(QFrame):
    """Виджет карточки мероприятия"""

    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.init_ui()

    def init_ui(self):
        self.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #2ecc71;
            }
        """)

        layout = QVBoxLayout(self)

        # Название
        title_label = QLabel(f"<h3>{self.event_data['title']}</h3>")
        layout.addWidget(title_label)

        # Описание
        if self.event_data['description']:
            desc = self.event_data['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        # Дата
        if self.event_data['start_date']:
            date_label = QLabel(f"📅 {self.event_data['start_date']}")
            layout.addWidget(date_label)

        # Место
        if self.event_data['location']:
            loc_label = QLabel(f"📍 {self.event_data['location']}")
            layout.addWidget(loc_label)

        # Теги
        tags = json.loads(self.event_data['tags'])
        if tags:
            tags_label = QLabel(f"🏷️ {', '.join(tags[:5])}")
            tags_label.setStyleSheet("color: #3498db;")
            layout.addWidget(tags_label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.all_users = []
        self.all_events = []
        self.all_tags = set()
        self.init_ui()
        self.load_data()

    def init_ui(self):
        self.setWindowTitle("CollabMatch - Поиск команды")
        self.setGeometry(100, 100, 1300, 850)

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
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        # Подзаголовок
        subtitle = QLabel("Найди команду для проекта по интересам и навыкам")
        subtitle.setStyleSheet("color: #7f8c8d; padding-bottom: 15px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(subtitle)

        # Панель поиска
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск пользователей, мероприятий, навыков, интересов...")
        self.search_input.returnPressed.connect(self.perform_search)
        search_button = QPushButton("Найти")
        search_button.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Вкладки
        self.tab_widget = QTabWidget()

        # Вкладка пользователей
        self.users_tab = QWidget()
        self.setup_users_tab()
        self.tab_widget.addTab(self.users_tab, "👥 Пользователи")

        # Вкладка мероприятий
        self.events_tab = QWidget()
        self.setup_events_tab()
        self.tab_widget.addTab(self.events_tab, "📅 Мероприятия")

        # Вкладка совпадений
        self.matches_tab = QWidget()
        self.setup_matches_tab()
        self.tab_widget.addTab(self.matches_tab, "💫 Совпадения")

        # Вкладка поиска
        self.search_tab = QWidget()
        self.setup_search_tab()
        self.tab_widget.addTab(self.search_tab, "🔍 Результаты поиска")

        # Вкладка интерактивной доски
        self.whiteboard_tab = WhiteboardTab()
        self.tab_widget.addTab(self.whiteboard_tab, "🎨 Интерактивная доска")

        main_layout.addWidget(self.tab_widget)

    def setup_users_tab(self):
        """Настроить вкладку пользователей"""
        layout = QVBoxLayout(self.users_tab)

        # Панель фильтров
        filter_layout = QHBoxLayout()

        # Поиск по имени/навыкам
        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText("Поиск по имени, навыкам...")
        self.user_search_input.textChanged.connect(self.filter_users)
        filter_layout.addWidget(self.user_search_input)

        # Фильтр по тегам (навыкам)
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("Все навыки", "")
        self.tag_filter_combo.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Фильтр по навыку:"))
        filter_layout.addWidget(self.tag_filter_combo)

        # Фильтр по поиску проекта
        self.project_filter_combo = QComboBox()
        self.project_filter_combo.addItem("Все", "all")
        self.project_filter_combo.addItem("Ищут проект", "looking")
        self.project_filter_combo.addItem("Не ищут проект", "not_looking")
        self.project_filter_combo.currentIndexChanged.connect(self.filter_users)
        filter_layout.addWidget(QLabel("Поиск проекта:"))
        filter_layout.addWidget(self.project_filter_combo)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Кнопка добавления пользователя
        add_user_btn = QPushButton("➕ Добавить пользователя")
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
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.users_scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Контейнер для карточек
        self.users_container = QWidget()
        self.users_layout = QVBoxLayout(self.users_container)
        self.users_scroll_layout.addWidget(self.users_container)

    def setup_events_tab(self):
        """Настроить вкладку мероприятий"""
        layout = QVBoxLayout(self.events_tab)

        # Панель фильтров для мероприятий
        event_filter_layout = QHBoxLayout()

        self.event_search_input = QLineEdit()
        self.event_search_input.setPlaceholderText("Поиск по названию, описанию...")
        self.event_search_input.textChanged.connect(self.filter_events)
        event_filter_layout.addWidget(self.event_search_input)

        self.event_tag_filter_combo = QComboBox()
        self.event_tag_filter_combo.addItem("Все теги", "")
        self.event_tag_filter_combo.currentIndexChanged.connect(self.filter_events)
        event_filter_layout.addWidget(QLabel("Фильтр по тегу:"))
        event_filter_layout.addWidget(self.event_tag_filter_combo)

        event_filter_layout.addStretch()
        layout.addLayout(event_filter_layout)

        # Кнопка добавления мероприятия
        add_event_btn = QPushButton("➕ Добавить мероприятие")
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

        # Прокручиваемая область для мероприятий
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.events_scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Контейнер для карточек
        self.events_container = QWidget()
        self.events_layout = QVBoxLayout(self.events_container)
        self.events_scroll_layout.addWidget(self.events_container)

    def setup_matches_tab(self):
        """Настроить вкладку совпадений"""
        layout = QVBoxLayout(self.matches_tab)

        # Выбор пользователя
        select_layout = QHBoxLayout()
        select_layout.addWidget(QLabel("Выберите пользователя:"))

        self.user_combo = QComboBox()
        select_layout.addWidget(self.user_combo)

        find_button = QPushButton("Найти совпадения")
        find_button.clicked.connect(self.find_matches)
        find_button.setStyleSheet("""
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
        select_layout.addWidget(find_button)

        select_layout.addStretch()
        layout.addLayout(select_layout)

        # Прокручиваемая область для результатов
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.matches_scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Контейнер для результатов
        self.matches_container = QWidget()
        self.matches_layout = QVBoxLayout(self.matches_container)
        self.matches_scroll_layout.addWidget(self.matches_container)

    def setup_search_tab(self):
        """Настроить вкладку поиска"""
        layout = QVBoxLayout(self.search_tab)

        # Заголовок
        self.search_title = QLabel("Результаты поиска")
        self.search_title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(self.search_title)

        # Прокручиваемая область
        scroll = QScrollArea()
        scroll_widget = QWidget()
        self.search_scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Контейнер для результатов
        self.search_container = QWidget()
        self.search_results_layout = QVBoxLayout(self.search_container)
        self.search_scroll_layout.addWidget(self.search_container)

    def load_data(self):
        """Загрузить все данные"""
        try:
            # Загрузка пользователей
            self.all_users = self.db.get_all_users()

            # Загрузка мероприятий
            self.all_events = self.db.get_all_events()

            # Собираем все уникальные навыки
            self.all_tags.clear()
            for user in self.all_users:
                skills = json.loads(user['skills'])
                self.all_tags.update(skills)

            # Собираем все уникальные теги мероприятий
            for event in self.all_events:
                tags = json.loads(event['tags'])
                self.all_tags.update(tags)

            # Обновляем комбобоксы фильтров
            self.update_filter_comboboxes()

            # Отображаем данные
            self.display_users(self.all_users)
            self.display_events(self.all_events)

            # Загрузка в комбобокс для поиска совпадений
            self.user_combo.clear()
            self.user_combo.addItem("-- Выберите пользователя --", -1)
            for user in self.all_users:
                self.user_combo.addItem(f"{user['name']} (ID: {user['id']})", user['id'])

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {str(e)}")

    def update_filter_comboboxes(self):
        """Обновить комбобоксы фильтров"""
        self.tag_filter_combo.clear()
        self.tag_filter_combo.addItem("Все навыки", "")

        self.event_tag_filter_combo.clear()
        self.event_tag_filter_combo.addItem("Все теги", "")

        # Сортируем теги по алфавиту
        sorted_tags = sorted(self.all_tags)
        for tag in sorted_tags:
            if tag.strip():
                self.tag_filter_combo.addItem(tag, tag)
                self.event_tag_filter_combo.addItem(tag, tag)

    def display_users(self, users):
        """Отобразить пользователей"""
        for i in reversed(range(self.users_layout.count())):
            widget = self.users_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not users:
            label = QLabel("Пользователей не найдено")
            label.setStyleSheet("color: #7f8c8d; padding: 20px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.users_layout.addWidget(label)
            return

        # Счетчик
        count_label = QLabel(f"Найдено пользователей: {len(users)}")
        count_label.setStyleSheet("font-size: 14px; color: #3498db; padding: 5px;")
        self.users_layout.addWidget(count_label)

        for user in users:
            if 'status' not in user:
                user['status'] = ''
            card = UserCard(user)
            self.users_layout.addWidget(card)

        self.users_layout.addStretch()

    def display_events(self, events):
        """Отобразить мероприятия"""
        for i in reversed(range(self.events_layout.count())):
            widget = self.events_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not events:
            label = QLabel("Мероприятий не найдено")
            label.setStyleSheet("color: #7f8c8d; padding: 20px;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_layout.addWidget(label)
            return

        # Счетчик
        count_label = QLabel(f"Найдено мероприятий: {len(events)}")
        count_label.setStyleSheet("font-size: 14px; color: #2ecc71; padding: 5px;")
        self.events_layout.addWidget(count_label)

        for event in events:
            card = EventCard(event)
            self.events_layout.addWidget(card)

        self.events_layout.addStretch()

    def filter_users(self):
        """Фильтрация пользователей"""
        search_text = self.user_search_input.text().lower().strip()
        selected_tag = self.tag_filter_combo.currentData()
        project_filter = self.project_filter_combo.currentData()

        filtered_users = []

        for user in self.all_users:
            matches_search = True
            if search_text:
                name_match = search_text in user['name'].lower()
                email_match = search_text in (user.get('email', '') or '').lower()

                skills = json.loads(user['skills'])
                skills_match = any(search_text in skill.lower() for skill in skills)

                interests = json.loads(user['interests'])
                interests_match = any(search_text in interest.lower() for interest in interests)

                status_match = search_text in (user.get('status', '') or '').lower()

                matches_search = name_match or email_match or skills_match or interests_match or status_match

            matches_tag = True
            if selected_tag:
                skills = json.loads(user['skills'])
                matches_tag = selected_tag in skills

            matches_project = True
            if project_filter == "looking":
                matches_project = user.get('looking_for_project', 0) == 1
            elif project_filter == "not_looking":
                matches_project = user.get('looking_for_project', 0) == 0

            if matches_search and matches_tag and matches_project:
                filtered_users.append(user)

        self.display_users(filtered_users)

    def filter_events(self):
        """Фильтрация мероприятий"""
        search_text = self.event_search_input.text().lower().strip()
        selected_tag = self.event_tag_filter_combo.currentData()

        filtered_events = []

        for event in self.all_events:
            matches_search = True
            if search_text:
                title_match = search_text in event['title'].lower()
                desc_match = search_text in (event.get('description', '') or '').lower()
                location_match = search_text in (event.get('location', '') or '').lower()

                matches_search = title_match or desc_match or location_match

            matches_tag = True
            if selected_tag:
                tags = json.loads(event['tags'])
                matches_tag = selected_tag in tags

            if matches_search and matches_tag:
                filtered_events.append(event)

        self.display_events(filtered_events)

    def find_matches(self):
        """Найти совпадения для выбранного пользователя"""
        user_id = self.user_combo.currentData()
        if user_id == -1:
            QMessageBox.warning(self, "Внимание", "Выберите пользователя")
            return

        try:
            matches = self.db.find_matches(user_id)

            for i in reversed(range(self.matches_layout.count())):
                widget = self.matches_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            if not matches:
                label = QLabel("Совпадений не найдено")
                label.setStyleSheet("color: #7f8c8d; padding: 20px;")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.matches_layout.addWidget(label)
                return

            user = self.db.get_user(user_id)
            user_name = user['name'] if user else "Неизвестный пользователь"
            title = QLabel(f"🎯 Найдено {len(matches)} совпадений для {user_name}:")
            title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
            self.matches_layout.addWidget(title)

            for match in matches[:15]:
                match_widget = self.create_match_widget(match)
                self.matches_layout.addWidget(match_widget)

            self.matches_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось найти совпадения: {str(e)}")

    def create_match_widget(self, match_data):
        """Создать виджет совпадения"""
        user = match_data['user']

        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
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

        header = QHBoxLayout()
        name_label = QLabel(f"<b>{user['name']}</b>")
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

        if user.get('email'):
            email_label = QLabel(f"📧 {user['email']}")
            layout.addWidget(email_label)

        common_skills = match_data.get('common_skills', [])
        if common_skills:
            skills_text = f"<b>Общие навыки:</b> {', '.join(common_skills)}"
            skills_label = QLabel(skills_text)
            skills_label.setWordWrap(True)
            layout.addWidget(skills_label)

        common_interests = match_data.get('common_interests', [])
        if common_interests:
            interests_text = f"<b>Общие интересы:</b> {', '.join(common_interests)}"
            interests_label = QLabel(interests_text)
            interests_label.setWordWrap(True)
            layout.addWidget(interests_label)

        status = user.get('status', '')
        if status:
            status_label = QLabel(f"💬 {status}")
            layout.addWidget(status_label)

        if user.get('looking_for_project', 0):
            project_label = QLabel("🔍 Ищет проект для коллаборации")
            project_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            layout.addWidget(project_label)

        return widget

    def perform_search(self):
        """Выполнить глобальный поиск"""
        query = self.search_input.text().strip()

        if not query:
            QMessageBox.warning(self, "Поиск", "Введите поисковый запрос")
            return

        try:
            self.tab_widget.setCurrentIndex(3)

            for i in reversed(range(self.search_results_layout.count())):
                widget = self.search_results_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            results = self.db.search(query)

            self.search_title.setText(f"Результаты поиска: '{query}'")

            total_results = len(results.get('users', [])) + len(results.get('events', [])) + len(
                results.get('projects', []))

            if total_results == 0:
                label = QLabel(f"По запросу '{query}' ничего не найдено")
                label.setStyleSheet("color: #7f8c8d; padding: 20px;")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.search_results_layout.addWidget(label)
                return

            results_label = QLabel(f"Найдено результатов: {total_results}")
            results_label.setStyleSheet("font-size: 14px; color: #3498db; padding: 5px;")
            self.search_results_layout.addWidget(results_label)

            if results.get('users'):
                users_label = QLabel(f"👥 Пользователи ({len(results['users'])})")
                users_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px; color: #3498db;")
                self.search_results_layout.addWidget(users_label)

                for user in results['users']:
                    if 'status' not in user:
                        user['status'] = ''
                    card = UserCard(user)
                    self.search_results_layout.addWidget(card)

            if results.get('events'):
                events_label = QLabel(f"📅 Мероприятия ({len(results['events'])})")
                events_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px; color: #2ecc71;")
                self.search_results_layout.addWidget(events_label)

                for event in results['events']:
                    card = EventCard(event)
                    self.search_results_layout.addWidget(card)

            if results.get('projects'):
                projects_label = QLabel(f"🚀 Проекты ({len(results['projects'])})")
                projects_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px; color: #9b59b6;")
                self.search_results_layout.addWidget(projects_label)

                for project in results['projects']:
                    project_widget = self.create_project_widget(project)
                    self.search_results_layout.addWidget(project_widget)

            self.search_results_layout.addStretch()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка поиска: {str(e)}")

    def create_project_widget(self, project_data):
        """Создать виджет проекта"""
        widget = QFrame()
        widget.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                padding: 10px;
                margin: 5px;
            }
            QFrame:hover {
                background-color: #f8f9fa;
                border-color: #9b59b6;
            }
        """)

        layout = QVBoxLayout(widget)

        title_label = QLabel(f"<h3>{project_data['title']}</h3>")
        layout.addWidget(title_label)

        if project_data.get('description'):
            desc = project_data['description']
            if len(desc) > 150:
                desc = desc[:150] + "..."
            desc_label = QLabel(desc)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        status = project_data.get('status', '')
        if status:
            status_text = f"📊 Статус: {status}"
            if status == 'active':
                status_text += " ✅"
            elif status == 'planning':
                status_text += " 📝"
            elif status == 'in_progress':
                status_text += " 🔄"

            status_label = QLabel(status_text)
            status_label.setStyleSheet("color: #9b59b6; font-weight: bold;")
            layout.addWidget(status_label)

        return widget

    def show_add_user_dialog(self):
        """Показать диалог добавления пользователя"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пользователя")
        dialog.setModal(True)
        dialog.resize(450, 400)

        layout = QVBoxLayout(dialog)

        form = QFormLayout()

        name_input = QLineEdit()
        email_input = QLineEdit()
        skills_input = QLineEdit()
        skills_input.setPlaceholderText("Python, SQL, Дизайн, Маркетинг...")
        interests_input = QLineEdit()
        interests_input.setPlaceholderText("ИИ, Биология, Стартапы, Образование...")
        status_input = QLineEdit()
        status_input.setPlaceholderText("Хочу сотрудничать в проекте по...")
        looking_checkbox = QCheckBox("Ищет проект для сотрудничества")

        form.addRow("Имя *:", name_input)
        form.addRow("Email *:", email_input)
        form.addRow("Навыки:", skills_input)
        form.addRow("Интересы:", interests_input)
        form.addRow("Статус:", status_input)
        form.addRow("", looking_checkbox)

        layout.addLayout(form)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def save_user():
            name = name_input.text().strip()
            email = email_input.text().strip()

            if not name or not email:
                QMessageBox.warning(dialog, "Ошибка", "Заполните имя и email")
                return

            skills = [s.strip() for s in skills_input.text().split(',') if s.strip()]
            interests = [i.strip() for i in interests_input.text().split(',') if i.strip()]

            try:
                user_id = self.db.add_user(
                    name=name,
                    email=email,
                    skills=skills,
                    interests=interests,
                    collaboration_status=status_input.text().strip(),
                    looking_for_project=looking_checkbox.isChecked()
                )

                QMessageBox.information(dialog, "Успех", f"Пользователь добавлен с ID: {user_id}")
                dialog.accept()
                self.load_data()

            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить пользователя: {str(e)}")

        save_button.clicked.connect(save_user)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()

    def show_add_event_dialog(self):
        """Показать диалог добавления мероприятия"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить мероприятие")
        dialog.setModal(True)
        dialog.resize(500, 450)

        layout = QVBoxLayout(dialog)

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
        tags_input.setPlaceholderText("нейросети, биология, лекция, хакатон...")

        form.addRow("Название *:", title_input)
        form.addRow("Описание:", description_input)
        form.addRow("Дата начала *:", start_date_input)
        form.addRow("Дата окончания:", end_date_input)
        form.addRow("Место:", location_input)
        form.addRow("Теги:", tags_input)

        layout.addLayout(form)

        button_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")

        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def save_event():
            title = title_input.text().strip()
            start_date = start_date_input.text().strip()

            if not title:
                QMessageBox.warning(dialog, "Ошибка", "Введите название мероприятия")
                return

            if not start_date:
                QMessageBox.warning(dialog, "Ошибка", "Введите дату начала")
                return

            tags = [t.strip() for t in tags_input.text().split(',') if t.strip()]

            try:
                event_id = self.db.add_event(
                    title=title,
                    description=description_input.toPlainText().strip(),
                    start_date=start_date,
                    end_date=end_date_input.text().strip(),
                    location=location_input.text().strip(),
                    tags=tags,
                    max_participants=0
                )

                QMessageBox.information(dialog, "Успех", f"Мероприятие добавлено с ID: {event_id}")
                dialog.accept()
                self.load_data()

            except Exception as e:
                QMessageBox.critical(dialog, "Ошибка", f"Не удалось добавить мероприятие: {str(e)}")

        save_button.clicked.connect(save_event)
        cancel_button.clicked.connect(dialog.reject)

        dialog.exec()


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

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
            padding: 8px 16px;
            border: 1px solid #d1d8e0;
        }
        QTabBar::tab:selected {
            background-color: white;
            border-bottom: 2px solid #3498db;
        }
        QPushButton {
            padding: 8px 16px;
            border-radius: 4px;
            border: none;
        }
        QLineEdit, QTextEdit {
            padding: 8px;
            border: 1px solid #d1d8e0;
            border-radius: 4px;
        }
        QComboBox {
            padding: 6px;
            border: 1px solid #d1d8e0;
            border-radius: 4px;
        }
        QScrollArea {
            border: none;
            background-color: #f8f9fa;
        }
    """)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()