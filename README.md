# Телеграм бот по продаже морепродуктов Seafood Bot 🐟

## Описание
Seafood Bot — это телеграмм-бот, предоставляющий функциональность для заказа морепродуктов.

## Регистрация и настройка на www.elasticpath.com

1. Зарегистрируйтесь на [elasticpath](https://www.elasticpath.com/).
2. Создайте новый магазина  "Create New Store"
3. Добавьте новые продукты в разделе "Products" -> "Create New"
4. Создайте иерархию
5. Создайте новый каталог в разделе "Price Books" -> "Add Price Book"
6. Добавьте католог в разделе "Catalogs" -> "Add Catalog" и добавьте в него ранее созданный Price Book
7. Сохраните и опубликуйте католог
8. В разделе Aplication keys создайте новый ключ и Client ID и Client Secret в .env файле

## Переменные окружения
Создать файл `.env` в каталоге с проектом и прописать в нем следующие переменные окружения:

- `TG_TOKEN` — токен вашего бота в Telegram. Получить токен можно у [@BotFather](https://telegram.me/BotFather).
- `REDIS_HOST` — хост для подключения к Redis. Заведите бесплатный аккаунт на [Redis Cloud](https://app.redislabs.com/#/login) и создайте базу данных.
- `REDIS_PORT` — порт для подключения к Redis.
- `REDIS_PASSWORD` — пароль для подключения к Redis.
- `ELASTICPATH_CLIENT_SECRET` смотри пункт 8
- `ELASTICPATH_CLIENT_ID` смотри пункт 8

## Как запустить бота через Docker
Предварительно установите [Docker](https://www.docker.com/) и [Docker Compose](https://docs.docker.com/compose/).

Скачайте код:
```sh
git clone git@github.com:Trm888/Devman_bot_4_lesson_5.git
```

Перейдите в каталог с проектом и создайте образ:
```sh
docker build -t seafood_bot .
```

Запуск бота с использованием Docker Composer:
```sh
docker-compose up -d
```

## Как запустить бота на Windows

Скачайте код:
```sh
git clone git@github.com:Trm888/Devman_bot_4_lesson_5.git
```

Перейдите в каталог с проектом и создайте виртуальное окружение:
```sh
python -m venv venv
```

Активируйте виртуальное окружение:
Для Git Bash:
```sh
source ./venv/Scripts/activate
```
Для PowerShell:
```sh
./venv/Scripts/Activate.ps1
```


Установите зависимости:
```sh
pip install -r requirements.txt
```

Запустите бота:
```sh
python app.py
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). 
