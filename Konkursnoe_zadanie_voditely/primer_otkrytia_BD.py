import sys
import sqlite3
import uuid
import re
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFileDialog, QFormLayout, QCompleter, QTableWidget, QTableWidgetItem
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
        notes TEXT
    );
    """)
    conn.commit()
    conn.close()


class CreateDriverWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Создание водителя")

        self.guid_field = QLineEdit(str(uuid.uuid4()))
        self.guid_field.setReadOnly(True)

        self.last_name_field = QLineEdit()
        self.first_name_field = QLineEdit()
        self.middle_name_field = QLineEdit()
        self.passport_field = QLineEdit()
        self.passport_field.setPlaceholderText("Серия и номер")

        self.registration_city_field = QLineEdit()
        self.registration_address_field = QLineEdit()
        self.living_city_field = QLineEdit()
        self.living_address_field = QLineEdit()

        self.workplace_field = QLineEdit()
        self.position_field = QLineEdit()

        self.phone_field = QLineEdit()
        self.phone_field.setPlaceholderText("+7XXXXXXXXXX")
        self.email_field = QLineEdit()
        self.notes_field = QLineEdit()

        self.choose_photo_button = QPushButton("Выбрать фото")
        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.save_driver_to_db)

        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор (GUID):", self.guid_field)
        form_layout.addRow("Фамилия*:", self.last_name_field)
        form_layout.addRow("Имя*:", self.first_name_field)
        form_layout.addRow("Отчество*:", self.middle_name_field)
        form_layout.addRow("Паспорт*:", self.passport_field)
        form_layout.addRow("Город регистрации:", self.registration_city_field)
        form_layout.addRow("Адрес регистрации:", self.registration_address_field)
        form_layout.addRow("Город проживания:", self.living_city_field)
        form_layout.addRow("Адрес проживания:", self.living_address_field)
        form_layout.addRow("Место работы:", self.workplace_field)
        form_layout.addRow("Должность:", self.position_field)
        form_layout.addRow("Телефон*:", self.phone_field)
        form_layout.addRow("Email*:", self.email_field)
        form_layout.addRow("Замечания:", self.notes_field)
        form_layout.addRow("", self.submit_button)

        self.setLayout(form_layout)

    def save_driver_to_db(self):
        conn = sqlite3.connect("drivers.db")
        cursor = conn.cursor()

        if not self.last_name_field.text() or not self.first_name_field.text():
            QMessageBox.warning(self, "Ошибка", "Поля 'Фамилия' и 'Имя' обязательны.")
            return

        cursor.execute("""
        INSERT INTO drivers (
            guid, last_name, first_name, middle_name, passport, registration_city, 
            registration_address, living_city, living_address, workplace, position, phone, email, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            self.guid_field.text(),
            self.last_name_field.text(),
            self.first_name_field.text(),
            self.middle_name_field.text(),
            self.passport_field.text(),
            self.registration_city_field.text(),
            self.registration_address_field.text(),
            self.living_city_field.text(),
            self.living_address_field.text(),
            self.workplace_field.text(),
            self.position_field.text(),
            self.phone_field.text(),
            self.email_field.text(),
            self.notes_field.text()
        ))

        conn.commit()
        conn.close()

        QMessageBox.information(self, "Успех", "Водитель успешно добавлен!")
        self.close()


class ViewDriversWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Список водителей")

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["GUID", "Фамилия", "Имя", "Телефон", "Email"])
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
        cursor.execute("SELECT guid, last_name, first_name, phone, email FROM drivers")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(0)

        for row_index, row_data in enumerate(rows):
            self.table.insertRow(row_index)
            for col_index, cell_data in enumerate(row_data):
                self.table.setItem(row_index, col_index, QTableWidgetItem(str(cell_data)))


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Главное меню")
        self.create_driver_button = QPushButton("Создать водителя")
        self.view_drivers_button = QPushButton("Посмотреть водителей")

        layout = QVBoxLayout()
        layout.addWidget(self.create_driver_button)
        layout.addWidget(self.view_drivers_button)
        self.setLayout(layout)

        self.create_driver_button.clicked.connect(self.open_create_driver_window)
        self.view_drivers_button.clicked.connect(self.open_view_drivers_window)

    def open_create_driver_window(self):
        self.create_driver_window = CreateDriverWindow()
        self.create_driver_window.show()

    def open_view_drivers_window(self):
        self.view_drivers_window = ViewDriversWindow()
        self.view_drivers_window.show()


if __name__ == "__main__":
    setup_database()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
