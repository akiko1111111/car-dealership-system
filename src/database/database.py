# database.py

import sqlite3
from datetime import datetime


class Database:
    def __init__(self, db_name='car_dealership.db'):
        self.db_name = db_name
        self._create_tables()
        self._insert_initial_data()

    def _create_tables(self):
        """Создает таблицы в базе данных."""
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
                Color TEXT NOT NULL,
                Price DECIMAL(10, 2) NOT NULL,
                CarStatus_ID INTEGER NOT NULL,
                UNIQUE(Name, Model, Color),
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
                Booking_status BOOLEAN NOT NULL DEFAULT 0,
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
        """Добавляет начальные данные в базу."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Статусы машин
            car_statuses = [
                (1, 'На складе'),
                (2, 'Забронирован'),
                (3, 'Продан')
            ]
            cursor.executemany("INSERT OR IGNORE INTO CarStatus (CarStatus_ID, Name) VALUES (?, ?)", car_statuses)

            # Менеджер
            managers = [('Админ', 'admin')]
            cursor.executemany("INSERT OR IGNORE INTO Manager (Name, Password) VALUES (?, ?)", managers)

            # Проверяем, есть ли уже машины
            cursor.execute("SELECT COUNT(*) FROM Car")
            car_count = cursor.fetchone()[0]

            # Если машин нет - добавляем
            if car_count == 0:
                cars = [
                    ('Genesis', 'GV80', 'Серый', 8000000.00, 1),
                    ('Haval', 'F7', 'Океанический лазурит', 3500000.00, 1),
                    ('Kia', 'Sportage', 'Темно-серый', 2000000.00, 1),
                    ('Zeekr', '001', 'Оранжевый', 16000000.00, 1),
                    ('Infiniti', 'QX70', 'Чёрный', 4000000.00, 1),
                    ('Infiniti', 'QX60', 'Темно-синий', 4500000.00, 1),
                    ('Infiniti', 'QX80', 'Чёрный', 4000000.00, 1),
                    ('Volvo', 'XC70', 'Серебристо-коричневый', 3500000.00, 1),
                    ('Toyota', 'Camry', 'Чёрный', 2500000.00, 1),
                    ('Honda', 'CR-V', 'Черный', 5000000.00, 1),
                    ('BMW', 'X5', 'Синий', 5000000.00, 3),
                    ('Kia', 'Rio', 'Красный', 1200000.00, 1),
                    ('Mercedes', 'E-Class', 'Серебристый', 4500000.00, 1),
                ]

                for car in cars:
                    try:
                        cursor.execute(
                            "INSERT INTO Car (Name, Model, Color, Price, CarStatus_ID) VALUES (?, ?, ?, ?, ?)",
                            car
                        )
                    except sqlite3.IntegrityError:
                        pass

            conn.commit()


if __name__ == "__main__":
    db = Database()