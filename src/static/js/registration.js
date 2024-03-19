async function registerUser() {
    event.preventDefault();
    document.getElementById("enter").innerText = '';
    document.getElementById('loading-reg').style.display = 'block';
    const formData = new FormData(document.querySelector("form[id='registerForm']"));

    const object = {};
    formData.forEach(function (value, key) {
        object[key] = value;
    });
    if (object['password'] !== object['password1']) {
        document.getElementById('loading-reg').style.display = 'none';
        document.getElementById('errors').textContent = 'Пароли не совпадают'
        document.getElementById("enter").innerText = 'Регистрация';
        return document.getElementById('errors-reg').style.display = 'block';
    }

    const json = JSON.stringify(object);

    await fetch('http://127.0.0.1:8000/user/register/', {
        method: 'POST', headers: {
            'Content-Type': 'application/json',
        }, body: json,
    }).then(response => {
        if (response.status === 403) {
            document.getElementById('loading-reg').style.display = 'none';
            document.getElementById("enter").innerText = 'Регистрация';
            document.getElementById('errors-reg').textContent = 'Имя клуба уже используется'
            return document.getElementById('errors-reg').style.display = 'block';
        } else if (response.status === 404) {
            document.getElementById('loading-reg').style.display = 'none';
            document.getElementById("enter").innerText = 'Регистрация';
            const errors = response.json();
            return alert('Ошибка валидации: ' + JSON.stringify(errors));
        } else if (response.status === 400) {
            document.getElementById('loading-reg').style.display = 'none';
            document.getElementById("enter").innerText = 'Регистрация';
            document.getElementById('errors-reg').textContent = 'Email уже используется'
            return document.getElementById('errors-reg').style.display = 'block';
        } else if (response.status === 422) {
            const x = response.json().then(data => ({
                data: data
            })).then(res => {
                const message = res.data.detail[0].msg
                const pass_err = 'Value error, Password must be between 6 and 8 characters'
                if (message === pass_err) {
                    const msq = 'Пароль должен быть от 6 до 8 символов'
                    document.getElementById('loading-reg').style.display = 'none';
                    document.getElementById("enter").innerText = 'Регистрация';
                    return document.getElementById('errors-reg').textContent = msq
                }
            })
            document.getElementById('loading-reg').style.display = 'none';
            document.getElementById("enter").innerText = 'Регистрация';
            document.getElementById('errors-reg').textContent = 'Ошибка сервера'
            return document.getElementById('errors-reg').style.display = 'block';
        } else if (response.status === 201) {
            document.getElementById('loading-reg').style.display = 'none';
            document.getElementById("enter").innerText = 'Регистрация';
            const em = object.email
            const redirectUrl = "http://127.0.0.1:8000/pages/email/confirm?email=" + em
            return window.location.href = redirectUrl
        }
    });

}


