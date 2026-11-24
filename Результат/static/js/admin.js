// admin.js — все заявки, фильтр, смена статуса, удаление
const STATUS_CLASS = { "Новая": "new", "Мероприятие назначено": "planned", "Завершено": "done" };
const filter = document.querySelector("#statusFilter");
const list = document.querySelector("#bookingList");
function statusOptions(statuses, current) {
    return statuses.map((s) => `<option value="${s}" ${s === current ? "selected" : ""}>${s}</option>`).join("");
}
function bookingCard(b, statuses) {
    return `<div class="col-12 col-md-6 col-xl-4"><article class="card booking-card"><div class="card-body">
        <h2 class="booking-card__title">Заявка №${b.id}</h2>
        <span class="status status--${STATUS_CLASS[b.status]}">${b.status}</span>
        <p class="booking-card__row"><b>Клиент:</b> ${escapeHtml(b.full_name)}</p>
        <p class="booking-card__row"><b>Телефон:</b> ${escapeHtml(b.phone)}</p>
        <p class="booking-card__row"><b>Почта:</b> ${escapeHtml(b.email)}</p>
        <p class="booking-card__row"><b>Помещение:</b> ${escapeHtml(b.room_name)}</p>
        <p class="booking-card__row"><b>Дата начала:</b> ${b.start_date_text}</p>
        <p class="booking-card__row"><b>Оплата:</b> ${escapeHtml(b.payment_method)}</p>
        <form class="booking-card__form" method="post" action="/admin/booking/${b.id}/status">
            <select class="form-select form-select-sm" name="status">${statusOptions(statuses, b.status)}</select>
            <button class="btn btn-primary btn-sm button" type="submit">Сохранить статус</button></form>
        <form class="booking-card__form" method="post" action="/admin/booking/${b.id}/delete">
            <button class="btn btn-outline-danger btn-sm button" type="submit">Удалить</button></form>
    </div></article></div>`;
}
async function loadBookings() {
    const data = await getJson("/api/admin/bookings?status=" + encodeURIComponent(filter.value));
    if (filter.options.length === 1) filter.innerHTML += statusOptions(data.statuses, "");
    document.querySelector("#emptyText").hidden = data.bookings.length > 0;
    list.innerHTML = data.bookings.map((b) => bookingCard(b, data.statuses)).join("");
}
document.querySelector("#filterForm").addEventListener("submit", (event) => {
    event.preventDefault();
    loadBookings();
});
list.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = await sendForm(event.target);
    if (data.ok) { showMessage(data.message); loadBookings(); }
    else { showMessage(Object.values(data.errors).join(" "), "danger"); }
});
loadBookings();