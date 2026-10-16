from __future__ import annotations
from typing import List
from lab1.abstract_matrix import IMatrix


class RealMatrix(IMatrix):

  EPSILON = 1e-9

  def __init__( self, rows: int, cols: int, initial_value: float = 0.0) -> None:
    if rows <= 0 or cols <= 0:
      raise ValueError('Размеры матрицы должны быть положительными числами')
    self._rows = rows
    self._cols = cols
    self._data: List[List[float]] = [[float(initial_value) for _ in range(cols)] for _ in range(rows)]

  def get_rows(self) -> int:
    return self._rows

  def get_cols(self) -> int:
    return self._cols

#Индексация для доступа к строкам матрицы
  def __getitem__(self, index: int) -> List[float]:
    return self._data[index]

#заменяем целую строку матрицы по индексу
  def __setitem__(self, index: int, value: List[float]) -> None:
    if len(value) != self._cols:
      raise ValueError('Длина строки не соответствует числу столбцов.')
    self._data[index] = [float(v) for v in value]

  # Сравнение на равенство
  def __eq__(self, other: object) -> bool:
    if not isinstance(other, RealMatrix):
      return NotImplemented
    if self._rows != other._rows or self._cols != other._cols:
      return False
    for i in range(self._rows):
      for j in range(self._cols):
        if abs(self._data[i][j] - other._data[i][j]) > self.EPSILON:
          return False
    return True

  def __ne__(self, other: object) -> bool:
    result = self.__eq__(other)
    if result is NotImplemented:
      return NotImplemented
    return not result

  # Вывод и чтение объекта
  def __str__(self) -> str:
    return '\n'.join(['\t'.join(f'{val:10.4f}' for val in row) for row in self._data])


  def __repr__(self) -> str:
    return (
        f'RealMatrix(rows={self._rows}, cols={self._cols}, data={self._data})'
    )

  @classmethod
  #Создает матрицу из строки
  def from_string(cls, text: str) -> RealMatrix:
    lines = [
        line.strip() for line in text.strip().split('\n') if line.strip()
    ]
    if not lines:
      raise ValueError('Пустой текст для инициализации матрицы.')
    data = []
    for line in lines:
      row = [float(x) for x in line.split()]
      data.append(row)

    rows = len(data)
    cols = len(data[0])
    for row in data:
      if len(row) != cols:
        raise ValueError('Все строки должны содержать одинаковое число элементов.')

    matrix = cls(rows, cols)
    matrix._data = data
    return matrix

  @classmethod
  def load_from_file(cls, filepath: str) -> RealMatrix:
    with open(filepath, 'r', encoding='utf-8') as f:
      content = f.read()
    return cls.from_string(content)

  def save_to_file(self, filepath: str) -> None:
    with open(filepath, 'w', encoding='utf-8') as f:
      f.write(str(self))

  # Пре- и постинкремент/декремент
  def increment(self) -> RealMatrix:

    for i in range(self._rows):
      for j in range(self._cols):
        self._data[i][j] += 1.0
    return self

  def decrement(self) -> RealMatrix:
    for i in range(self._rows):
      for j in range(self._cols):
        self._data[i][j] -= 1.0
    return self

#Изменение числа строк и столбцов матрицы
  def resize(self, new_rows: int, new_cols: int, fill_value: float = 0.0) -> None:
    if new_rows <= 0 or new_cols <= 0:
      raise ValueError('Новые размеры должны быть положительными.')

    new_data = [[float(fill_value) for _ in range(new_cols)] for _ in range(new_rows)]
    for i in range(min(self._rows, new_rows)):
      for j in range(min(self._cols, new_cols)):
        new_data[i][j] = self._data[i][j]

    self._rows = new_rows
    self._cols = new_cols
    self._data = new_data

  def transpose(self) -> RealMatrix:
    transposed = RealMatrix(self._cols, self._rows)
    for i in range(self._rows):
      for j in range(self._cols):
        transposed._data[j][i] = self._data[i][j]
    return transposed

#Извлечение подматрицы заданного размера
  def get_submatrix(self, start_row: int, start_col: int, sub_rows: int, sub_cols: int) -> RealMatrix:
    if (
        start_row < 0
        or start_col < 0
        or sub_rows <= 0
        or sub_cols <= 0
        or start_row + sub_rows > self._rows
        or start_col + sub_cols > self._cols
    ):
      raise ValueError('Некорректные параметры для извлечения подматрицы.')

    sub = RealMatrix(sub_rows, sub_cols)
    for i in range(sub_rows):
      for j in range(sub_cols):
        sub._data[i][j] = self._data[start_row + i][start_col + j]
    return sub


  def is_square(self) -> bool:
    return self._rows == self._cols

  def is_zero(self) -> bool:
    return all(
        abs(val) < self.EPSILON for row in self._data for val in row
    )

#единичная ли
  def is_identity(self) -> bool:
    if not self.is_square():
      return False
    for i in range(self._rows):
      for j in range(self._cols):
        if i == j:
          expected = 1.0
        else:
          expected = 0.0
        if abs(self._data[i][j] - expected) > self.EPSILON:
          return False
    return True

  def is_diagonal(self) -> bool:
    if not self.is_square():
      return False
    for i in range(self._rows):
      for j in range(self._cols):
        if i != j and abs(self._data[i][j]) > self.EPSILON:
          return False
    return True

  def is_symmetric(self) -> bool:
    if not self.is_square():
      return False
    for i in range(self._rows):
      for j in range(i + 1, self._cols):
        if abs(self._data[i][j] - self._data[j][i]) > self.EPSILON:
          return False
    return True

  def is_upper_triangular(self) -> bool:
    if not self.is_square():
      return False
    for i in range(1, self._rows):
      for j in range(i):
        if abs(self._data[i][j]) > self.EPSILON:
          return False
    return True

  def is_lower_triangular(self) -> bool:
    if not self.is_square():
      return False
    for i in range(self._rows):
      for j in range(i + 1, self._cols):
        if abs(self._data[i][j]) > self.EPSILON:
          return False
    return True