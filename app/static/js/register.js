
const registerForm = document.getElementById("registerForm");
const errorMessage = document.getElementById("errorMessage");

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    errorMessage.textContent = "";

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    try {
        const response = await fetch("/api/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                username: username,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok) {
            window.location.href = "/";
        } else {
            errorMessage.textContent =
                data.detail || "Не удалось зарегистрироваться.";
        }

    } catch (error) {
        errorMessage.textContent = "Не удалось связаться с сервером.";
    }
});
