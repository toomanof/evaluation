### Базовое описание сервиса "Брокер"

Сервис предоставляет возможность добавить любое количество уникальных паблишеров и консьюмеров. Каждую сущность можно настроить уникально в зависимости от требуемых параметров.

### Схема подключения сервиса в aiohttp приложение
1. Создать брокер в init файле сервиса (core/project/services/broker/__init__.py)
```python
main_broker = RabbitMQBroker(
    url=settings.RABBIT_MQ.get("url"),)

```
2. Заполнить контроллер в зависимости от требований в том же файле (core/project/services/broker/__init__.py)
```python
from core.project.services.broker.schemas import ConsumerParams
from core.project.services.broker.callbacks import base_consumer_callback

consumer_params = ConsumerParams(callback=base_consumer_callback)

async def run_main_broker(app: Application):
    connection = await main_broker.get_connection(app)
    async with connection:
            # Добавляем паблишера для микросервиса "отслеживание остатков"
        await main_broker.add_publisher("stock_publisher", settings.STOCK_QUEUE_PUBLISHER)

```

* названия консьюмеров и паблишеров должны быть уникальными. Это нужно для возможности оперировать сущностями(консьюмеры и паблишеры)
* колбэки обработчики для консьюмеров можно описать в файле (core.project.services.broker.callbacks) и применять их для своих консьюмеров
3. Добавить объекты в приложение aiohttp (файл main.py)
```python
def main():
    app = web.Application(middlewares=settings.MIDDLEWARE)
    app.on_startup.append(run_main_broker)  # Подключение брокера

```
4. Отправка сообщения в нужную очередь
```python
from core.project.services.broker.utils import convert_pydantic_message_to_aio_pika

aio_pika_message = convert_pydantic_message_to_aio_pika(pydantic_obj)
await main_broker.publish("publisher_name", aio_pika_message)
```
* по publisher_name мы понимаем в какую очереь отправлять, тк мы определили этого паблишера в пункте №2
* в метод publish нужно передать подходящее сообщение для aio_pika, для этого можно воспользоваться утилитой convert_pydantic_message_to_aio_pika, которая принимает любой pydantic объект
* метод convert_pydantic_message_to_aio_pika принимает параметры:
```python
        headers: Optional[HeadersType] = None,
        content_type: Optional[str] = None,
        content_encoding: Optional[str] = None,
        delivery_mode: Union[DeliveryMode, int, None] = None,
        priority: Optional[int] = None,
        correlation_id: Optional[str] = None,
        reply_to: Optional[str] = None,
        expiration: Optional[DateType] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[DateType] = None,
        type: Optional[str] = None,
        user_id: Optional[str] = None,
        app_id: Optional[str] = None,"""
```
