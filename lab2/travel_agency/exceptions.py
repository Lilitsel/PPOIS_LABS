"""Собственные исключения предметной области."""


class TravelAgencyException(Exception):
    """Базовое исключение туристической компании."""


class InvalidClientDataException(TravelAgencyException):
    """Некорректные данные клиента или отзыва."""


class InvalidDateRangeException(TravelAgencyException):
    """Дата окончания периода раньше даты начала."""


class PassportExpiredException(TravelAgencyException):
    """Паспорт недействителен на нужную дату."""


class VisaRequiredException(TravelAgencyException):
    """Для въезда нужна действующая виза."""


class RoomNotAvailableException(TravelAgencyException):
    """Нет свободного подходящего номера."""


class SeatNotAvailableException(TravelAgencyException):
    """Место в самолёте занято или не существует."""


class TourFullyBookedException(TravelAgencyException):
    """В туре не осталось свободных мест."""


class CapacityExceededException(TravelAgencyException):
    """Превышена вместимость экскурсии, трансфера или списка ожидания."""


class BookingNotFoundException(TravelAgencyException):
    """Бронирование не найдено."""


class InvalidBookingStateException(TravelAgencyException):
    """Операция недопустима в текущем состоянии объекта."""


class InsufficientFundsException(TravelAgencyException):
    """Недостаточно средств или бонусных баллов."""


class CardExpiredException(TravelAgencyException):
    """Срок действия банковской карты истёк."""


class InvalidPaymentDataException(TravelAgencyException):
    """Некорректная сумма, номер карты или валюта."""


class InvalidPromoCodeException(TravelAgencyException):
    """Промокод недействителен или исчерпан."""


class RefundNotAllowedException(TravelAgencyException):
    """Возврат средств невозможен."""


class InvalidTourDataException(TravelAgencyException):
    """Некорректные параметры тура, программы или пакета."""


class StaffNotQualifiedException(TravelAgencyException):
    """Сотрудник не имеет нужной квалификации."""


class EmployeeNotFoundException(TravelAgencyException):
    """Сотрудник не найден в филиале."""


class InsuranceClaimRejectedException(TravelAgencyException):
    """Страховой случай не покрывается полисом."""
