import aio_pika


async def base_consumer_callback(message: aio_pika.abc.AbstractIncomingMessage):
    print(message)
    print(message.body)
