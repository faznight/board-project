
const adsContainer = document.getElementById("adsContainer");
const searchInput = document.getElementById("searchInput");
const searchButton = document.getElementById("searchButton");
const categoryFilter = document.getElementById("categoryFilter");
const sortSelect = document.getElementById("sortSelect");
const createForm = document.getElementById("createForm");
const adForm = document.getElementById("adForm");

// Проверка авторизации
async function checkUser() {
    const response = await fetch("/api/auth/me");

    if (!response.ok) {
        window.location.href = "/login";
        return;
    }

    const user = await response.json();
    document.getElementById("username").textContent = user.username;

    loadCategories();
    loadAds();
}

// Загрузка категорий
async function loadCategories() {
    const response = await fetch("/api/categories/");

    if (!response.ok) return;

    const categories = await response.json();

    categories.forEach(category => {
        const option1 = document.createElement("option");
        option1.value = category.id;
        option1.textContent = category.name;
        categoryFilter.appendChild(option1);

        const option2 = document.createElement("option");
        option2.value = category.id;
        option2.textContent = category.name;
        document.getElementById("adCategory").appendChild(option2);
    });
}

// Загрузка объявлений
async function loadAds() {
    adsContainer.innerHTML = "<p>Загрузка объявлений...</p>";

    const params = new URLSearchParams();

    if (searchInput.value.trim()) {
        params.append("q", searchInput.value.trim());
    }

    if (categoryFilter.value) {
        params.append("category_id", categoryFilter.value);
    }

    params.append("sort", sortSelect.value);

    const isMyAds = window.location.pathname === "/my-ads";

document.getElementById("adsHeading").textContent =
    isMyAds ? "Мои объявления" : "Все объявления";

const url = isMyAds
    ? "/api/ads/mine"
    : `/api/ads/?${params}`;

const response = await fetch(url);

    if (response.status === 401) {
        window.location.href = "/login";
        return;
    }

    if (!response.ok) {
        adsContainer.innerHTML = "<p>Не удалось загрузить объявления.</p>";
        return;
    }

    const ads = await response.json();

    if (ads.length === 0) {
        adsContainer.innerHTML = "<p>Объявлений пока нет.</p>";
        return;
    }

    adsContainer.innerHTML = "";

    ads.forEach(ad => {
        const card = document.createElement("article");
        card.className = "ad-card";

        const title = document.createElement("h3");
        title.textContent = ad.title;

        const description = document.createElement("p");
        description.textContent = ad.description;

        const price = document.createElement("div");
        price.className = "ad-price";
        price.textContent = `${ad.price} ₽`;

        card.append(title, description, price);

        if (window.location.pathname === "/my-ads") {
            const actions = document.createElement("div");
            actions.className = "ad-actions";

            const editButton = document.createElement("button");
            editButton.className = "button button-primary";
            editButton.textContent = "Изменить";
            editButton.onclick = () => editAd(ad);

            const deleteButton = document.createElement("button");
            deleteButton.className = "button button-outline";
            deleteButton.textContent = "Удалить";
            deleteButton.onclick = () => deleteAd(ad.id);

            actions.append(editButton, deleteButton);
            card.appendChild(actions);
        }

        adsContainer.appendChild(card);
    });
}

// Создание объявления
adForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const ad = {
        title: document.getElementById("adTitle").value,
        description: document.getElementById("adDescription").value,
        price: Number(document.getElementById("adPrice").value),
        category_id: Number(document.getElementById("adCategory").value)
    };

    const response = await fetch("/api/ads/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(ad)
    });

    if (response.ok) {
        adForm.reset();
        createForm.classList.add("hidden");
        loadAds();
        alert("Объявление успешно опубликовано!");
    } else {
        alert("Не удалось создать объявление.");
    }
});

// Редактирование объявления
async function editAd(ad) {
    const title = prompt("Новое название:", ad.title);
    if (title === null) return;

    const price = prompt("Новая цена:", ad.price);
    if (price === null) return;

    const response = await fetch(`/api/ads/${ad.id}`, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            title: title,
            price: Number(price)
        })
    });

    if (response.ok) {
        alert("Объявление изменено!");
        loadAds();
    } else {
        alert("Ошибка при редактировании.");
    }
}

// Удаление объявления
async function deleteAd(id) {
    if (!confirm("Удалить это объявление?")) return;

    const response = await fetch(`/api/ads/${id}`, {
        method: "DELETE"
    });

    if (response.ok) {
        alert("Объявление удалено!");
        loadAds();
    } else {
        alert("Ошибка при удалении.");
    }
}

// Кнопка поиска
searchButton.addEventListener("click", loadAds);

// Поиск при нажатии Enter
searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") loadAds();
});

// Фильтры
categoryFilter.addEventListener("change", loadAds);
sortSelect.addEventListener("change", loadAds);

// Открытие формы создания
document.getElementById("openCreateForm").addEventListener("click", () => {
    createForm.classList.toggle("hidden");
});

// Мои объявления
document.getElementById("myAdsLink").addEventListener("click", (event) => {
    event.preventDefault();
    window.location.href = "/my-ads";
});

// Выход из аккаунта
document.getElementById("logoutButton").addEventListener("click", async () => {
    await fetch("/api/auth/logout", {
        method: "POST"
    });

    window.location.href = "/login";
});

// Запуск приложения
checkUser();
