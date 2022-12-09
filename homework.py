import os
import logging
import sys
import time
import requests
import telegram

from http import HTTPStatus
from dotenv import load_dotenv
from telegram import TelegramError
from exceptions import ServerNotAvailableException, APINotAvailableException

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
)
handler = logging.StreamHandler()
handler.setStream(sys.stdout)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


def check_tokens():
    """Проверка доступности переменных окружения."""
    if not PRACTICUM_TOKEN or not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.critical('Отсутствует обязательная переменная окружения')
        return False
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except TelegramError:
        logging.error('Ошибка при отправке сообщения')
    else:
        logger.debug('Сообщение успешно отправленно в чат')


def get_api_answer(timestamp):
    """Запрос к API-сервиса."""
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            url=ENDPOINT, headers=HEADERS, params=params
        )
    except requests.RequestException as error:
        raise APINotAvailableException(f'Сбой API не доступен: {error}')
    if response.status_code != HTTPStatus.OK:
        raise ServerNotAvailableException(
            f"Не удалось выполнить запрос - {response.status_code}"
        )
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('API возвращает не словарь.')
    if 'homeworks' not in response.keys():
        raise KeyError('Не найден ключ homeworks.')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError("API возвращает не список.")
    return response.get('homeworks')


def parse_status(homework):
    """Получает статутс домашнего задания."""
    homework_name = homework.get('homework_name')
    if 'homework_name' not in homework:
        raise KeyError(f'Отсутсвует ключ {homework_name}')
    status = homework.get('status')
    if status not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы:{homework.get("status")}')
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    if verdict is None:
        logging.error(f'Неизвестный статус работы')
    return f'Изменился статус проверки работы "{homework_name}": {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        sys.exit('Отсутвуют переменные окружения')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                send_message(bot, parse_status(homeworks[0]))
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
