from real_matrix import RealMatrix


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