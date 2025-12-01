1) Установите PostgreSQL
Скачайте установщик: postgresql.org → Download → Windows → последняя LTS.
Установите Postgres + pgAdmin. Запомните пароль пользователя postgres.
Создайте БД:
Откройте pgAdmin → Servers → PostgreSQL → Databases → Create → Database…
Name: crmhotdog
Owner: postgres (или другой пользователь)
2) Установите Python 3.12+
python.org → Downloads → Windows → установите с опцией “Add Python to PATH”.
3) Скачайте код
Скопируйте папку проекта на диск, например: C:\DonHotDog\CRM
4) Настройте подключение к БД
Вариант A (локальная БД, установленная на этом ПК):
Строка подключения:
DATABASE_URL=postgresql://postgres:ваш_пароль@localhost:5432/crmhotdog

Откройте PowerShell и задайте переменные окружения (пример для локальной БД):

        cd "C:\DonHotDog\CRM\backend"
        $env:DATABASE_URL="postgresql://postgres:Пароль@localhost:5432/crmhotdog"
        $env:SECRET_KEY="your-secret-key-change-in-production-12345"
        $env:MAIL_SERVER="smtp.mail.ru"
        $env:MAIL_PORT="465"
        $env:MAIL_USE_TLS="True"
        $env:MAIL_USERNAME="wfdanya1@mail.ru"
        $env:MAIL_PASSWORD="7bjT8G9xIFgwCB5EHJyQ"
        $env:MAIL_DEFAULT_SENDER="wfdanya1@mail.ru"
6) Создайте виртуальное окружение и установите зависимости
В PowerShell:

       cd "C:\DonHotDog\CRM\backend"

       py -m venv .venv

        .\.venv\Scripts\python -m pip install --upgrade pip

        .\.venv\Scripts\pip install -r requirements.txt

        python -m pip install click

        .\.venv\Scripts\Activate.ps1

        python -m pip install flask flask-sqlalchemy flask-login flask-migrate flask-cors flask-mail flask-wtf python-dotenv click email-validator

        python -m pip install psycopg2-binary --no-cache-dir --force-reinstall

8) Инициализируйте базу (создание таблиц и базовых данных)
В PowerShell:

       .\.venv\Scripts\python manage.py init-db
Команда создаст таблицы, роль admin, а также базовые столы (1…6).
9) Запустите сервер
В PowerShell:

    .\.venv\Scripts\python wsgi.py
    
Откройте в браузере:
http://localhost:8000
