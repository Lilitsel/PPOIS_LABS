"""Демонстрационные данные для консольного приложения.

Все значения собраны в таблицы-конфигурации в начале модуля;
функции ниже только создают по ним объекты предметной области.
"""
from datetime import date, datetime, time, timedelta

from travel_agency.accommodation.hotel import Hotel, MealPlan, Room, RoomType
from travel_agency.booking.service import BookingService
from travel_agency.company.company import Branch, TravelCompany
from travel_agency.documents.identity import Passport, Visa
from travel_agency.finance.cards import BankCard, PaymentProcessor
from travel_agency.geography.places import Address, Attraction, City, Country, Destination
from travel_agency.people.person import Client
from travel_agency.service.clients import LoyaltyCard
from travel_agency.service.notifications import NotificationService
from travel_agency.tours.tour import Season, Tour
from travel_agency.transport.air import Airline, Airport, Flight, Seat

COMPANY = {"name": "ВокругСвета", "license": "LIC-2026-001", "home_city": "minsk"}
BRANCH = {"name": "Главный офис", "street": "пр. Независимости", "building": "10", "postal": "220030", "hours": (9, 20)}
# ключ: (название, ISO-код, валюта, ISO-коды стран с безвизом)
COUNTRIES = {
    "BY": ("Беларусь", "BY", "BYN", ()),
    "IT": ("Италия", "IT", "EUR", ()),
    "TR": ("Турция", "TR", "TRY", ("BY",)),
    "GE": ("Грузия", "GE", "GEL", ("BY",)),
}
# ключ: (название, страна, смещение UTC, широта, долгота)
CITIES = {
    "minsk": ("Минск", "BY", 3, 53.90, 27.56),
    "rome": ("Рим", "IT", 1, 41.90, 12.50),
    "antalya": ("Анталья", "TR", 3, 36.90, 30.70),
    "tbilisi": ("Тбилиси", "GE", 4, 41.72, 44.79),
}
# (код, название, город, климат, лучшие месяцы, дней, цена, мест)
TOURS = (
    ("T1", "Вечный Рим", "rome", "средиземноморский", {4, 5, 9, 10}, 7, 650.0, 20),
    ("T2", "Пляжи Антальи", "antalya", "субтропический", {5, 6, 7, 8, 9}, 10, 480.0, 30),
    ("T3", "Гастрономический Тбилиси", "tbilisi", "умеренный", {4, 5, 6, 9, 10}, 5, 390.0, 15),
)
SEASONS = (("Высокий сезон", 6, 8, 1.3), ("Низкий сезон", 11, 2, 0.85))
ATTRACTIONS = {"rome": ("Колизей", "история", 18.0, 9, 19)}
HOTEL = {"street": "Набережная", "building": "1", "postal": "000001", "stars": 4, "check_in_hour": 14,
         "rooms": 5, "capacity": 4, "night_price": 60.0, "meal": ("BB", 10.0, 1)}
FLIGHT = {"airline": ("Belavia", "B2", 20.0, 8.0), "destination": "antalya", "number": "B2-711",
          "days_ahead": 30, "departure": time(hour=9), "duration_hours": 3, "price": 150.0, "seats": 6}
# (номер, имя, фамилия, номер карты, нужна ли шенгенская виза)
CLIENTS = (("C1", "Анна", "Иванова", "4111111111111111", True), ("C2", "Пётр", "Смирнов", "5500000000000004", False))
CLIENT_DEFAULTS = {"birth_date": date(1995, 5, 17), "phone": "+375291234567", "cvv": "123", "balance": 10000.0,
                   "document_years": 10, "visa_years": 2, "visa_entries": 2}
DAYS_IN_YEAR = 365
FLIGHT_DAYS_AHEAD = FLIGHT["days_ahead"]


def _create_cities() -> dict[str, City]:
    countries = {}
    for key, (name, iso_code, currency, visa_free) in COUNTRIES.items():
        countries[key] = Country(name, iso_code, currency)
        for partner in visa_free:
            countries[key].add_visa_free_country(partner)
    return {key: City(name, countries[country], utc, lat, lon) for key, (name, country, utc, lat, lon) in CITIES.items()}


def _create_tour(row: tuple, cities: dict[str, City]) -> Tour:
    tour_id, name, city_key, climate, best_months, days, price, places = row
    destination = Destination(cities[city_key], climate, best_months)
    if city_key in ATTRACTIONS:
        title, category, fee, opens, closes = ATTRACTIONS[city_key]
        destination.add_attraction(Attraction(title, cities[city_key], category, fee, opens, closes))
    tour = Tour(tour_id, name, destination, days, price, places)
    for season in SEASONS:
        tour.add_season(Season(*season))
    return tour


def _create_hotel(city: City) -> Hotel:
    address = Address(HOTEL["street"], HOTEL["building"], HOTEL["postal"], city)
    hotel = Hotel(f"Отель «{city.name}»", address, HOTEL["stars"], HOTEL["check_in_hour"])
    standard = RoomType("Стандарт", 1.0, False)
    for room_number in range(1, HOTEL["rooms"] + 1):
        hotel.add_room(Room(str(room_number), standard, HOTEL["capacity"], HOTEL["night_price"]))
    hotel.add_meal_plan(MealPlan(*HOTEL["meal"]))
    return hotel


def _create_flight(origin: City, destination: City) -> Flight:
    departure = datetime.combine(date.today() + timedelta(days=FLIGHT["days_ahead"]), FLIGHT["departure"])
    arrival = departure + timedelta(hours=FLIGHT["duration_hours"])
    route = (Airport(origin.name, "MSQ", origin, {"1"}), Airport(destination.name, "AYT", destination, {"1"}))
    flight = Flight(FLIGHT["number"], Airline(*FLIGHT["airline"]), route, (departure, arrival), FLIGHT["price"])
    for seat_number in range(1, FLIGHT["seats"] + 1):
        flight.add_seat(Seat(f"{seat_number}A", "economy", 1.0))
    return flight


def _create_client(row: tuple, home: Country, visa_country: Country) -> Client:
    client_id, first_name, last_name, card_number, needs_visa = row
    defaults = CLIENT_DEFAULTS
    email = f"{client_id.lower()}@mail.by"
    client = Client(client_id, first_name, last_name, defaults["birth_date"], defaults["phone"], email)
    today = date.today()
    valid_until = today + timedelta(days=DAYS_IN_YEAR * defaults["document_years"])
    client.passport = Passport(f"MP{client_id}", home, today, valid_until)
    client.bank_card = BankCard(card_number, client.full_name, valid_until, defaults["cvv"], defaults["balance"])
    client.loyalty_card = LoyaltyCard(f"L-{client_id}")
    if needs_visa:
        visa_until = today + timedelta(days=DAYS_IN_YEAR * defaults["visa_years"])
        client.add_visa(Visa("Шенген C", visa_country, today, visa_until, defaults["visa_entries"]))
    return client


def build_demo_company() -> TravelCompany:
    cities = _create_cities()
    home_city = cities[COMPANY["home_city"]]
    service = BookingService(PaymentProcessor(), NotificationService())
    company = TravelCompany(COMPANY["name"], COMPANY["license"], service, home_city.country)
    branch_address = Address(BRANCH["street"], BRANCH["building"], BRANCH["postal"], home_city)
    company.open_branch(Branch(BRANCH["name"], branch_address, *BRANCH["hours"]))
    for row in TOURS:
        tour = _create_tour(row, cities)
        company.add_tour(tour)
        company.add_partner_hotel(_create_hotel(tour.destination.city))
    company.add_flight(_create_flight(home_city, cities[FLIGHT["destination"]]))
    for row in CLIENTS:
        company.register_client(_create_client(row, home_city.country, cities["rome"].country))
    return company
