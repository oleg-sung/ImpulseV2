function CreateCoachCode() {
    document.getElementById('create-coach-code').addEventListener('click', function () {
        fetch('http://127.0.0.1:8000/token/create/', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',

            },
        })
            .then(response => response.json())
            .then(data => {
                console.log(data);
                location.reload();
            })
            .catch(error => {
                console.error('Ошибка загрузки данных:', error);
            });
    });
}


function DisableCode(tikenId) {
    document.getElementById(`checkbox-${tikenId}`).addEventListener('click', function () {
        this.disabled = true;
        fetch(`http://127.0.0.1:8000/token/disable/${tikenId}/`, {
            method: 'PATCH',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',

            },
        })
            .then(response => response.json())
            .then(data => {
                // Обработка полученных данных
                console.log(data);

                // Скрыть индикатор загрузки
                this.disabled = false;
                location.reload();
            })
            .catch(error => {
                console.error('Ошибка загрузки данных:', error);
                // Скрыть индикатор загрузки в случае ошибки
                this.disabled = false;
            });
    });
}