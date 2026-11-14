# Лабораторная работа №2. Крупный ООП-проект «Туристическая компания»

Объектная модель туристической компании на Python: туры и направления, клиенты и их документы,
отели и авиаперелёты, бронирование с оплатой картой, отмены со штрафами, бонусная программа, отчёты.

## Итоговая статистика

| Показатель | Требование | В проекте |
|---|---|---|
| Классы предметной области | ≥ 50 | 58 |
| Поля (суммарно) | ≥ 150 | 280 |
| Методы (суммарно) | — | 207 |
| Содержательные поведения (публичные методы, без свойств) | ≥ 100 | 191 |
| Ассоциации между классами | ≥ 30 | 123 |
| Собственные исключения | ≥ 12 | 20 |

Формат строки таблиц: `Класс | число полей: поля | число методов: методы | связанные классы`.
Запись `GroupTour ← Tour` означает наследование. Ассоциация — класс используется как поле или параметр метода.

## Структура

```
lab2/
├── travel_agency/          # предметная область
│   ├── people/             # Person, Client, сотрудники
│   ├── documents/          # паспорта, визы, страховки, договоры, билеты
│   ├── geography/          # страны, города, адреса, достопримечательности
│   ├── accommodation/      # отели, номера, питание, бронь проживания
│   ├── transport/          # авиарейсы, места, автобусы, трансферы
│   ├── tours/              # туры, сезоны, программа, экскурсии, скидки, пакеты
│   ├── booking/            # бронирование, отмена, лист ожидания, сервис
│   ├── finance/            # карты, платежи, возвраты, счета, отчёты
│   ├── service/            # лояльность, отзывы, жалобы, уведомления
│   ├── company/            # компания и филиалы
│   ├── cli/                # консольный интерфейс и демо-данные (отделены от логики)
│   ├── constants.py        # все числовые параметры бизнес-логики
│   ├── statuses.py         # перечисления состояний
│   └── exceptions/         # собственные исключения, по одному в файле
├── tests/                  # модульные тесты
├── run_cli.py              # точка входа для сборки исполняемого файла
├── setup.cfg               # настройки flake8, pytest, coverage
└── requirements-dev.txt    # зависимости для разработки
```

## Запуск

Требуется Python 3.10+. Внешних зависимостей у приложения нет.

```bash
cd lab2
python -m travel_agency                         # запуск CLI
pip install -r requirements-dev.txt             # инструменты разработки
pytest --cov --cov-report=term-missing          # тесты и покрытие
flake8 travel_agency tests run_cli.py           # статический анализ
```

Готовые сборки лежат в разделе **Releases**: `travel_agency-Windows.exe`, `travel_agency-Linux`
и `travel_agency.pyz` (запуск: `python travel_agency.pyz`).

## CLI

Меню позволяет посмотреть и подобрать туры, зарегистрировать клиента, забронировать тур, оплатить и отменить
бронирование, посмотреть брони и уведомления клиента, сформировать отчёт о продажах. Демо-клиенты:
`C1` (есть шенгенская виза) и `C2` (без визы), CVV демо-карт — `123`. Тур `T2` (Анталья) имеет рейс
через 30 дней от текущей даты.

## Классы

### Люди и персонал (`travel_agency/people`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Person` | 5: first_name, last_name, birth_date, phone, email | 3: full_name(), calculate_age(), is_adult() | — |
| `Client ← Person` | 6: client_id, passport, visas, loyalty_card, bank_card, bookings | 5: add_visa(), add_booking(), get_active_bookings(), check_travel_documents(), can_travel_to() | Passport, Visa, LoyaltyCard, BankCard, Booking, Country |
| `Employee ← Person` | 5: employee_id, position, salary, hire_date, branch | 2: calculate_experience_years(), calculate_bonus() | Person, Branch |
| `TravelAgent ← Employee` | 3: commission_percent, assigned_clients, sold_bookings | 3: assign_client(), sell_tour(), calculate_commission() | Client, Booking |
| `Guide ← Employee` | 4: languages, rating, ratings_count, excursions | 3: speaks_language(), assign_to_excursion(), update_rating() | Excursion |
| `Manager ← Employee` | 2: approval_limit, subordinates | 4: add_subordinate(), approve_discount(), approve_refund(), review_complaint() | Employee, Discount, Refund, Complaint |
| `Accountant ← Employee` | 2: issued_invoices, processed_refunds | 3: issue_invoice(), process_refund(), generate_sales_report() | Booking, Invoice, Refund, SalesReport |
| `Driver ← Employee` | 2: license_categories, transfers | 2: can_drive(), assign_transfer() | Bus, Transfer |

### Документы (`travel_agency/documents`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Passport` | 4: number, issuing_country, issue_date, expiry_date | 3: is_valid_on(), months_until_expiry(), is_valid_for_trip() | Country |
| `Visa` | 6: visa_type, country, valid_from, valid_to, entries_allowed, entries_used | 4: covers_date(), has_entries_left(), allows_stay_in(), register_entry() | Country |
| `InsurancePolicy` | 6: policy_number, insured_person, start_date, end_date, coverage_amount, claims | 4: calculate_premium(), covers_date(), remaining_coverage(), file_claim() | Person |
| `Contract` | 6: contract_number, client, booking, terms, sign_date, is_terminated | 4: is_signed(), sign(), calculate_penalty(), terminate() | Client, Booking, CancellationPolicy |
| `Voucher` | 5: code, booking, issue_date, valid_days, is_used | 2: is_expired(), redeem() | Booking |
| `Ticket` | 6: ticket_number, passenger, flight, seat, price, status | 3: check_in(), cancel(), change_seat() | Person, Flight, Seat |

### География (`travel_agency/geography`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Country` | 5: name, iso_code, currency, safety_level, visa_free_for | 3: add_visa_free_country(), requires_visa_for(), is_safe_for_travel() | Passport |
| `City` | 5: name, country, utc_offset_hours, latitude, longitude | 2: local_time(), distance_to() | Country |
| `Address` | 4: street, building, postal_code, city | 1: format_full() | City |
| `Attraction` | 6: name, city, category, entrance_fee, opening_hour, closing_hour | 2: is_open_at(), calculate_group_fee() | City |
| `Destination` | 4: city, climate, best_months, attractions | 4: country(), is_recommended_in_month(), add_attraction(), find_attractions_by_category() | City, Attraction, Country |

### Проживание (`travel_agency/accommodation`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `RoomType` | 3: name, price_multiplier, has_balcony | 1: apply_multiplier() | — |
| `MealPlan` | 3: code, daily_cost_per_person, meals_per_day | 1: calculate_cost() | — |
| `Room` | 5: number, room_type, capacity, base_price_per_night, is_available | 3: price_per_night(), calculate_stay_cost(), can_accommodate() | RoomType |
| `Hotel` | 6: name, address, stars, check_in_hour, rooms, meal_plans | 6: add_room(), add_meal_plan(), find_available_room(), reserve_room(), release_room(), count_free_rooms() | Address, Room, MealPlan, Client, HotelReservation |
| `HotelReservation` | 8: hotel, room, client, guests, check_in, check_out, meal_plan, is_cancelled | 4: calculate_nights(), choose_meal_plan(), calculate_total(), cancel() | Hotel, Room, Client, MealPlan |

### Транспорт (`travel_agency/transport`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Airline` | 4: name, iata_code, baggage_allowance_kg, fee_per_extra_kg | 1: calculate_baggage_fee() | — |
| `Airport` | 4: name, iata_code, city, terminals | 1: has_terminal() | City |
| `Seat` | 4: number, seat_class, price_multiplier, is_occupied | 2: occupy(), release() | — |
| `Flight` | 9: flight_number, airline, departure_airport, arrival_airport, departure_time, arrival_time, base_price, seats, issued_tickets | 7: add_seat(), calculate_duration(), find_free_seat(), book_seat(), calculate_seat_price(), issue_ticket(), flies_to() | Airline, Airport, Seat, Ticket, Person, City |
| `Bus` | 5: plate_number, capacity, required_license, has_air_conditioning, mileage_km | 2: can_carry(), register_trip() | — |
| `Transfer` | 8: from_address, to_address, pickup_time, bus, distance_km, driver, passengers, is_completed | 4: add_passenger(), calculate_cost(), estimate_arrival(), complete() | Address, Bus, Driver, Client |

### Туры и ценообразование (`travel_agency/tours`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Discount` | 5: name, percent, valid_until, min_order_amount, is_approved | 2: is_applicable(), apply() | — |
| `PromoCode` | 4: code, discount, usage_limit, times_used | 2: is_exhausted(), redeem() | Discount |
| `TourPackage` | 8: tour, start_date, travelers_count, hotel_reservation, flight, transfer, insurances, discount | 6: end_date(), destination_country(), apply_discount(), validate_completeness(), _components_cost(), calculate_total_price() | Tour, HotelReservation, Flight, Transfer, InsurancePolicy, Discount, Country |
| `Season` | 4: name, start_month, end_month, price_coefficient | 2: contains_date(), adjust_price() | — |
| `Excursion` | 8: name, attraction, language, duration_hours, price_per_person, max_participants, guide, participants | 3: is_full(), register_participant(), calculate_revenue() | Attraction, Guide, Client |
| `ItineraryDay` | 4: day_number, city, free_time_hours, excursions | 2: calculate_busy_hours(), add_excursion() | City, Excursion |
| `Itinerary` | 2: days, total_distance_km | 3: add_day(), remove_last_day(), count_activities() | ItineraryDay |
| `Tour` | 10: tour_id, name, destination, duration_days, base_price, max_group_size, itinerary, seasons, reviews, booked_places | 11: destination_name(), add_season(), season_coefficient(), is_available_in_season(), calculate_price_for_group(), free_places(), has_free_places(), reserve_places(), release_places(), add_review(), average_rating() | Destination, Itinerary, Season, Review |
| `GroupTour ← Tour` | 2: group_leader, min_participants | 2: is_confirmed(), calculate_price_for_group() | Tour, Guide |

### Бронирование (`travel_agency/booking`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Booking` | 7: booking_id, client, package, created_at, travelers, status, total_price | 9: departure_date(), destination_name(), is_active(), _require_status(), add_traveler(), calculate_total(), confirm(), cancel(), complete() | Client, TourPackage, Person, Cancellation |
| `Cancellation` | 5: booking, reason, cancel_date, policy, penalty_amount | 3: days_before_departure(), calculate_penalty(), calculate_refund_amount() | Booking, CancellationPolicy |
| `Waitlist` | 3: tour, max_size, queue | 3: enqueue(), position_of(), promote_next() | Tour, Client |
| `CancellationPolicy` | 1: rules | 2: penalty_percent_for(), calculate_penalty() | — |
| `BookingService` | 4: processor, notifier, bookings, payments | 6: create_booking(), find_booking(), find_by_client(), pay_booking(), cancel_booking(), _reward_loyalty() | PaymentProcessor, NotificationService, Booking, Payment, BankCard, Client, TourPackage |

### Финансы (`travel_agency/finance`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `BankCard` | 5: masked_number, holder_name, expiry_date, cvv_hash, balance | 5: _validate_amount(), is_expired(), verify_cvv(), withdraw(), deposit() | — |
| `Payment` | 8: payment_id, amount, currency, card, booking, created_at, status, refunded_amount | 2: process(), refund() | BankCard, Booking |
| `PaymentProcessor` | 2: commission_percent, transaction_log | 5: _next_payment_id(), calculate_commission(), charge(), transfer(), rollback() | Payment, BankCard, Booking |
| `Refund` | 5: payment, amount, reason, status, approved_by | 4: _require_pending(), approve(), reject(), execute() | Payment, Manager |
| `Invoice` | 6: invoice_number, booking, issue_date, due_date, vat_percent, items | 5: add_item(), calculate_subtotal(), calculate_vat(), calculate_total(), is_overdue() | Booking |
| `CurrencyConverter` | 3: base_currency, rates, last_updated | 3: update_rate(), _rate_of(), convert() | — |
| `SalesReport` | 4: COUNTED_STATUSES, period_start, period_end, bookings | 4: _is_counted(), calculate_revenue(), average_check(), top_destinations() | Booking |

### Клиентский сервис (`travel_agency/service`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `LoyaltyCard` | 4: card_number, points, lifetime_points, tier | 3: add_points(), redeem_points(), upgrade_tier() | — |
| `Review` | 5: author, tour, rating, text, created_at | 3: contains_forbidden_words(), validate(), is_positive() | Client, Tour |
| `Complaint` | 6: client, booking, description, status, escalation_level, resolution | 2: escalate(), resolve() | Client, Booking |
| `Notification` | 4: recipient, message, channel, sent_at | 2: mark_as_sent(), is_sent() | Client |
| `NotificationService` | 2: default_channel, sent_notifications | 6: send(), notify_booking_confirmed(), notify_booking_cancelled(), notify_departure_reminder(), send_bulk(), history_for() | Notification, Client, Booking |

### Компания (`travel_agency/company`)

| Класс | Поля | Методы | Ассоциации |
|---|---|---|---|
| `Branch` | 5: name, address, opening_hour, closing_hour, employees | 4: hire_employee(), fire_employee(), is_open_at(), calculate_payroll() | Address, Employee |
| `TravelCompany` | 9: name, home_country, license_number, booking_service, branches, tours, clients, hotels, flights | 14: open_branch(), add_partner_hotel(), add_flight(), register_client(), find_client(), add_tour(), find_tour(), search_tours(), _matches(), find_hotel_in_city(), find_flight_to(), assemble_package(), book_tour(), all_bookings() | BookingService, Country, Branch, Tour, Client, Hotel, Flight, City, TourPackage, Booking |

### Перечисления (`travel_agency/statuses.py`)

`BookingStatus`, `PaymentStatus`, `RefundStatus`, `TicketStatus`, `ComplaintStatus` — допустимые состояния объектов.

## Exceptions (`travel_agency/exceptions/`, one per file)

| Exception | When Raised |
|---|---|
| `TravelAgencyException` | Base class for all domain exceptions |
| `InvalidClientDataException` | Empty name, invalid email, duplicate registration, invalid review |
| `InvalidDateRangeException` | End date is earlier than start date |
| `PassportExpiredException` | Passport expires less than 6 months after the trip |
| `VisaRequiredException` | No valid visa or no entries remaining |
| `RoomNotAvailableException` | No available room or partner hotel in the city |
| `SeatNotAvailableException` | Airplane seat is occupied or does not exist |
| `TourFullyBookedException` | No places left in the tour |
| `CapacityExceededException` | Excursion, transfer, package, or waitlist is full |
| `BookingNotFoundException` | Booking with the specified ID was not found |
| `InvalidBookingStateException` | Operation is invalid in the current state (duplicate payment, cancellation, etc.) |
| `InsufficientFundsException` | Insufficient funds on the card or bonus points |
| `CardExpiredException` | Bank card has expired |
| `InvalidPaymentDataException` | Invalid card number, amount, or currency |
| `InvalidPromoCodeException` | Promo code is exhausted or discount is invalid |
| `RefundNotAllowedException` | Refund is not allowed or exceeds the manager's approval limit |
| `InvalidTourDataException` | Invalid parameters for a tour, itinerary, or package |
| `StaffNotQualifiedException` | Employee lacks required language, driver'''s license category, or authority |
| `EmployeeNotFoundException` | Employee was not found in the branch |
| `InsuranceClaimRejectedException` | Insurance claim is outside the coverage period or exceeds the coverage amount |

## Документация

HTML-документация по коду лежит в папке `docs/`: откройте `docs/index.html` в браузере.
Она сгенерирована инструментом pdoc из описаний классов и методов в коде. Пересоздать после изменений:

```bash
pip install pdoc==14.7.0
pdoc travel_agency -o docs
```
