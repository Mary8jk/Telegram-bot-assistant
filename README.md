# Telegram бот-ассистент на Python #

Телеграм бот-ассистент раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы, при обновлении статуса анализирует ответ API и отправляет соответствующее уведомление в Telegram. <br>
Бот-ассистент логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

## Стек технологий ##
+ Python 3.10.10
+ telegram bot
+ OAuth 
+ logger


## Установка
Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Mary8jk/Telegram-bot-assistant.git
```

```
cd homework_bot
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
