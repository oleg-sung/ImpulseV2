// async function registerUser() {
//
//     // Создаем объект FormData из формы
//     const formData = new FormData(document.querySelector("form[id='registerForm']"));
//
//     // Преобразуем FormData в объект
//     const object = {};
//     formData.forEach(function (value, key) {
//         object[key] = value;
//     });
//
//     // Преобразуем объект в JSON
//     const json = JSON.stringify(object);
//
//     // Отправляем JSON с помощью fetch
//     const response = await fetch('user/register/', {
//         method: 'POST', // или 'PUT'
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: json,
//     });
//     if (response.ok) {
//         const data = await response.json();
//         alert('Успешная регистрация: ' + JSON.stringify(data.user));
//         redirectUrl = "pages/email/confirm?email=" + encodeURIComponent(email)
//         return window.location.href = redirectUrl
//     } else {
//         const errors = await response.json();
//         alert('Ошибка валидации: ' + JSON.stringify(errors));
//     }
//
// }