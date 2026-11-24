// booking.js — список помещений и отправка формы заявки
const bookingForm = document.querySelector("#bookingForm");
const roomSelect = document.querySelector("#room_id");
async function loadRoomOptions() {
    const rooms = await getJson("/api/rooms");
    roomSelect.innerHTML = '<option value="">— выберите помещение —</option>' + rooms
        .map((room) => `<option value="${room.id}">${escapeHtml(room.name)} (${escapeHtml(room.room_type)})</option>`).join("");
}
if (roomSelect) loadRoomOptions();
bookingForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = await sendForm(bookingForm);
    if (data.ok) { showMessageAfterRedirect(data.message); window.location.href = data.redirect; }
    else { showFieldErrors(bookingForm, data.errors); }
});