# export_data.py

import sqlite3
import json
import csv
import xml.etree.ElementTree as ET
import yaml
import os
from database import Database


def export_all_formats():
    """Экспортирует данные о бронированиях во все форматы."""

    db = Database()

    # Создаем папку out если её нет
    if not os.path.exists('out'):
        os.makedirs('out')

    # Получаем данные из БД
    data = get_booking_data(db)

    # Экспортируем во все форматы
    export_to_json(data, 'out/data.json')
    export_to_csv(data, 'out/data.csv')
    export_to_xml(data, 'out/data.xml')
    export_to_yaml(data, 'out/data.yaml')

    print("Данные успешно экспортированы в папку out/")


def get_booking_data(db):
    """Получает данные о бронированиях с связанными таблицами."""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()

        # Сначала проверяем, есть ли бронирования
        cursor.execute("SELECT COUNT(*) FROM Booking")
        booking_count = cursor.fetchone()[0]

        # Если нет бронирований, создаем тестовые
        if booking_count == 0:
            create_test_booking_data(db)

        # Выполняем основной запрос
        cursor.execute("""
            SELECT 
                b.Booking_ID,
                b.Booking_Date,
                b.Booking_status,
                c.Customer_ID,
                c.Name as Customer_Name,
                c.Phone_number,
                car.Car_ID,
                car.Name as Car_Name,
                car.Model as Car_Model,
                car.Color as Car_Color,
                car.Price as Car_Price,
                cs.Name as Car_Status
            FROM Booking b
            JOIN Customer c ON b.Customer_ID = c.Customer_ID
            JOIN Car car ON b.Car_ID = car.Car_ID
            JOIN CarStatus cs ON car.CarStatus_ID = cs.CarStatus_ID
        """)

        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()

        # Преобразуем в список словарей
        data = []
        for row in rows:
            row_dict = dict(zip(columns, row))

            # Структурируем данные
            structured_data = {
                'booking_id': row_dict['Booking_ID'],
                'booking_date': row_dict['Booking_Date'],
                'booking_status': 'Активна' if row_dict['Booking_status'] == 0 else 'Завершена',
                'customer': {
                    'customer_id': row_dict['Customer_ID'],
                    'name': row_dict['Customer_Name'],
                    'phone': row_dict['Phone_number']
                },
                'car': {
                    'car_id': row_dict['Car_ID'],
                    'name': row_dict['Car_Name'],
                    'model': row_dict['Car_Model'],
                    'color': row_dict['Car_Color'],
                    'price': float(row_dict['Car_Price']),
                    'status': row_dict['Car_Status']
                }
            }
            data.append(structured_data)

        return data


def create_test_booking_data(db):
    """Создает тестовые бронирования если их нет"""
    with sqlite3.connect(db.db_name) as conn:
        cursor = conn.cursor()

        print("Создаем тестовые бронирования...")

        # Создаем тестового клиента
        cursor.execute("""
            INSERT OR IGNORE INTO Customer (Name, Password, Phone_number) 
            VALUES ('Иван Иванов', 'pass123', '+79991234567')
        """)

        # Получаем ID созданного клиента
        cursor.execute("SELECT Customer_ID FROM Customer WHERE Phone_number = '+79991234567'")
        customer_id = cursor.fetchone()[0]

        # Берем первую доступную машину (статус "На складе")
        cursor.execute("SELECT Car_ID FROM Car WHERE CarStatus_ID = 1 LIMIT 1")
        car_result = cursor.fetchone()

        if car_result:
            car_id = car_result[0]

            # Создаем бронирование
            from datetime import datetime
            cursor.execute("""
                INSERT INTO Booking (Customer_ID, Car_ID, Booking_Date, Booking_status) 
                VALUES (?, ?, ?, 0)
            """, (customer_id, car_id, datetime.now().strftime('%Y-%m-%d')))

            # Обновляем статус машины на "Забронирован"
            cursor.execute("UPDATE Car SET CarStatus_ID = 2 WHERE Car_ID = ?", (car_id,))

            conn.commit()
            print("Тестовое бронирование создано!")
        else:
            print("Нет доступных машин для бронирования!")


def export_to_json(data, filename):
    """Экспортирует данные в JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def export_to_csv(data, filename):
    """Экспортирует данные в CSV."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Заголовки
        writer.writerow([
            'booking_id', 'booking_date', 'booking_status',
            'customer_id', 'customer_name', 'customer_phone',
            'car_id', 'car_name', 'car_model', 'car_color', 'car_price', 'car_status'
        ])

        # Данные
        for item in data:
            writer.writerow([
                item['booking_id'],
                item['booking_date'],
                item['booking_status'],
                item['customer']['customer_id'],
                item['customer']['name'],
                item['customer']['phone'],
                item['car']['car_id'],
                item['car']['name'],
                item['car']['model'],
                item['car']['color'],
                item['car']['price'],
                item['car']['status']
            ])


def export_to_xml(data, filename):
    """Экспортирует данные в XML."""
    root = ET.Element('bookings')

    for item in data:
        booking_elem = ET.SubElement(root, 'booking')

        ET.SubElement(booking_elem, 'id').text = str(item['booking_id'])
        ET.SubElement(booking_elem, 'date').text = item['booking_date']
        ET.SubElement(booking_elem, 'status').text = item['booking_status']

        customer_elem = ET.SubElement(booking_elem, 'customer')
        ET.SubElement(customer_elem, 'id').text = str(item['customer']['customer_id'])
        ET.SubElement(customer_elem, 'name').text = item['customer']['name']
        ET.SubElement(customer_elem, 'phone').text = item['customer']['phone']

        car_elem = ET.SubElement(booking_elem, 'car')
        ET.SubElement(car_elem, 'id').text = str(item['car']['car_id'])
        ET.SubElement(car_elem, 'name').text = item['car']['name']
        ET.SubElement(car_elem, 'model').text = item['car']['model']
        ET.SubElement(car_elem, 'color').text = item['car']['color']
        ET.SubElement(car_elem, 'price').text = str(item['car']['price'])
        ET.SubElement(car_elem, 'status').text = item['car']['status']

    tree = ET.ElementTree(root)
    tree.write(filename, encoding='utf-8', xml_declaration=True)


def export_to_yaml(data, filename):
    """Экспортирует данные в YAML."""
    with open(filename, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False)


if __name__ == "__main__":
    export_all_formats()