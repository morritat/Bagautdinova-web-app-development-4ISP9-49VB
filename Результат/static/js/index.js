// index.js — карточки помещений из базы
async function loadRooms() {
    const rooms = await getJson("/api/rooms");
    document.querySelector("#roomList").innerHTML = rooms.map((room) => `
        <div class="col-12 col-md-6 col-lg-3">
            <article class="card room-card"><div class="card-body">
                <h3 class="room-card__title">${escapeHtml(room.name)}</h3>
                <p class="room-card__type">${escapeHtml(room.room_type)}</p>
            </div></article>
        </div>`).join("");
}
loadRooms();