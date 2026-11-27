"""Консольное меню. Только ввод/вывод: вся логика — в предметной области."""
from datetime import date
from typing import Callable, Optional

from travel_agency.cli.demo_data import build_demo_company
from travel_agency.company.company import TravelCompany
from travel_agency.constants import BASE_CURRENCY, CARD_NUMBER_LENGTH
from travel_agency.documents.identity import Passport
from travel_agency.exceptions import InvalidPaymentDataException, TravelAgencyException
from travel_agency.finance.cards import BankCard
from travel_agency.finance.reports import SalesReport
from travel_agency.people.person import Client
from travel_agency.service.clients import LoyaltyCard

EXIT_COMMAND = "0"
DATE_HINT = "ГГГГ-ММ-ДД"


class TravelAgencyCli:
    """Интерактивное меню туристической компании."""

    def __init__(self, company: TravelCompany, input_func: Optional[Callable[[str], str]] = None,
                 output_func: Optional[Callable[[str], None]] = None):
        self.company = company
        self.read = input_func or input
        self.write = output_func or print
        self.actions = {
            "1": ("Показать доступные туры", self.show_tours),
            "2": ("Подобрать тур по цене и месяцу", self.search_tours),
            "3": ("Зарегистрировать клиента", self.register_client),
            "4": ("Забронировать тур", self.book_tour),
            "5": ("Оплатить бронирование", self.pay_booking),
            "6": ("Отменить бронирование", self.cancel_booking),
            "7": ("Бронирования клиента", self.show_client_bookings),
            "8": ("Отчёт о продажах", self.show_sales_report),
            "9": ("Уведомления клиента", self.show_notifications),
        }

    def run(self) -> None:
        self.write(f"Туристическая компания «{self.company.name}»")
        while True:
            self._print_menu()
            choice = self.read("Выберите пункт: ").strip()
            if choice == EXIT_COMMAND:
                self.write("До свидания!")
                return
            self._execute(choice)

    def _print_menu(self) -> None:
        self.write("")
        for key, (title, _) in self.actions.items():
            self.write(f"{key}. {title}")
        self.write(f"{EXIT_COMMAND}. Выход")

    def _execute(self, choice: str) -> None:
        if choice not in self.actions:
            self.write("Нет такого пункта меню")
            return
        _, action = self.actions[choice]
        try:
            action()
        except (TravelAgencyException, ValueError) as error:
            self.write(f"Ошибка: {error}")

    def _ask_date(self, prompt: str) -> date:
        return date.fromisoformat(self.read(f"{prompt} ({DATE_HINT}): ").strip())

    def _print_tours(self, tours: list) -> None:
        if not tours:
            self.write("Подходящих туров нет")
        for tour in tours:
            self.write(f"[{tour.tour_id}] {tour.name}, {tour.destination_name}, {tour.duration_days} дн., "
                       f"от {tour.base_price:.2f} {BASE_CURRENCY}, свободно мест: {tour.free_places()}")

    def show_tours(self) -> None:
        self._print_tours(self.company.search_tours())

    def search_tours(self) -> None:
        max_price = float(self.read("Максимальная цена за человека: "))
        month = int(self.read("Месяц поездки (1-12): "))
        self._print_tours(self.company.search_tours(max_price, month))

    def register_client(self) -> None:
        client_id = self.read("Номер клиента: ").strip()
        first_name = self.read("Имя: ")
        last_name = self.read("Фамилия: ")
        birth_date = self._ask_date("Дата рождения")
        phone = self.read("Телефон: ")
        email = self.read("Email: ")
        client = Client(client_id, first_name, last_name, birth_date, phone, email)
        self._attach_documents(client)
        self.company.register_client(client)
        self.write(f"Клиент {client.full_name} зарегистрирован")

    def _attach_documents(self, client: Client) -> None:
        passport_number = self.read("Номер паспорта: ")
        expiry_date = self._ask_date("Паспорт действует до")
        client.passport = Passport(passport_number, self.company.home_country, date.today(), expiry_date)
        card_number = self.read(f"Номер карты ({CARD_NUMBER_LENGTH} цифр): ").strip()
        cvv = self.read("CVV: ").strip()
        balance = float(self.read("Баланс карты: "))
        client.bank_card = BankCard(card_number, client.full_name, expiry_date, cvv, balance)
        client.loyalty_card = LoyaltyCard(f"L-{client.client_id}")

    def book_tour(self) -> None:
        client_id = self.read("Номер клиента: ").strip()
        tour_id = self.read("Код тура: ").strip().upper()
        start_date = self._ask_date("Дата начала")
        travelers = int(self.read("Количество путешественников: "))
        booking = self.company.book_tour(client_id, tour_id, (start_date, travelers), date.today())
        self.write(f"Создана бронь {booking.booking_id} на сумму {booking.total_price:.2f} {BASE_CURRENCY}")

    def pay_booking(self) -> None:
        booking = self.company.booking_service.find_booking(self.read("Номер брони: ").strip())
        card = booking.client.bank_card
        if card is None or not card.verify_cvv(self.read("CVV карты клиента: ").strip()):
            raise InvalidPaymentDataException("Карта не привязана или CVV неверен")
        payment = self.company.booking_service.pay_booking(booking.booking_id, card, date.today())
        self.write(f"Платёж {payment.payment_id} проведён. Остаток на карте: {card.balance:.2f}")

    def cancel_booking(self) -> None:
        booking_id = self.read("Номер брони: ").strip()
        reason = self.read("Причина отмены: ")
        cancellation = self.company.booking_service.cancel_booking(booking_id, reason, date.today())
        self.write(f"Бронь отменена. Штраф: {cancellation.penalty_amount:.2f} {BASE_CURRENCY}")

    def show_client_bookings(self) -> None:
        client = self.company.find_client(self.read("Номер клиента: ").strip())
        bookings = self.company.booking_service.find_by_client(client)
        if not bookings:
            self.write("У клиента нет бронирований")
        for booking in bookings:
            self.write(f"{booking.booking_id}: {booking.destination_name()}, {booking.departure_date}, "
                       f"{booking.total_price:.2f} {BASE_CURRENCY}, {booking.status.value}")

    def show_sales_report(self) -> None:
        period_start = self._ask_date("Начало периода")
        period_end = self._ask_date("Конец периода")
        report = SalesReport(period_start, period_end, self.company.all_bookings())
        self.write(f"Выручка: {report.calculate_revenue():.2f} {BASE_CURRENCY}")
        self.write(f"Средний чек: {report.average_check():.2f} {BASE_CURRENCY}")
        for city_name, sales in report.top_destinations():
            self.write(f"  {city_name}: продаж {sales}")

    def show_notifications(self) -> None:
        client = self.company.find_client(self.read("Номер клиента: ").strip())
        notifier = self.company.booking_service.notifier
        for notification in notifier.history_for(client):
            self.write(f"[{notification.channel}] {notification.message}")


def main() -> None:
    try:
        TravelAgencyCli(build_demo_company()).run()
    except (EOFError, KeyboardInterrupt):
        print("\nРабота завершена")
