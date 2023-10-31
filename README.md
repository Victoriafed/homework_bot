# homework_bot
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

## Описание
Telegram-бот для отслеживания статуса домашней работы 
Бот:
- каждые 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы
- отправляет сообщение об изменение уведомлений
- логирует и сообщает об ошибках

## Запуск проекта
```
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
```
Выносим токены в .env и запускаем.

### Автор
[Федорова Виктория](https://github.com/Victoriafed)


