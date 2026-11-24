// common.js — общие функции всех страниц, подключается ПЕРЕД скриптом страницы
function escapeHtml(text) {
    return String(text ?? "")
        .replaceAll("&", "&amp;").replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}
async function getJson(url) {
    const response = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
    return response.json();
}
async function sendForm(form) {
    const response = await fetch(form.action, {
        method: "POST",
        headers: { "X-Requested-With": "fetch" },
        body: new FormData(form),
    });
    return response.json();
}
function showMessage(text, type = "success") {
    const box = document.querySelector("#messages");
    if (!box || !text) return;
    box.innerHTML = `<div class="alert alert-${type} message">${escapeHtml(text)}</div>`;
}
function showMessageAfterRedirect(text) {
    if (text) sessionStorage.setItem("message", text);
}
function showFieldErrors(form, errors) {
    form.querySelectorAll("[data-error]").forEach((box) => { box.textContent = ""; });
    form.querySelectorAll(".is-invalid").forEach((f) => f.classList.remove("is-invalid"));
    for (const [name, text] of Object.entries(errors)) {
        const box = form.querySelector(`[data-error="${name}"]`);
        if (box) {
            box.textContent = text;
            const field = box.parentElement.querySelector(".form-control, .form-select");
            if (field) field.classList.add("is-invalid");
        }
    }
}
async function renderMenu() {
    const data = await getJson("/api/me");
    const user = data.user;
    let links;
    if (user && user.role === "admin") {
        links = [["/admin", "Заявки"], ["/logout", "Выйти"]];
    } else if (user) {
        links = [["/cabinet", "Мои заявки"], ["/booking/new", "Новая заявка"], ["/logout", "Выйти"]];
    } else {
        links = [["/login", "Вход"], ["/register", "Регистрация"]];
    }
    document.querySelector("#nav").innerHTML = links
        .map(([href, text]) => `<a class="nav__link" href="${href}">${text}</a>`).join("");
    return user;
}
const currentUser = renderMenu();
const savedMessage = sessionStorage.getItem("message");
if (savedMessage) { showMessage(savedMessage); sessionStorage.removeItem("message"); }