import logging
import sys
import os
import time
import requests
import telegram
from http import HTTPStatus
from dotenv import load_dotenv
from exceptions import StatusException

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
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if not all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        raise logger.critical('Отсутсвуют одна или несколько '
                              'переменных окружения')
    return True


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception as error:
        logger.error(f'Сбой при отправке сообщения {error}')
    logger.debug('Сообщение отправлено')


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса.
    В случае успешного запроса возвращает ответ API,
    приведя его из формата JSON к типам данных Python.
    """
    params = {'from_date': timestamp}
    try:
        response_get = requests.get(ENDPOINT, headers=HEADERS,
                                    params=params)
    except requests.RequestException as error:
        raise ConnectionError(f'Ошибка при запросе к API: {error}')
    if response_get.status_code != HTTPStatus.OK:
        raise StatusException(f'Ошибка HTTPs: {response_get.status_code}')
    response = response_get.json()
    return response


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not isinstance(response, dict):
        raise TypeError('Ошибка типа данных "dict"')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Ошибка типа данных "list"')
    try:
        'current_date' and 'homeworks' in response.keys()
    except KeyError:
        logger.error('Ключей current_date и homeworks нет в словаре')
    return response['homeworks']


def parse_status(homework):
    """Извлекает из информации о конкретной домашней работе статус работы."""
    if not isinstance(homework, dict):
        logger.error('Ошибка типа данных "dict"')
        raise TypeError('Ошибка типа данных "dict"')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_name is None:
        logger.error('В словаре нет ключа homework_name')
        raise ValueError('В словаре нет ключа homework_name')
    if homework_status is None:
        logger.error('В словаре нет ключа status')
        raise ValueError('В словаре нет ключа status')
    if homework_status not in HOMEWORK_VERDICTS:
        logger.error('Неизвестный статус домашки')
        raise ValueError('Неизвестный статус')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return (f'Изменился статус проверки работы "{homework_name}". {verdict}')


def main():
    """Основная логика работы бота."""
    if check_tokens() is not True:
        logger.critical('Принудительное завершение программы')
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                homework_status = parse_status(homework)
                message = homework_status
            return send_message(bot, message)
        except Exception as error:
            error_message = (f'Сбой в работе программы: {error}')
            logger.error(error_message)
            send_message(bot, error_message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
