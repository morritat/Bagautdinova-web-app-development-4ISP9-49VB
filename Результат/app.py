"""Портал «Конференции.РФ» — маршруты Flask."""
from functools import wraps
from flask import Flask, jsonify, redirect, request, send_from_directory, session
import config
from db import Database, init_db
from repositories import BookingRepository, ReviewRepository, RoomRepository, UserRepository
from validators import RegistrationValidator, is_future_or_today, parse_date

app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.json.ensure_ascii = False

db = Database(config.DATABASE)
users, rooms = UserRepository(db), RoomRepository(db)
bookings, reviews = BookingRepository(db), ReviewRepository(db)

def page(name):
    """Отдать HTML-файл из папки pages."""
    return send_from_directory("pages", name)

def is_fetch():
    return request.headers.get("X-Requested-With") == "fetch"

def ok(message="", redirect_to=None):
    if redirect_to and not is_fetch():
        return redirect(redirect_to)
    return jsonify({"ok": True, "message": message, "redirect": redirect_to})

def fail(errors, status=200):
    return jsonify({"ok": False, "errors": errors}), status

def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if request.method == "GET" and not request.path.startswith("/api/"):
                return redirect("/login")
            return fail({"common": "Сначала войдите в систему"}, 401)
        return view(*args, **kwargs)
    return wrapper

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            if request.method == "GET" and not request.path.startswith("/api/"):
                return redirect("/login")
            return fail({"common": "Доступ только для администратора"}, 403)
        return view(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return page("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return page("register.html")
    validator = RegistrationValidator(request.form)
    if not validator.validate():
        return fail(validator.errors)
    login_value = request.form["login"].strip()
    if users.login_exists(login_value):
        return fail({"login": "Такой логин уже занят"})
    users.create(login_value, request.form["password"], request.form["full_name"].strip(),
                 request.form["phone"].strip(), request.form["email"].strip())
    return ok("Пользователь создан. Теперь войдите в систему.", "/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return page("login.html")
    login_value = request.form.get("login", "").strip()
    password = request.form.get("password", "")
    errors = {}
    if not login_value: errors["login"] = "Введите логин"
    if not password: errors["password"] = "Введите пароль"
    if errors: return fail(errors)
    user = users.authenticate(login_value, password)
    if user is None:
        return fail({"common": "Неверный логин или пароль"})
    session["user_id"], session["role"], session["full_name"] = user["id"], user["role"], user["full_name"]
    return ok("", "/admin" if user["role"] == "admin" else "/cabinet")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/cabinet")
@login_required
def cabinet():
    return page("cabinet.html")

@app.route("/booking/new", methods=["GET", "POST"])
@login_required
def booking_new():
    if request.method == "GET":
        return page("booking_new.html")
    form, errors = request.form, {}
    room_id = form.get("room_id", "")
    room = rooms.get(int(room_id)) if room_id.isdigit() else rooms.find_by_name(form.get("room_name", "").strip())
    if room is None:
        errors["room"] = "Помещение не найдено: выберите его из списка"
    start_date = parse_date(form.get("start_date", ""))
    if start_date is None:
        errors["start_date"] = "Укажите дату в формате ДД.ММ.ГГГГ"
    elif not is_future_or_today(start_date):
        errors["start_date"] = "Дата не может быть в прошлом"
    payment = form.get("payment_method", "")
    if payment not in BookingRepository.PAYMENT_METHODS:
        errors["payment_method"] = "Выберите способ оплаты"
    if errors: return fail(errors)
    bookings.create(session["user_id"], room["id"], start_date.isoformat(), payment)
    return ok("Заявка отправлена администратору", "/cabinet")

@app.route("/booking/<int:booking_id>/delete", methods=["POST"])
@login_required
def booking_delete(booking_id):
    booking = bookings.get(booking_id)
    if not booking or booking["user_id"] != session["user_id"]:
        return fail({"common": "Заявка не найдена"}, 404)
    if booking["status"] != "Новая":
        return fail({"common": "Удалить можно только новую заявку"})
    bookings.delete(booking_id)
    return ok("Заявка удалена", "/cabinet")

@app.route("/booking/<int:booking_id>/review", methods=["POST"])
@login_required
def booking_review(booking_id):
    booking = bookings.get(booking_id)
    text = request.form.get("text", "").strip()
    if not booking or booking["user_id"] != session["user_id"]:
        return fail({"common": "Заявка не найдена"}, 404)
    if booking["status"] != "Завершено":
        return fail({"common": "Отзыв можно оставить только после завершения мероприятия"})
    if not text:
        return fail({"text": "Напишите текст отзыва"})
    reviews.create(booking_id, text)
    return ok("Спасибо за отзыв!", "/cabinet")

@app.route("/admin")
@admin_required
def admin():
    return page("admin.html")

@app.route("/admin/booking/<int:booking_id>/status", methods=["POST"])
@admin_required
def admin_change_status(booking_id):
    try:
        bookings.update_status(booking_id, request.form.get("status", ""))
    except ValueError:
        return fail({"common": "Недопустимый статус"})
    return ok(f"Статус заявки №{booking_id} изменён", "/admin")

@app.route("/admin/booking/<int:booking_id>/delete", methods=["POST"])
@admin_required
def admin_delete(booking_id):
    bookings.delete(booking_id)
    return ok(f"Заявка №{booking_id} удалена", "/admin")

@app.route("/api/me")
def api_me():
    if "user_id" not in session:
        return jsonify({"user": None})
    return jsonify({"user": {"full_name": session["full_name"], "role": session["role"]}})

@app.route("/api/rooms")
def api_rooms():
    return jsonify(rooms.all())

@app.route("/api/bookings")
@login_required
def api_bookings():
    return jsonify(bookings.for_user(session["user_id"]))

@app.route("/api/admin/bookings")
@admin_required
def api_admin_bookings():
    status = request.args.get("status", "")
    return jsonify({"statuses": BookingRepository.STATUSES, "bookings": bookings.all(status or None)})

if __name__ == "__main__":
    init_db(config.DATABASE)
    app.run(debug=True)