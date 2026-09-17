import asyncio
import xml.etree.ElementTree as ET
import json
from datetime import datetime
from typing import Any, Dict, Optional, SupportsIndex

import aiohttp

from src.utils import backend_logger as logger
from config import settings


class NetlabAPI:
    def __init__(self, login: str, password: str, token: Optional[str] = None, expires: Optional[str] = None):
        """Инициализация API клиента для работы с ботом."""
        self.login = login
        self.password = password
        self.token = token
        self.expires = expires
        self.auth = False

        if not all([self.login, self.password]):
            raise ValueError("Необходимо установить логин и пароль")

    def _is_token_expired(self) -> bool:
        if not self.expires:
            return True

        try:
            expires_dt = datetime.fromisoformat(self.expires)
            return datetime.now() >= expires_dt
        except ValueError:
            return True

    async def authenticate(self) -> bool:
        """Асинхронная аутентификация в API."""
        logger.info(f"Попытка аутентификации для пользователя: {self.login}")
        url = settings.netlab_config.get("auth_url")
        params = {'username': self.login, 'password': self.password}
        headers = {'User-Agent': 'Mozilla/5.0'}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as response:
                    response_text = await response.text()
                    logger.debug(f"Raw response: {response_text}")

                    if not response_text:
                        logger.error("Пустой ответ от сервера")
                        return False

                    # Очистка ответа от не-JSON частей
                    cleaned_response = response_text.strip()
                    if '&&' in cleaned_response:
                        json_part = cleaned_response.split('&&', 1)[1].strip()
                    else:
                        json_part = cleaned_response

                    try:
                        data = json.loads(json_part)
                    except json.JSONDecodeError as e:
                        logger.error(f"Ошибка парсинга JSON: {e}\nОригинальный ответ: {cleaned_response}")
                        return False

                    if not data or not isinstance(data, dict):
                        logger.error(f"Некорректный формат данных: {data}")
                        return False

                    token_response = data.get('tokenResponse', {})
                    if not token_response:
                        logger.error("Отсутствует tokenResponse в ответе")
                        return False

                    status = token_response.get('status', {})
                    if not status:
                        logger.error("Отсутствует status в ответе")
                        return False

                    if status.get('code') == '200':
                        token_data = token_response.get('data', {})
                        if not token_data:
                            logger.error("Отсутствует data в ответе")
                            return False

                        self.token = token_data.get('token')
                        expires_str = token_data.get('expiredIn')

                        if not self.token or not expires_str:
                            logger.error("В ответе отсутствует токен или дата истечения")
                            return False

                        try:
                            expires_dt = datetime.strptime(expires_str, '%d.%m.%Y %H:%M')
                            self.expires = expires_dt.isoformat()
                            logger.info(f"Аутентификация успешна. Токен: {self.token} - действителен до {expires_str}")
                            self.auth = True
                            return True
                        except ValueError as e:
                            logger.error(f"Ошибка парсинга даты: {e}")
                    else:
                        error_msg = status.get('message', 'Неизвестная ошибка')
                        logger.error(f"Ошибка аутентификации: {error_msg}")

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Ошибка сетевого запроса: {e}")
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}", exc_info=True)

        return False

    async def _ensure_auth(self):
        """Проверяет и обновляет аутентификацию при необходимости."""
        if not self.auth or (self.token and self._is_token_expired()):
            if not await self.authenticate():
                raise Exception("Ошибка аутентификации")

    async def get_partnumber_sku(self, sku_number: str) -> Dict[str, Any]:
        """Получение информации о товаре по партномеру (XML)."""
        await self._ensure_auth()

        url = f"{settings.netlab_config.get("api_url")}goodsByPartnumber/{sku_number}.xml?oauth_token={self.token}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    xml_data = await response.text()

                    # Парсинг XML с учетом namespace
                    namespaces = {'ns': 'http://ws.web.netlab.com/'}
                    root = ET.fromstring(xml_data)

                    # Проверка статуса ответа
                    status_code = root.find('.//ns:status/ns:code', namespaces)
                    if status_code is None or status_code.text != '200':
                        logger.error(f"Неверный статус ответа: {status_code.text if status_code else 'нет статуса'}")
                        return {}

                    # Инициализация переменных для сбора данных
                    name = ""
                    total_quantity = 0.0
                    transit = ""
                    remote_warehouse = ""
                    price_f = ""

                    # Обработка данных
                    data = root.find('.//ns:data', namespaces)
                    if data is not None:
                        properties = data.find('ns:properties', namespaces)
                        if properties is not None:
                            for prop in properties.findall('ns:property', namespaces):
                                name_elem = prop.find('ns:name', namespaces)
                                value_elem = prop.find('ns:value', namespaces)
                                if name_elem is None or value_elem is None:
                                    continue

                                prop_name = name_elem.text
                                prop_value = value_elem.text

                                if prop_name == 'название':
                                    name = prop_value
                                elif prop_name == 'цена по категории F':
                                    price_f = float(prop_value)
                                elif prop_name == 'удаленный склад':
                                    remote_warehouse = prop_value
                                elif prop_name == 'количество в транзите':
                                    transit = prop_value
                                elif prop_name.startswith('количество на'):
                                    try:
                                        quantity = float(prop_value) if prop_value else 0.0
                                        total_quantity += quantity
                                    except (ValueError, TypeError):
                                        logger.warning(f"Не удалось преобразовать количество: {prop_value}")

                    # Формирование результата в требуемом формате
                    result = {
                        'Наименование': name,
                        'Количество': total_quantity,
                        'Транзиты': transit,
                        'Удаленный склад': remote_warehouse,
                        'Цена': price_f
                    }

                    logger.info(f'Успешно получены данные для товара {sku_number}')
                    return result

        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.error(f"Ошибка запроса: {e}")
            return {}
        except ET.ParseError as e:
            logger.error(f"Ошибка парсинга XML: {e}")
            return {}
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return {}
