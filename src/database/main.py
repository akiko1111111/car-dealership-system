# main.py

from database import Database

def main():
    db = Database() # Инициализация базы данных

    while True:
        print("\n--- Добро пожаловать в систему автосалона! ---")
        print("1. Я клиент")
        print("2. Я менеджер")
        print("3. Выйти")
        choice = input("Выберите роль: ")

        if choice == '1':
            from customer_flow import customer_menu
            customer_menu(db)
        elif choice == '2':
            from manager_flow import manager_menu
            manager_menu(db)
        elif choice == '3':
            print("До свидания!")
            break
        else:
            print("Неверный ввод, попробуйте снова.")

if __name__ == "__main__":
    main()