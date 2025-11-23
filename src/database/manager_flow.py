# manager_flow.py

import sqlite3

def manager_login():
    """Простая авторизация менеджера."""
    name = input("Имя менеджера: ")
    password = input("Пароль: ")
    # В реальном приложении пароль должен быть хеширован!
    return name == "Админ" and password == "admin"

def manager_menu(db):
    if not manager_login():
        print("Ошибка авторизации!")
        return

    while True:
        print("\n--- Панель управления менеджера ---")
        print("1. Просмотреть все бронирования")
        print("2. Подтвердить бронирование (оформить продажу)")
        print("3. Отменить бронирование")
        print("4. Добавить автомобиль")
        print("5. Сменить статус автомобиля")
        print("6. Выйти в главное меню")
        choice = input("Выберите действие: ")

        if choice == '1':
            view_all_bookings(db)
        elif choice == '2':
            confirm_booking(db)
        elif choice == '3':
            cancel_booking(db)
        elif choice == '4':
            add_car(db)
        elif choice == '5':
            change_car_status(db)
        elif choice == '6':
            break
        else:
            print("Неверный ввод.")

def view_all_bookings(db):
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.Booking_ID, c.Name, c.Phone_number, car.Name || ' ' || car.Model, b.Booking_Date, b.Booking_status
            FROM Booking b
            JOIN Customer c ON b.Customer_ID = c.Customer_ID
            JOIN Car car ON b.Car_ID = car.Car_ID
            WHERE b.Booking_status = 0 -- Только активные брони
        """)
        bookings = cursor.fetchall()

    if not bookings:
        print("Активных бронирований нет.")
        return

    print("\n--- Список всех активных бронирований ---")
    for book in bookings:
        print(f"ID брони: {book[0]}, Клиент: {book[1]}, Телефон: {book[2]}, Авто: {book[3]}, Дата: {book[4]}")

def confirm_booking(db):
    """Менеджер подтверждает бронь, автомобиль помечается как проданный."""
    booking_id = input("Введите ID бронирования для подтверждения: ")
    if not booking_id.isdigit():
        print("Ошибка: ID должен быть числом.")
        return

    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()
        try:
            # Получаем Car_ID из брони
            cursor.execute("SELECT Car_ID FROM Booking WHERE Booking_ID = ? AND Booking_status = 0", (booking_id,))
            result = cursor.fetchone()
            if not result:
                print("Бронирование с таким ID не найдено или уже обработано.")
                return

            car_id = result[0]
            # Меняем статус автомобиля на "Продан" (ID=3)
            cursor.execute("UPDATE Car SET CarStatus_ID = 3 WHERE Car_ID = ?", (car_id,))
            # Помечаем бронь как завершенную
            cursor.execute("UPDATE Booking SET Booking_status = 1 WHERE Booking_ID = ?", (booking_id,))
            conn.commit()
            print("Бронирование подтверждено. Автомобиль помечен как проданный.")
        except sqlite3.Error as e:
            print(f"Произошла ошибка: {e}")

# Аналогично нужно реализовать функции cancel_booking, add_car, change_car_status.
# Их структура будет очень похожа на confirm_booking.