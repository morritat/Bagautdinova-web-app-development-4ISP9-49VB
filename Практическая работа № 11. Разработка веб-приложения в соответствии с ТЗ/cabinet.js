// cabinet.js — заявки пользователя, удаление, отзыв
const STATUS_CLASS = { "Новая": "new", "Мероприятие назначено": "planned", "Завершено": "done" };
const list = document.querySelector("#bookingList");
function bookingCard(b) {
    let actions = "";
    if (b.status === "Новая") {
        actions += `<form class="booking-card__form" method="post" action="/booking/${b.id}/delete">
            <button class="btn btn-outline-danger btn-sm button" type="submit">Удалить заявку</button></form>`;
    }
    if (b.review_text) {
        actions += `<p class="booking-card__review"><b>Ваш отзыв:</b> ${escapeHtml(b.review_text)}</p>`;
    } else if (b.status === "Завершено") {
        actions += `<form class="booking-card__form" method="post" action="/booking/${b.id}/review">
            <label class="form-label" for="review${b.id}">Отзыв о мероприятии</label>
            <textarea class="form-control" id="review${b.id}" name="text" rows="3" required></textarea>
            <button class="btn btn-primary btn-sm button" type="submit">Оставить отзыв</button></form>`;
    }
    return `<div class="col-12 col-md-6"><article class="card booking-card"><div class="card-body">
        <h2 class="booking-card__title">Заявка №${b.id}</h2>
        <p class="booking-card__row"><b>Помещение:</b> ${escapeHtml(b.room_name)}</p>
        <p class="booking-card__row"><b>Дата начала:</b> ${b.start_date_text}</p>
        <p class="booking-card__row"><b>Оплата:</b> ${escapeHtml(b.payment_method)}</p>
        <span class="status status--${STATUS_CLASS[b.status]}">${b.status}</span>${actions}
    </div></article></div>`;
}
async function loadBookings() {
    const bookings = await getJson("/api/bookings");
    document.querySelector("#emptyText").hidden = bookings.length > 0;
    list.innerHTML = bookings.map(bookingCard).join("");
}
list.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = await sendForm(event.target);
    if (data.ok) { showMessage(data.message); loadBookings(); }
    else { showMessage(Object.values(data.errors).join(" "), "danger"); }
});
currentUser.then((user) => {
    if (user) document.querySelector("#hello").textContent = `Здравствуйте, ${user.full_name}!`;
});
loadBookings();