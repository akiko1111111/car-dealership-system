# manager_flow.py

import sqlite3


def manager_login():
    """Простая авторизация менеджера."""
    name = input("Имя менеджера: ")
    password = input("Пароль: ")
    return name == "Админ" and password == "admin"


def manager_menu(db):
    if not manager_login():
        print("Ошибка авторизации!")
        return

    while True:
        print("\n--- Панель управления менеджера ---")
        print("1. Управление бронированиями")
        print("2. Добавить автомобиль")
        print("3. Просмотреть все автомобили")
        print("4. Сменить статус автомобиля")
        print("5. Выйти в главное меню")
        choice = input("Выберите действие: ")

        if choice == '1':
            manage_bookings(db)
        elif choice == '2':
            add_car(db)
        elif choice == '3':
            view_all_cars(db)
        elif choice == '4':
            change_car_status(db)
        elif choice == '5':
            break
        else:
            print("Неверный ввод.")


def manage_bookings(db):
    """Управление бронированиями - просмотр и действия с конкретными бронями."""
    while True:
        print("\n--- Управление бронированиями ---")
        print("1. Просмотреть все активные бронирования")
        print("2. Вернуться в предыдущее меню")
        sub_choice = input("Выберите действие: ")

        if sub_choice == '1':
            view_and_manage_bookings(db)
        elif sub_choice == '2':
            break
        else:
            print("Неверный ввод.")


def view_and_manage_bookings(db):
    """Просмотр бронирований с возможностью управления каждой бронью."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.Booking_ID, c.Name, c.Phone_number, 
                   car.Name || ' ' || car.Model, car.Color, b.Booking_Date,
                   car.Car_ID
            FROM Booking b
            JOIN Customer c ON b.Customer_ID = c.Customer_ID
            JOIN Car car ON b.Car_ID = car.Car_ID
            WHERE b.Booking_status = 0
        """)
        bookings = cursor.fetchall()

    if not bookings:
        print("Активных бронирований нет.")
        return

    print("\n--- Список всех активных бронирований ---")
    for book in bookings:
        print(f"ID брони: {book[0]}, Клиент: {book[1]}, Телефон: {book[2]}")
        print(f"   Авто: {book[3]}, Цвет: {book[4]}, Дата: {book[5]}")
        print("   " + "-" * 50)

    # Выбор брони для управления
    booking_id = input("\nВведите ID брони для управления (или 0 для возврата): ")
    if booking_id == '0':
        return

    if not booking_id.isdigit():
        print("Ошибка: ID должен быть числом.")
        return

    # Находим выбранную бронь
    selected_booking = None
    for book in bookings:
        if str(book[0]) == booking_id:
            selected_booking = book
            break

    if not selected_booking:
        print("Бронирование с таким ID не найдено.")
        return

    # Меню управления выбранной бронью
    while True:
        print(f"\n--- Управление бронированием ID: {selected_booking[0]} ---")
        print(f"Клиент: {selected_booking[1]}, Телефон: {selected_booking[2]}")
        print(f"Автомобиль: {selected_booking[3]}, Цвет: {selected_booking[4]}")
        print("1. Подтвердить бронирование (оформить продажу)")
        print("2. Отменить бронирование")
        print("3. Вернуться к списку бронирований")

        action = input("Выберите действие: ")

        if action == '1':
            confirm_single_booking(db, selected_booking[0], selected_booking[6])
            break
        elif action == '2':
            cancel_single_booking(db, selected_booking[0], selected_booking[6])
            break
        elif action == '3':
            break
        else:
            print("Неверный ввод.")


def confirm_single_booking(db, booking_id, car_id):
    """Подтверждение конкретной брони."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Car SET CarStatus_ID = 3 WHERE Car_ID = ?", (car_id,))
            cursor.execute("UPDATE Booking SET Booking_status = 1 WHERE Booking_ID = ?", (booking_id,))
            conn.commit()
            print("Бронирование подтверждено. Автомобиль помечен как проданный.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")


def cancel_single_booking(db, booking_id, car_id):
    """Отмена конкретной брони."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Car SET CarStatus_ID = 1 WHERE Car_ID = ?", (car_id,))
            cursor.execute("UPDATE Booking SET Booking_status = 1 WHERE Booking_ID = ?", (booking_id,))
            conn.commit()
            print("Бронирование отменено. Автомобиль возвращен на склад.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")


def add_car(db):
    """Добавление нового автомобиля в каталог."""
    print("\n--- Добавление нового автомобиля ---")

    name = input("Марка автомобиля: ")
    model = input("Модель автомобиля: ")
    color = input("Цвет автомобиля: ")
    price = input("Цена автомобиля: ")

    try:
        price = float(price)
        if price <= 0:
            print("Ошибка: цена должна быть положительным числом.")
            return
    except ValueError:
        print("Ошибка: цена должна быть числом.")
        return

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO Car (Name, Model, Color, Price, CarStatus_ID) VALUES (?, ?, ?, ?, ?)",
                (name, model, color, price, 1)
            )
            conn.commit()
            print(f"Автомобиль '{name} {model}' успешно добавлен в каталог!")
            print(f"Цвет: {color}, Цена: {price:.2f} руб.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка при добавлении автомобиля: {e}")


def change_car_status(db):
    """Ручное изменение статуса автомобиля."""
    print("\n--- Смена статуса автомобиля ---")

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Car_ID, c.Name, c.Model, c.Color, cs.Name 
            FROM Car c 
            JOIN CarStatus cs ON c.CarStatus_ID = cs.CarStatus_ID
        """)
        cars = cursor.fetchall()

    if not cars:
        print("В каталоге нет автомобилей.")
        return

    print("\n--- Все автомобили ---")
    for car in cars:
        print(f"ID: {car[0]}, {car[1]} {car[2]}, Цвет: {car[3]}, Статус: {car[4]}")

    car_id = input("\nВведите ID автомобиля для смены статуса: ")
    if not car_id.isdigit():
        print("Ошибка: ID должен быть числом.")
        return

    print("\n--- Доступные статусы ---")
    print("1. На складе")
    print("2. Забронирован")
    print("3. Продан")

    status_choice = input("Выберите новый статус (1-3): ")
    status_map = {'1': 1, '2': 2, '3': 3}

    if status_choice not in status_map:
        print("Ошибка: выберите статус от 1 до 3.")
        return

    new_status = status_map[status_choice]

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Car SET CarStatus_ID = ? WHERE Car_ID = ?", (new_status, car_id))
            conn.commit()
            print("Статус автомобиля успешно изменен!")
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")


def view_all_cars(db):
    """Просмотр всех автомобилей в системе."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.Car_ID, c.Name, c.Model, c.Color, c.Price, cs.Name 
            FROM Car c 
            JOIN CarStatus cs ON c.CarStatus_ID = cs.CarStatus_ID
            ORDER BY c.Car_ID
        """)
        cars = cursor.fetchall()

    if not cars:
        print("В системе нет автомобилей.")
        return

    print("\n--- Все автомобили в системе ---")
    for index, car in enumerate(cars, 1):  # Нумерация с 1
        print(f"{index}. {car[1]} {car[2]}, Цвет: {car[3]}, Цена: {car[4]:.2f} руб., Статус: {car[5]} (ID в системе: {car[0]})")