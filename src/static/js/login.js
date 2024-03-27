async function loginUser() {
    event.preventDefault();
    document.getElementById("enter").innerText = '';
    document.getElementById('errors-enter').style.display = 'none';
    document.getElementById('loading-enter').style.display = 'block';
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    await fetch("http://127.0.0.1:8000/user/login/", {
        method: 'POST',
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({'email': email, 'password': password})
    }).then(response => {
        if (response.status === 404) {
            document.getElementById('loading-enter').style.display = 'none';
            document.getElementById("enter").innerText = 'Вход';
            document.getElementById('errors-enter').textContent = 'Пользователь не найден';
            return document.getElementById('errors-enter').style.display = 'block';
        } else if (response.status === 403) {
            document.getElementById('loading-enter').style.display = 'none';
            document.getElementById("enter").innerText = 'Вход';
            document.getElementById('errors-enter').textContent = 'Неверный логин или пароль';
            return document.getElementById('errors-enter').style.display = 'block';
        } else if (response.status === 422) {
            document.getElementById('loading-enter').style.display = 'none';
            document.getElementById("enter").innerText = 'Вход';
            document.getElementById('errors-enter').textContent = 'Ошибка сервера, попробуйте позже!';
            return document.getElementById('errors-enter').style.display = 'block';
        } else if (response.status === 200) {
            document.getElementById('loading-enter').style.display = 'none';
            document.getElementById("enter").innerText = 'Вход';
            return window.location.href = "http://127.0.0.1:8000/pages/home/";
        }
    });
}
