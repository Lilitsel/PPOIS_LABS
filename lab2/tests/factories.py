"""Фабрики тестовых объектов с фиксированными датами."""
from datetime import date, datetime, timedelta

from travel_agency.accommodation.hotel import Hotel, MealPlan, Room, RoomType
from travel_agency.booking.service import BookingService
from travel_agency.documents.identity import Passport
from travel_agency.finance.cards import BankCard, PaymentProcessor
from travel_agency.geography.places import Address, City, Country, Destination
from travel_agency.people.person import Client, Person
from travel_agency.service.notifications import NotificationService
from travel_agency.tours.pricing import TourPackage
from travel_agency.tours.tour import Tour
from travel_agency.transport.air import Airline, Airport, Flight, Seat

TODAY = date(2026, 3, 1)
START = date(2026, 4, 10)
CARD_NUMBER = "4111111111111111"
CVV = "123"


def make_country(name="Беларусь", iso="BY"):
    return Country(name, iso, "BYN")


def make_city(name="Минск", country=None, lat=53.9, lon=27.56):
    return City(name, country or make_country(), 3, lat, lon)


def make_person():
    return Person("Иван", "Петров", date(1990, 6, 15), "+375290000000", "ivan@mail.by")


def make_client(client_id="C1", home=None):
    client = Client(client_id, "Анна", "Иванова", date(1995, 5, 17), "+375291111111", "anna@mail.by")
    client.passport = Passport("MP1", home or make_country(), date(2020, 1, 1), date(2030, 1, 1))
    client.bank_card = make_card()
    return client


def make_card(balance=10000.0, expiry=date(2030, 1, 1)):
    return BankCard(CARD_NUMBER, "ANNA IVANOVA", expiry, CVV, balance)


def make_hotel(city, rooms=2, capacity=2):
    hotel = Hotel("Sunrise", Address("Main", "1", "07000", city), 4, 14)
    standard = RoomType("Стандарт", 1.0, False)
    for index in range(1, rooms + 1):
        hotel.add_room(Room(str(index), standard, capacity, 50.0))
    hotel.add_meal_plan(MealPlan("BB", 10.0, 1))
    return hotel


def make_tour(city=None, tour_id="T1", max_group=10, duration=7):
    destination = Destination(city or make_city("Анталья", make_country("Турция", "TR")), "субтропики", {5, 6})
    return Tour(tour_id, "Море", destination, duration, 400.0, max_group)


def make_flight(origin_city, destination_city, departure=datetime(2026, 4, 10, 9, 0), seats=2):
    airline = Airline("Belavia", "B2", 20.0, 5.0)
    route = (Airport("MSQ", "MSQ", origin_city, {"1"}), Airport("AYT", "AYT", destination_city, {"1", "2"}))
    flight = Flight("B2-101", airline, route, (departure, departure + timedelta(hours=3)), 150.0)
    for index in range(1, seats + 1):
        flight.add_seat(Seat(f"{index}A", "economy", 1.0))
    flight.add_seat(Seat("1F", "business", 2.0))
    return flight


def make_package(tour=None, client=None, travelers=1):
    tour = tour or make_tour()
    package = TourPackage(tour, START, travelers)
    hotel = make_hotel(tour.destination.city)
    package.hotel_reservation = hotel.reserve_room(client or make_client(), travelers, START, package.end_date)
    return package


def make_service():
    return BookingService(PaymentProcessor(), NotificationService())
