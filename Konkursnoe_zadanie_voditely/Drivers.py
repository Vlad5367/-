import os
import sys
import sqlite3
from time import time, sleep
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QFormLayout, QCompleter, QTabWidget, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

def setup_database():
    conn = sqlite3.connect("drivers.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS drivers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guid TEXT NOT NULL,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        middle_name TEXT,
        passport TEXT NOT NULL,
        registration_city TEXT,
        registration_address TEXT,
        living_city TEXT,
        living_address TEXT,
        workplace TEXT,
        position TEXT,
        phone TEXT,
        email TEXT,
        photo_path TEXT,
        notes TEXT
    );
    """)
    conn.commit()
    conn.close()

class LoginTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
        self.users = {"inspector": "inspector"}
        self.error_count = 0
        self.last_failed_attempt_time = None

    def init_ui(self):
        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Войти")
        self.info_label = QLabel("")

        self.login_button.clicked.connect(self.handle_login)

        layout = QVBoxLayout()
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def handle_login(self):
        if self.last_failed_attempt_time and time() - self.last_failed_attempt_time < 60:
            remaining_time = 60 - int(time() - self.last_failed_attempt_time)
            self.info_label.setText(f"Блокировка ввода. Попробуйте через {remaining_time} секунд.")
            return

        login = self.login_input.text()
        password = self.password_input.text()

        if login in self.users and self.users[login] == password:
            self.info_label.setText("Успешный вход!")
            self.main_app.unlock_menu()
            self.error_count = 0
            self.last_failed_attempt_time = None
        else:
            self.error_count += 1
            if self.error_count >= 3:
                self.last_failed_attempt_time = time()
                self.info_label.setText("Блокировка ввода на 1 минуту.")
            else:
                self.info_label.setText(f"Неверный логин или пароль. Осталось попыток: {3 - self.error_count}")


class MenuTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()
    def init_ui(self):
        self.create_driver_button = QPushButton("Создать водителя")
        self.create_driver_button.clicked.connect(lambda: self.main_app.tabs.setCurrentIndex(2))
        self.view_drivers_button = QPushButton("Посмотреть водителей")
        self.view_drivers_button.clicked.connect(self.view_drivers)
        layout = QVBoxLayout()
        layout.addWidget(self.create_driver_button)
        layout.addWidget(self.view_drivers_button)
        self.setLayout(layout)
    def view_drivers(self):
        self.main_app.view_drivers_window = ViewDriversWindow()
        self.main_app.view_drivers_window.show()


class CreateDriverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.photo_path = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание водителя")

        self.guid_field = QLineEdit()
        self.full_name_field = QLineEdit()
        self.full_name_field.setPlaceholderText("Введите фамилию и имя")
        self.middle_name_field = QLineEdit()
        self.passport_field = QLineEdit()
        self.passport_field.setPlaceholderText("Серия и номер")
        self.registration_address_field = QLineEdit()
        self.living_address_field = QLineEdit()
        self.workplace_field = QLineEdit()
        self.position_field = QLineEdit()
        self.phone_field = QLineEdit()
        self.phone_field.setPlaceholderText("+7XXXXXXXXXX")
        self.email_field = QLineEdit()
        self.notes_field = QLineEdit()

        self.photo_label = QLabel("Фото не выбрано")
        self.photo_label.setFixedSize(100, 100)
        self.photo_label.setStyleSheet("border: 1px solid black;")
        self.photo_label.setAlignment(Qt.AlignCenter)

        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)

        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.save_driver_to_db)

        form_layout = QFormLayout()
        form_layout.addRow("GUID:", self.guid_field)
        form_layout.addRow("Фамилия и имя*:", self.full_name_field)
        form_layout.addRow("Отчество:", self.middle_name_field)
        form_layout.addRow("Паспорт*:", self.passport_field)
        form_layout.addRow("Адрес регистрации:", self.registration_address_field)
        form_layout.addRow("Адрес проживания:", self.living_address_field)
        form_layout.addRow("Место работы:", self.workplace_field)
        form_layout.addRow("Должность:", self.position_field)
        form_layout.addRow("Телефон*:", self.phone_field)
        form_layout.addRow("Email:", self.email_field)
        form_layout.addRow("Замечания:", self.notes_field)
        form_layout.addRow("Фото:", self.photo_label)
        form_layout.addRow("", self.choose_photo_button)
        form_layout.addRow("", self.submit_button)

        self.setLayout(form_layout)

    def choose_photo(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Выбрать фото", "", "Изображения (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.photo_path = file_path
            pixmap = QPixmap(file_path).scaled(100, 100, Qt.KeepAspectRatio)
            self.photo_label.setPixmap(pixmap)

    def save_driver_to_db(self):
        conn = sqlite3.connect("drivers.db")
        cursor = conn.cursor()

        if not self.full_name_field.text() or not self.passport_field.text():
            QMessageBox.warning(self, "Ошибка", "Поля 'Фамилия и имя' и 'Паспорт' обязательны.")
            return

        full_name = self.full_name_field.text().strip()
        name_parts = full_name.split(" ", 1)
        if len(name_parts) != 2:
            QMessageBox.warning(self, "Ошибка", "Поле 'Фамилия и имя' должно содержать два слова.")
            return
        last_name, first_name = name_parts

        cursor.execute("""
        INSERT INTO drivers (
            guid, last_name, first_name, middle_name, passport, registration_address, 
            living_address, workplace, position, phone, email, photo_path, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.guid_field.text(),
            last_name,
            first_name,
            self.middle_name_field.text(),
            self.passport_field.text(),
            self.registration_address_field.text(),
            self.living_address_field.text(),
            self.workplace_field.text(),
            self.position_field.text(),
            self.phone_field.text(),
            self.email_field.text(),
            self.photo_path,
            self.notes_field.text()
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Водитель успешно добавлен!")
        self.close()
        email = self.email_field.text()
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            QMessageBox.warning(self, "Ошибка", "Введите корректный email.")
            return


class ViewDriversWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        self.setWindowTitle("Список водителей")
        self.table = QTableWidget()
        self.table.setColumnCount(15)
        self.table.setHorizontalHeaderLabels([
            "ID", "Фамилия", "Имя", "Отчество", "Паспорт", "Город регистрации",
            "Адрес проживания", "Место работы", "Должность", "Телефон", "Email", "Фото", "Описание"
        ])

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.load_drivers)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

        self.load_drivers()

    def load_drivers(self):
        conn = sqlite3.connect("drivers.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, last_name, first_name, middle_name, passport, registration_city, 
                registration_address, living_city, living_address, workplace, 
                position, phone, email, photo_path, notes 
            FROM drivers
        """)
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)

        for row_index, row_data in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                if col_index == 13:
                    photo_label = QLabel()
                    if cell_data and os.path.exists(cell_data):
                        pixmap = QPixmap(cell_data).scaled(50, 66, Qt.KeepAspectRatio)
                        photo_label.setPixmap(pixmap)
                    else:
                        photo_label.setText("Нет фото")
                    self.table.setCellWidget(row_index, col_index, photo_label)
                else:
                    self.table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))


class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.resize(400, 600)

    def init_ui(self):
        self.tabs = QTabWidget()
        self.login_tab = LoginTab(self)
        self.menu_tab = MenuTab(self)
        self.create_driver_tab = CreateDriverWindow()

        self.tabs.addTab(self.login_tab, "Логин")
        self.tabs.addTab(self.menu_tab, "Главное меню")
        self.tabs.addTab(self.create_driver_tab, "Создание водителя")

        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def unlock_menu(self):
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setCurrentIndex(1)

if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())