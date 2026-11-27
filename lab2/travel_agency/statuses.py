"""Перечисления состояний объектов предметной области."""
from enum import Enum


class BookingStatus(Enum):
    PENDING = "ожидает оплаты"
    CONFIRMED = "подтверждено"
    CANCELLED = "отменено"
    COMPLETED = "завершено"


class PaymentStatus(Enum):
    PENDING = "ожидает"
    COMPLETED = "проведён"
    REFUNDED = "возвращён"


class RefundStatus(Enum):
    PENDING = "на рассмотрении"
    APPROVED = "одобрен"
    REJECTED = "отклонён"
    EXECUTED = "выполнен"


class TicketStatus(Enum):
    ISSUED = "выписан"
    CHECKED_IN = "регистрация пройдена"
    CANCELLED = "аннулирован"


class ComplaintStatus(Enum):
    OPEN = "открыта"
    ESCALATED = "эскалирована"
    RESOLVED = "решена"
