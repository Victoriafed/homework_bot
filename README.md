# homework_bot

## Telegram-бот для отслеживания статуса домашней работы 

Функции:
- каждые 10 минутопрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы
- отправляет сообщение обизменение уведомлений
- логирует и сообщает об ошибках

## Запуск проекта
```
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
Выносим токены в .env и запускаем.

