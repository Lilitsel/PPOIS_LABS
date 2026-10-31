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
    print("10. Увеличить/уменьшить числовые элементы")
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
                print("Элемент успешно удален.")
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
from lab1.real_matrix import RealMatrix


def print_menu():
    print('\nМеню управления вещественной матрицей: ')
    print('1. Создать новую матрицу вручную')
    print('2. Загрузить матрицу из файла')
    print('3. Вывести матрицу на экран')
    print('4. Изменить размер матрицы')
    print('5. Инкремент всех элементов')
    print('6. Декремент всех элементов')
    print('7. Транспонировать матрицу')
    print('8. Извлечь подматрицу')
    print('9. Проверить свойства матрицы')

    print('10. Сохранить матрицу в файл')
    print('0. Выход')


def main():
    matrix: RealMatrix | None = None

    while True:
        print_menu()
        choice = input('Выберите пункт меню: ').strip()

        try:
            if choice == '1':
                r = int(input('Введите число строк: '))
                c = int(input('Введите число столбцов: '))
                print('Введите элементы по строкам через пробел:')
                lines = []
                for i in range(r):
                    lines.append(input(f'Строка {i + 1}: '))
                text = '\n'.join(lines)
                matrix = RealMatrix.from_string(text)
                print('Матрица успешно создана!')

            elif choice == '2':
                path = input('Введите путь к файлу: ').strip()
                matrix = RealMatrix.load_from_file(path)
                print('Матрица успешно загружена из файла!')

            elif choice == '3':
                if matrix:
                    print('\nТекущая матрица:')
                    print(matrix)
                else:
                    print('Матрица еще не создана.')

            elif choice == '4':
                if not matrix:
                    print('Сначала создайте матрицу.')
                    continue
                r = int(input('Новое число строк: '))
                c = int(input('Новое число столбцов: '))
                val = float(input('Значение по умолчанию для новых ячеек: '))
                matrix.resize(r, c, val)
                print('Размер матрицы изменен.')

            elif choice == '5':
                if matrix:
                    matrix.increment()
                    print('Инкремент выполнен успешно.')
                else:
                    print('Матрица не создана.')

            elif choice == '6':
                if matrix:
                    matrix.decrement()
                    print('Декремент выполнен успешно.')
                else:
                    print('Матрица не создана.')

            elif choice == '7':
                if matrix:
                    matrix = matrix.transpose()
                    print('Матрица транспонирована:')
                    print(matrix)
                else:
                    print('Матрица не создана.')

            elif choice == '8':
                if not matrix:
                    print('Сначала создайте матрицу.')
                    continue
                sr = int(input('Начальная строка): '))
                sc = int(input('Начальный столбец: '))
                sub_r = int(input('Количество строк подматрицы: '))
                sub_c = int(input('Количество столбцов подматрицы: '))
                sub = matrix.get_submatrix(sr, sc, sub_r, sub_c)
                print('\nИзвлеченная подматрица:')
                print(sub)

            elif choice == '9':
                if not matrix:
                    print('Сначала создайте матрицу.')
                    continue
                print(f'Квадратная: {matrix.is_square()}')
                print(f'Нулевая: {matrix.is_zero()}')
                print(f'Единичная: {matrix.is_identity()}')
                print(f'Диагональная: {matrix.is_diagonal()}')
                print(f'Симметрическая: {matrix.is_symmetric()}')
                print(f'Верхняя треугольная: {matrix.is_upper_triangular()}')
                print(f'Нижняя треугольная: {matrix.is_lower_triangular()}')

            elif choice == '10':
                if matrix:
                    path = input('Введите путь для сохранения файла: ').strip()
                    matrix.save_to_file(path)
                    print('Матрица сохранена.')
                else:
                    print('Матрица не создана.')

            elif choice == '0':
                print('Выход из программы.')
                break
            else:
                print('Неверный выбор. Попробуйте снова.')

        except Exception as e:
            print(f'[Ошибка!!!]: {e}')


if __name__ == '__main__':
    main()