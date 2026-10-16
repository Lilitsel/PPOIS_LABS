import os
import unittest
from real_matrix import RealMatrix


class TestRealMatrix(unittest.TestCase):

  def test_init_and_dimensions(self):
    m = RealMatrix(2, 3, 5.0)
    self.assertEqual(m.get_rows(), 2)
    self.assertEqual(m.get_cols(), 3)
    self.assertEqual(m[0][0], 5.0)

    # Проверка ошибок некорректных размеров при создании
    with self.assertRaises(ValueError):
      RealMatrix(0, 3)
    with self.assertRaises(ValueError):
      RealMatrix(2, -1)

#Тест доступа по индексам и замены строки
  def test_getitem_and_setitem(self):
    m = RealMatrix(2, 2, 0.0)
    m[0] = [1.0, 2.0]
    self.assertEqual(m[0], [1.0, 2.0])

    # Ошибка при несоответствии длины строки количеству столбцов
    with self.assertRaises(ValueError):
      m[0] = [1.0, 2.0, 3.0]

#Тест сравнения матриц (__eq__ и __ne__)
  def test_equality_and_inequality(self):
    m1 = RealMatrix(2, 2, 1.0)
    m2 = RealMatrix(2, 2, 1.0)
    m3 = RealMatrix(2, 2, 2.0)
    m4 = RealMatrix(2, 3, 1.0)

    self.assertEqual(m1, m2)
    self.assertNotEqual(m1, m3)
    self.assertNotEqual(m1, m4)
    self.assertNotEqual(m1, "not a matrix")

    # Проверка неравенства (__ne__)
    self.assertTrue(m1 != m3)
    self.assertFalse(m1 != m2)

#Tест строковых представлений (__str__ и __repr__)
  def test_string_representations(self):
    m = RealMatrix(1, 1, 3.5)
    self.assertIn("3.5000", str(m))
    self.assertIn("RealMatrix", repr(m))

#Тест создания матрицы из строки и обработки ошибок
  def test_from_string_and_errors(self):
    text = "1.0 2.0\n3.0 4.0"
    m = RealMatrix.from_string(text)
    self.assertEqual(m.get_rows(), 2)
    self.assertEqual(m.get_cols(), 2)
    self.assertEqual(m[1][1], 4.0)

    # Пустой текст
    with self.assertRaises(ValueError):
      RealMatrix.from_string("   \n  ")

    # Разное количество элементов в строках
    with self.assertRaises(ValueError):
      RealMatrix.from_string("1.0 2.0\n3.0")

#Тест сохранения и загрузки из файла
  def test_file_operations(self):
    m = RealMatrix(2, 2, 4.0)
    filename = "temp_test_matrix.txt"
    try:
      m.save_to_file(filename)
      m_loaded = RealMatrix.load_from_file(filename)
      self.assertEqual(m, m_loaded)
    finally:
      if os.path.exists(filename):
        os.remove(filename)

#Тест инкремента и декремента
  def test_increment_and_decrement(self):
    m = RealMatrix(2, 2, 1.0)
    m.increment()
    self.assertEqual(m[0][0], 2.0)
    m.decrement()
    self.assertEqual(m[0][0], 1.0)

#Тест изменения размера матрицы
  def test_resize(self):
    m = RealMatrix(2, 2, 1.0)
    # Увеличение размера
    m.resize(3, 3, 9.0)
    self.assertEqual(m.get_rows(), 3)
    self.assertEqual(m.get_cols(), 3)
    self.assertEqual(m[0][0], 1.0)  # Старые данные сохранились
    self.assertEqual(m[2][2], 9.0)  # Новая ячейка заполнена fill_value

    # Уменьшение размера
    m.resize(1, 1)
    self.assertEqual(m.get_rows(), 1)
    self.assertEqual(m[0][0], 1.0)

    # Неверный новый размер
    with self.assertRaises(ValueError):
      m.resize(0, 2)

#Тест транспонирования матрицы
  def test_transpose(self):
    text = "1.0 2.0\n3.0 4.0"
    m = RealMatrix.from_string(text)
    t = m.transpose()
    self.assertEqual(t[0], [1.0, 3.0])
    self.assertEqual(t[1], [2.0, 4.0])

#Тест извлечения подматрицы и проверка границ
  def test_get_submatrix(self):
    text = "1.0 2.0 3.0\n4.0 5.0 6.0\n7.0 8.0 9.0"
    m = RealMatrix.from_string(text)
    sub = m.get_submatrix(1, 1, 2, 2)
    self.assertEqual(sub[0], [5.0, 6.0])
    self.assertEqual(sub[1], [8.0, 9.0])

    # Некорректные параметры подматрицы
    with self.assertRaises(ValueError):
      m.get_submatrix(-1, 0, 2, 2)
    with self.assertRaises(ValueError):
      m.get_submatrix(0, 0, 0, 2)
    with self.assertRaises(ValueError):
      m.get_submatrix(1, 1, 5, 5)

#Тест свойств: квадратная и нулевая матрица
  def test_matrix_properties_square_and_zero(self):
    sq = RealMatrix(2, 2, 1.0)
    self.assertTrue(sq.is_square())
    rect = RealMatrix(2, 3, 1.0)
    self.assertFalse(rect.is_square())

    zero_m = RealMatrix(2, 2, 0.0)
    self.assertTrue(zero_m.is_zero())
    self.assertFalse(sq.is_zero())

#Тест свойств: единичная и диагональная матрица
  def test_matrix_properties_identity_and_diagonal(self):
    id_m = RealMatrix.from_string("1.0 0.0\n0.0 1.0")
    self.assertTrue(id_m.is_identity())
    self.assertTrue(id_m.is_diagonal())

    diag_m = RealMatrix.from_string("5.0 0.0\n0.0 -2.0")
    self.assertFalse(diag_m.is_identity())
    self.assertTrue(diag_m.is_diagonal())

    # Прямоугольная матрица для проверки False на не-квадратность
    rect = RealMatrix(2, 3, 0.0)
    self.assertFalse(rect.is_identity())
    self.assertFalse(rect.is_diagonal())

#Тест свойства симметричности
  def test_matrix_properties_symmetric(self):
    sym_m = RealMatrix.from_string("1.0 2.0\n2.0 3.0")
    self.assertTrue(sym_m.is_symmetric())

    non_sym = RealMatrix.from_string("1.0 2.0\n3.0 1.0")
    self.assertFalse(non_sym.is_symmetric())
    self.assertFalse(RealMatrix(2, 3, 1.0).is_symmetric())

#Тест верхней и нижней треугольных матриц
  def test_matrix_properties_triangular(self):
    upper = RealMatrix.from_string("1.0 2.0\n0.0 3.0")
    self.assertTrue(upper.is_upper_triangular())
    self.assertFalse(upper.is_lower_triangular())

    lower = RealMatrix.from_string("1.0 0.0\n2.0 3.0")
    self.assertTrue(lower.is_lower_triangular())
    self.assertFalse(lower.is_upper_triangular())

    rect = RealMatrix(2, 3, 1.0)
    self.assertFalse(rect.is_upper_triangular())
    self.assertFalse(rect.is_lower_triangular())


if __name__ == "__main__":
  unittest.main()