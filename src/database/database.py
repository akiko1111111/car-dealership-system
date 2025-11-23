# database.py

import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name='car_dealership.db'):
        self.db_name = db_name
        self._create_tables()

    def _create_tables(self):
        """Создает таблицы в базе данных, если они не существуют."""
        commands = [
            """
            CREATE TABLE IF NOT EXISTS Customer (
                Customer_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Password TEXT NOT NULL,
                Phone_number TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS CarStatus (
                CarStatus_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL UNIQUE
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Car (
                Car_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Model TEXT NOT NULL,
                Price DECIMAL(10, 2) NOT NULL,
                CarStatus_ID INTEGER NOT NULL,
                FOREIGN KEY (CarStatus_ID) REFERENCES CarStatus (CarStatus_ID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Manager (
                Manager_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Name TEXT NOT NULL,
                Password TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Booking (
                Booking_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Customer_ID INTEGER NOT NULL,
                Car_ID INTEGER NOT NULL,
                Booking_Date DATETIME NOT NULL,
                Booking_status BOOLEAN NOT NULL DEFAULT 0, -- 0 = активна, 1 = завершена (подтверждена/отменена)
                FOREIGN KEY (Customer_ID) REFERENCES Customer (Customer_ID),
                FOREIGN KEY (Car_ID) REFERENCES Car (Car_ID)
            );
            """
        ]

        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            for command in commands:
                cursor.execute(command)
            conn.commit()

    def _insert_initial_data(self):
        """Наполняет базу начальными данными."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Добавляем возможные статусы автомобиля
            car_statuses = [
                (1, 'На складе'),
                (2, 'Забронирован'),
                (3, 'Продан')
            ]
            try:
                cursor.executemany("INSERT OR IGNORE INTO CarStatus (CarStatus_ID, Name) VALUES (?, ?)", car_statuses)
            except sqlite3.IntegrityError:
                pass # Игнорируем ошибку, если статусы уже есть

            # Добавляем тестового менеджера
            managers = [('Админ', 'admin')]
            try:
                cursor.executemany("INSERT OR IGNORE INTO Manager (Name, Password) VALUES (?, ?)", managers)
            except sqlite3.IntegrityError:
                pass

            # Добавляем тестовые автомобили
            cars = [
                ('Toyota', 'Camry', 2500000.00, 1), # На складе
                ('Honda', 'Civic', 1800000.00, 1),  # На складе
                ('BMW', 'X5', 5000000.00, 3),       # Продан
            ]
            try:
                cursor.executemany("INSERT OR IGNORE INTO Car (Name, Model, Price, CarStatus_ID) VALUES (?, ?, ?, ?)", cars)
            except sqlite3.IntegrityError:
                pass

            conn.commit()

# При первом запуске создастся база с таблицами и тестовыми данными
if __name__ == "__main__":
    db = Database()
    db._insert_initial_data()
    print("База данных инициализирована успешно!")