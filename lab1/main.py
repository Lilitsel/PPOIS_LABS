from lab1.cantor_set import CantorSet


def show_menu():
    print("\nМеню Cantor Set")
    print("1. Создать/загрузить множество из строки")
    print("2. Вывести текущее множество")
    print("3. Добавить элемент")
    print("4. Удалить элемент")
    print("5. Проверить на пустоту")
    print("6. Мощность множества и float")
    print("7. Построить булеан (power_set)")
    print("8. Арифметические операции (+, *, -)")
    print("9. Проверить принадлежность элемента ([item])")
    print("10. Увеличить/уменьшить числовые элементы (increment / decrement)")
    print("0. Выход")


def main():
    current_set = CantorSet()

    while True:
        show_menu()
        choice = input("Выберите действие: ")

        try:
            if choice == '1':
                s = input("Введите множество (например, {a, b, {c}}): ")
                current_set = CantorSet.from_string(s)
                print(f"Множество загружено: {current_set}")
            elif choice == '2':
                print(f"Текущее множество (__str__): {current_set}")
                print(f"Представление (__repr__): {repr(current_set)}")
            elif choice == '3':
                el = input("Введите элемент: ")
                if el.isdigit():
                    el = int(el)
                current_set.add(el)
                print("Элемент добавлен.")
            elif choice == '4':
                el = input("Введите элемент для удаления: ")
                if el.isdigit():
                    el = int(el)
                current_set.remove(el)
                print("Элемент удален.")
            elif choice == '5':
                print("Пустое!" if current_set.is_empty() else "Не пустое.")
            elif choice == '6':
                print(f"Мощность (int): {len(current_set)}")
                print(f"Мощность как float (__float__): {float(current_set)}")
            elif choice == '7':
                bool_set = current_set.power_set()
                print(f"Булеан:\n{bool_set}")
            elif choice == '8':
                print("1. Объединение (+)")
                print("2. Пересечение (*)")
                print("3. Разность (-)")
                sub = input("Выберите операцию: ")
                s = input("Введите второе множество: ")
                other_set = CantorSet.from_string(s)

                if sub == '1':
                    print(f"Результат (+): {current_set + other_set}")
                elif sub == '2':
                    print(f"Результат (*): {current_set * other_set}")
                elif sub == '3':
                    print(f"Результат (-): {current_set - other_set}")
            elif choice == '9':
                el = input("Введите элемент для проверки принадлежности: ")
                if el.isdigit():
                    el = int(el)
                print(f"Принадлежит ли множеству: {current_set[el]}")
            elif choice == '10':
                print("1. increment()")
                print("2. decrement()")
                sub = input("Выберите действие: ")
                if sub == '1':
                    current_set.increment()
                    print(f"После increment: {current_set}")
                elif sub == '2':
                    current_set.decrement()
                    print(f"После decrement: {current_set}")
            elif choice == '0':
                break
            else:
                print("Неизвестная команда.")
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()