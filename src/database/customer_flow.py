# customer_flow.py

import sqlite3
from datetime import datetime

def customer_auth(db):
    """Регистрация или авторизация клиента."""
    phone = input("Введите ваш номер телефона: ")
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT Customer_ID, Name, Password FROM Customer WHERE Phone_number = ?", (phone,))
        customer = cursor.fetchone()

        if customer:
            # Клиент найден - запрашиваем пароль
            password = input("Введите пароль: ")
            if password == customer[2]:
                print(f"Добро пожаловать, {customer[1]}!")
                return customer[0]
            else:
                print("Неверный пароль!")
                return None
        else:
            # Новый клиент - регистрация
            print("Номер не найден. Требуется регистрация.")
            name = input("Введите ваше имя: ")
            password = input("Придумайте пароль: ")
            try:
                cursor.execute("INSERT INTO Customer (Name, Password, Phone_number) VALUES (?, ?, ?)",
                               (name, password, phone))
                conn.commit()
                new_id = cursor.lastrowid
                print("Регистрация прошла успешно!")
                return new_id
            except sqlite3.IntegrityError:
                print("Этот номер телефона уже зарегистрирован.")
                return None

def customer_menu(db):
    customer_id = customer_auth(db)
    if not customer_id:
        return

    while True:
        print("\n--- Личный кабинет клиента ---")
        print("1. Просмотреть каталог автомобилей")
        print("2. Забронировать автомобиль")
        print("3. Мои бронирования")
        print("4. Выйти в главное меню")
        choice = input("Выберите действие: ")

        if choice == '1':
            view_car_catalog(db)
        elif choice == '2':
            book_car(db, customer_id)
        elif choice == '3':
            view_my_bookings(db, customer_id)
        elif choice == '4':
            break
        else:
            print("Неверный ввод.")

def view_car_catalog(db):
    """Показывает автомобили со статусом 'На складе'."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Car_ID, Name, Model, Color, Price FROM Car
            WHERE CarStatus_ID = 1
        """)
        cars = cursor.fetchall()

    if not cars:
        print("Нет доступных для бронирования автомобилей.")
        return

    print("\n--- Доступные автомобили ---")
    for car in cars:
        print(f"ID: {car[0]}, {car[1]} {car[2]}, Цвет: {car[3]}, Цена: {car[4]:.2f} руб.")

def book_car(db, customer_id):
    """Процесс бронирования автомобиля."""
    view_car_catalog(db)
    car_id = input("Введите ID автомобиля для бронирования: ")
    if not car_id.isdigit():
        print("Ошибка: ID должен быть числом.")
        return

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT CarStatus_ID, Name, Model, Color FROM Car WHERE Car_ID = ?", (car_id,))
        car_info = cursor.fetchone()

        if not car_info:
            print("Автомобиль с таким ID не найден.")
            return
        if car_info[0] != 1:
            print("Этот автомобиль недоступен для бронирования.")
            return

        try:
            booking_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Booking (Customer_ID, Car_ID, Booking_Date, Booking_status) VALUES (?, ?, ?, ?)",
                           (customer_id, car_id, booking_date, 0))
            cursor.execute("UPDATE Car SET CarStatus_ID = 2 WHERE Car_ID = ?", (car_id,))
            conn.commit()
            print(f"Автомобиль {car_info[1]} {car_info[2]} ({car_info[3]}) успешно забронирован! Ожидайте звонка менеджера.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка при бронировании: {e}")

def view_my_bookings(db, customer_id):
    """Показывает бронирования текущего клиента."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.Booking_ID, car.Name, car.Model, car.Color, b.Booking_Date, b.Booking_status
            FROM Booking b
            JOIN Car car ON b.Car_ID = car.Car_ID
            WHERE b.Customer_ID = ?
        """, (customer_id,))
        bookings = cursor.fetchall()

    if not bookings:
        print("У вас нет бронирований.")
        return

    print("\n--- Ваши бронирования ---")
    for book in bookings:
        status = "Подтверждена" if book[5] == 1 else "Активна (ожидание)"
        print(f"ID брони: {book[0]}, Авто: {book[1]} {book[2]}, Цвет: {book[3]}, Дата: {book[4]}, Статус: {status}")