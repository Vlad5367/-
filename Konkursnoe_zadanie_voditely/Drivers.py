import sys
import os
import uuid
import re
from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QFileDialog,
    QFormLayout, QCompleter, QTabWidget
)
from PyQt5.QtCore import Qt

class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Система управления водителями")
        self.resize(600, 400)

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


class LoginTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

        # Данные пользователей (для примера)
        self.users = {"Inspector": "qaz123-="}
        self.error_count = 0

    def init_ui(self):
        self.setWindowTitle("Логин")

        # Виджеты
        self.login_label = QLabel("Логин:")
        self.login_input = QLineEdit()
        self.password_label = QLabel("Пароль:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Войти")
        self.info_label = QLabel("")

        # Сигналы
        self.login_button.clicked.connect(self.handle_login)

        # Компоновка
        layout = QVBoxLayout()
        layout.addWidget(self.login_label)
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.info_label)
        self.setLayout(layout)

    def handle_login(self):
        login = self.login_input.text()
        password = self.password_input.text()

        if login in self.users and self.users[login] == password:
            self.info_label.setText("Успешный вход!")
            self.main_app.unlock_menu()
        else:
            self.error_count += 1
            self.info_label.setText(f"Неверный логин или пароль. Попыток: {3 - self.error_count}")


class MenuTab(QWidget):
    def __init__(self, main_app):
        super().__init__()
        self.main_app = main_app
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Главное меню")

        self.create_driver_button = QPushButton("Создать водителя")
        self.create_driver_button.clicked.connect(self.open_create_driver_tab)

        self.view_drivers_button = QPushButton("Посмотреть водителей")
        self.view_drivers_button.clicked.connect(self.view_drivers)

        # Компоновка
        layout = QVBoxLayout()
        layout.addWidget(self.create_driver_button)
        layout.addWidget(self.view_drivers_button)
        self.setLayout(layout)

    def open_create_driver_tab(self):
        self.main_app.tabs.setCurrentIndex(2)

    def view_drivers(self):
        QMessageBox.information(self, "Информация", "Просмотр водителей пока не реализован.")


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
        self.passport_field.setPlaceholderText("Серия и номер (XXXX XXXXXX)")

        self.registration_city_field = QLineEdit()
        self.registration_address_field = QLineEdit()

        self.living_city_field = QLineEdit()
        self.living_address_field = QLineEdit()

        self.workplace_field = QLineEdit()
        self.position_field = QLineEdit()

        self.phone_field = QLineEdit()
        self.phone_field.setPlaceholderText("+7XXXXXXXXXX")

        self.email_field = QLineEdit()
        self.photo_path_label = QLabel("Фото не выбрано")
        self.photo_preview = QLabel()
        self.photo_preview.setFixedSize(100, 133)
        self.photo_preview.setStyleSheet("border: 1px solid black;")
        self.photo_preview.setAlignment(Qt.AlignCenter)

        self.notes_field = QLineEdit()

        self.choose_photo_button = QPushButton("Выбрать фото")
        self.choose_photo_button.clicked.connect(self.choose_photo)

        self.submit_button = QPushButton("Сохранить")
        self.submit_button.clicked.connect(self.validate_data)

        cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань"]
        completer = QCompleter(cities)
        self.registration_city_field.setCompleter(completer)
        self.living_city_field.setCompleter(completer)

        form_layout = QFormLayout()
        form_layout.addRow("Идентификатор (GUID):", self.guid_field)
        form_layout.addRow("Фамилия*:", self.last_name_field)
        form_layout.addRow("Имя*:", self.first_name_field)
        form_layout.addRow("Отчество*:", self.middle_name_field)
        form_layout.addRow("Паспорт*:", self.passport_field)
        form_layout.addRow("Город регистрации*:", self.registration_city_field)
        form_layout.addRow("Адрес регистрации*:", self.registration_address_field)
        form_layout.addRow("Город проживания*:", self.living_city_field)
        form_layout.addRow("Адрес проживания*:", self.living_address_field)
        form_layout.addRow("Место работы:", self.workplace_field)
        form_layout.addRow("Должность:", self.position_field)
        form_layout.addRow("Мобильный телефон*:", self.phone_field)
        form_layout.addRow("Email*:", self.email_field)

        photo_layout = QVBoxLayout()
        photo_layout.addWidget(self.photo_preview)
        photo_layout.addWidget(self.photo_path_label)
        photo_layout.addWidget(self.choose_photo_button)
        form_layout.addRow("Фотография*:", photo_layout)

        form_layout.addRow("Замечания:", self.notes_field)
        form_layout.addRow("", self.submit_button)

        self.setLayout(form_layout)

    def choose_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите фотографию", "", "Images (*.jpg *.png)")
        if file_path:
            try:
                image = Image.open(file_path)
                width, height = image.size
                file_size = os.path.getsize(file_path)

                # if width / height != 3 / 4:
                #     raise ValueError("Соотношение сторон изображения должно быть 3:4.")
                if height < width:
                     raise ValueError("Изображение должно быть вертикальным.")
                if file_size > 2 * 1024 * 1024:
                     raise ValueError("Размер изображения не должен превышать 2 МБ.")

                self.photo_path_label.setText(f"Фото выбрано: {os.path.basename(file_path)}")
                self.photo_preview.setPixmap(QPixmap(file_path).scaled(100, 133, Qt.KeepAspectRatio))
                self.photo_path = file_path
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", str(e))

    def validate_data(self):
        errors = []
        if not self.last_name_field.text():
            errors.append("Фамилия обязательна.")
        if not self.first_name_field.text():
            errors.append("Имя обязательно.")
        if not self.middle_name_field.text():
            errors.append("Отчество обязательно.")
        if not self.passport_field.text() or not re.match(r"^\d{4}\s\d{6}$", self.passport_field.text()):
            errors.append("Паспорт должен быть в формате 'XXXX XXXXXX'.")
        if not self.registration_city_field.text():
            errors.append("Город регистрации обязателен.")
        if not self.registration_address_field.text():
            errors.append("Адрес регистрации обязателен.")
        if not self.living_city_field.text():
            errors.append("Город проживания обязателен.")
        if not self.living_address_field.text():
            errors.append("Адрес проживания обязателен.")
        if not self.phone_field.text() or not re.match(r"^\+7\d{10}$", self.phone_field.text()):
            errors.append("Телефон должен быть в формате '+7XXXXXXXXXX'.")
        if not self.email_field.text() or not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", self.email_field.text()):
            errors.append("Email имеет неверный формат.")
        if not hasattr(self, 'photo_path') or not self.photo_path:
            errors.append("Фотография обязательна.")

        if errors:
            QMessageBox.warning(self, "Ошибки", "\n".join(errors))
        else:
            QMessageBox.information(self, "Успех", "Водитель успешно сохранен!")
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    main_app.show()
    sys.exit(app.exec_())