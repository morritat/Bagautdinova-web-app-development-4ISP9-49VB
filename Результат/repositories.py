"""Классы-репозитории: каждый отвечает за одну таблицу (ООП)."""
from werkzeug.security import check_password_hash, generate_password_hash

class UserRepository:
    """Пользователи: регистрация и вход."""
    def __init__(self, db): self.db = db
    def login_exists(self, login):
        return self.db.fetch_one("SELECT id FROM users WHERE login = ?", (login,)) is not None
    def create(self, login, password, full_name, phone, email, role="user"):
        # Пароль храним только в виде хеша
        self.db.execute(
            "INSERT INTO users (login, password_hash, full_name, phone, email, role) VALUES (?, ?, ?, ?, ?, ?)",
            (login, generate_password_hash(password), full_name, phone, email, role))
    def authenticate(self, login, password):
        user = self.db.fetch_one("SELECT * FROM users WHERE login = ?", (login,))
        if user and check_password_hash(user["password_hash"], password):
            return user
        return None

class RoomRepository:
    """Помещения для конференций."""
    def __init__(self, db): self.db = db
    def all(self):
        return self.db.fetch_all("SELECT * FROM rooms ORDER BY room_type, name")
    def get(self, room_id):
        return self.db.fetch_one("SELECT * FROM rooms WHERE id = ?", (room_id,))
    def find_by_name(self, name):
        return self.db.fetch_one("SELECT * FROM rooms WHERE LOWER(name) = LOWER(?)", (name,))

class BookingRepository:
    """Заявки: создание, чтение, изменение, удаление (CRUD)."""
    STATUSES = ("Новая", "Мероприятие назначено", "Завершено")
    PAYMENT_METHODS = ("При очном посещении", "Перевод по СБП")
    def __init__(self, db): self.db = db
    def create(self, user_id, room_id, start_date, payment_method):
        self.db.execute(
            "INSERT INTO bookings (user_id, room_id, start_date, payment_method) VALUES (?, ?, ?, ?)",
            (user_id, room_id, start_date, payment_method))
    def get(self, booking_id):
        return self.db.fetch_one("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    def for_user(self, user_id):
        return self.db.fetch_all(
            "SELECT b.id, b.status, b.payment_method, "
            "strftime('%d.%m.%Y', b.start_date) AS start_date_text, "
            "r.name AS room_name, rv.text AS review_text "
            "FROM bookings b JOIN rooms r ON r.id = b.room_id "
            "LEFT JOIN reviews rv ON rv.booking_id = b.id "
            "WHERE b.user_id = ? ORDER BY b.created_at DESC", (user_id,))
    def all(self, status=None):
        sql = ("SELECT b.id, b.status, b.payment_method, "
               "strftime('%d.%m.%Y', b.start_date) AS start_date_text, "
               "r.name AS room_name, u.full_name, u.phone, u.email "
               "FROM bookings b JOIN rooms r ON r.id = b.room_id JOIN users u ON u.id = b.user_id ")
        params = ()
        if status:
            sql += "WHERE b.status = ? "
            params = (status,)
        return self.db.fetch_all(sql + "ORDER BY b.created_at DESC", params)
    def update_status(self, booking_id, status):
        if status not in self.STATUSES:
            raise ValueError("Недопустимый статус")
        self.db.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
    def delete(self, booking_id):
        self.db.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))

class ReviewRepository:
    """Отзывы о завершённых мероприятиях."""
    def __init__(self, db): self.db = db
    def create(self, booking_id, text):
        self.db.execute("INSERT INTO reviews (booking_id, text) VALUES (?, ?)", (booking_id, text))