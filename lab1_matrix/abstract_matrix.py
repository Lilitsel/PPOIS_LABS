from abc import ABC, abstractmethod


class IMatrix(ABC):

  @abstractmethod
  def get_rows(self) -> int:
    pass

  @abstractmethod
  def get_cols(self) -> int:
    pass

  @abstractmethod
  def transpose(self) -> 'IMatrix':
    pass