"""Сотрудники туристической компании."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from travel_agency.constants import (
    BONUS_PERCENT_PER_YEAR,
    DAYS_IN_YEAR,
    DEFAULT_AGENT_COMMISSION_PERCENT,
    DEFAULT_REFUND_APPROVAL_LIMIT,
    MAX_BONUS_PERCENT,
    MAX_GUIDE_RATING,
    MAX_MANAGER_DISCOUNT_PERCENT,
    MIN_GUIDE_RATING,
    PERCENT_BASE,
)
from travel_agency.exceptions import (
    InvalidBookingStateException,
    InvalidClientDataException,
    RefundNotAllowedException,
    StaffNotQualifiedException,
)
from travel_agency.finance.reports import Invoice, SalesReport
from travel_agency.people.person import Person
from travel_agency.statuses import RefundStatus

if TYPE_CHECKING:
    from travel_agency.booking.booking import Booking
    from travel_agency.company.company import Branch
    from travel_agency.finance.cards import Refund
    from travel_agency.people.person import Client
    from travel_agency.service.clients import Complaint
    from travel_agency.tours.pricing import Discount
    from travel_agency.tours.tour import Excursion
    from travel_agency.transport.ground import Bus, Transfer


class Employee(Person):
    """Базовый класс сотрудника."""

    def __init__(self, employee_id: str, person: Person, position: str, salary: float, hire_date: date):
        super().__init__(person.first_name, person.last_name, person.birth_date, person.phone, person.email)
        self.employee_id = employee_id
        self.position = position
        self.salary = salary
        self.hire_date = hire_date
        self.branch: Optional[Branch] = None

    def calculate_experience_years(self, on_date: Optional[date] = None) -> int:
        on_date = on_date or date.today()
        return max(0, (on_date - self.hire_date).days // DAYS_IN_YEAR)

    def calculate_bonus(self, on_date: Optional[date] = None) -> float:
        bonus_percent = min(self.calculate_experience_years(on_date) * BONUS_PERCENT_PER_YEAR, MAX_BONUS_PERCENT)
        return self.salary * bonus_percent / PERCENT_BASE


class TravelAgent(Employee):
    """Турагент: работает с клиентами и продаёт туры."""

    def __init__(self, employee_id: str, person: Person, salary: float, hire_date: date,
                 commission_percent: float = DEFAULT_AGENT_COMMISSION_PERCENT):
        super().__init__(employee_id, person, "Турагент", salary, hire_date)
        self.commission_percent = commission_percent
        self.assigned_clients: list[Client] = []
        self.sold_bookings: list[Booking] = []

    def assign_client(self, client: Client) -> None:
        if client not in self.assigned_clients:
            self.assigned_clients.append(client)

    def sell_tour(self, booking: Booking) -> None:
        self.assign_client(booking.client)
        self.sold_bookings.append(booking)

    def calculate_commission(self) -> float:
        sales_total = sum(booking.total_price for booking in self.sold_bookings if booking.is_active())
        return sales_total * self.commission_percent / PERCENT_BASE


class Guide(Employee):
    """Гид, проводящий экскурсии."""

    def __init__(self, employee_id: str, person: Person, salary: float, hire_date: date, languages: set[str]):
        super().__init__(employee_id, person, "Гид", salary, hire_date)
        self.languages = {language.lower() for language in languages}
        self.rating = 0.0
        self.ratings_count = 0
        self.excursions: list[Excursion] = []

    def speaks_language(self, language: str) -> bool:
        return language.lower() in self.languages

    def assign_to_excursion(self, excursion: Excursion) -> None:
        if not self.speaks_language(excursion.language):
            raise StaffNotQualifiedException(f"Гид {self.full_name} не владеет языком {excursion.language}")
        excursion.guide = self
        self.excursions.append(excursion)

    def update_rating(self, score: int) -> float:
        if not MIN_GUIDE_RATING <= score <= MAX_GUIDE_RATING:
            raise InvalidClientDataException(f"Оценка должна быть от {MIN_GUIDE_RATING} до {MAX_GUIDE_RATING}")
        total = self.rating * self.ratings_count + score
        self.ratings_count += 1
        self.rating = total / self.ratings_count
        return self.rating


class Manager(Employee):
    """Менеджер: согласует скидки, возвраты и разбирает жалобы."""

    def __init__(self, employee_id: str, person: Person, salary: float, hire_date: date,
                 approval_limit: float = DEFAULT_REFUND_APPROVAL_LIMIT):
        super().__init__(employee_id, person, "Менеджер", salary, hire_date)
        self.approval_limit = approval_limit
        self.subordinates: list[Employee] = []

    def add_subordinate(self, employee: Employee) -> None:
        if employee is not self and employee not in self.subordinates:
            self.subordinates.append(employee)

    def approve_discount(self, discount: Discount) -> None:
        if discount.percent > MAX_MANAGER_DISCOUNT_PERCENT:
            raise StaffNotQualifiedException(f"Скидка {discount.percent}% превышает полномочия менеджера")
        discount.is_approved = True

    def approve_refund(self, refund: Refund) -> None:
        if refund.amount > self.approval_limit:
            raise RefundNotAllowedException(f"Сумма {refund.amount} превышает лимит {self.approval_limit}")
        refund.approve(self)

    def review_complaint(self, complaint: Complaint, resolution: str) -> None:
        complaint.resolve(resolution)


class Accountant(Employee):
    """Бухгалтер: выставляет счета, проводит возвраты, готовит отчёты."""

    def __init__(self, employee_id: str, person: Person, salary: float, hire_date: date):
        super().__init__(employee_id, person, "Бухгалтер", salary, hire_date)
        self.issued_invoices: list[Invoice] = []
        self.processed_refunds: list[Refund] = []

    def issue_invoice(self, booking: Booking, issue_date: date) -> Invoice:
        invoice = Invoice(f"INV-{len(self.issued_invoices) + 1}", booking, issue_date)
        invoice.add_item("Туристический пакет", booking.calculate_total())
        self.issued_invoices.append(invoice)
        return invoice

    def process_refund(self, refund: Refund) -> None:
        if refund.status is not RefundStatus.APPROVED:
            raise InvalidBookingStateException("Провести можно только одобренный возврат")
        refund.execute()
        self.processed_refunds.append(refund)

    def generate_sales_report(self, bookings: list[Booking], period_start: date, period_end: date) -> SalesReport:
        return SalesReport(period_start, period_end, bookings)


class Driver(Employee):
    """Водитель автобуса для трансферов."""

    def __init__(self, employee_id: str, person: Person, salary: float, hire_date: date, license_categories: set[str]):
        super().__init__(employee_id, person, "Водитель", salary, hire_date)
        self.license_categories = {category.upper() for category in license_categories}
        self.transfers: list[Transfer] = []

    def can_drive(self, bus: Bus) -> bool:
        return bus.required_license in self.license_categories

    def assign_transfer(self, transfer: Transfer) -> None:
        if not self.can_drive(transfer.bus):
            raise StaffNotQualifiedException(f"У водителя {self.full_name} нет категории {transfer.bus.required_license}")
        transfer.driver = self
        self.transfers.append(transfer)
