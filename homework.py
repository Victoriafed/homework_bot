import os
import logging
import sys

from datetime import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setStream(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
)
handler.setFormatter(formatter)


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
    except Exception:
        logging.error('Ошибка при отправке сообщения')
    else:
        logger.debug('Сообщение успешно отправленно в чат')


def get_api_answer(timestamp):
    """Запрос к API-сервиса."""
    try:
        response = requests.get(
            url=ENDPOINT, headers=HEADERS, params=timestamp
        )
        if response.status_code != HTTPStatus.OK:
            raise ConnectionError
    except requests.RequestException as error:
        logging.error(f'Сбой API не доступен: {error}')
    return response.json()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if isinstance(response, dict):
        if 'homeworks' in response:
            if isinstance(response.get('homeworks'), list):
                return response.get('homeworks')
            raise TypeError("API возвращает не список.")
        raise KeyError('Не найден ключ homeworks.')
    raise TypeError('API возвращает не словарь.')


def parse_status(homework):
    """Получает статутс домашнего задания."""
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise TypeError
    verdict = HOMEWORK_VERDICTS.get(homework.get('status'))
    if homework.get('status') not in HOMEWORK_VERDICTS:
        raise ValueError(f'Неизвестный статус работы: {verdict}')
    return f'Изменился статус проверки работы "{homework_name}": {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
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
