import timeit
from functools import wraps
from typing import Callable, Any

from core.project.utils import logger_info


def async_timed(func: Callable) -> Callable:
    @wraps(func)
    async def wrapped(*args, **kwargs) -> Any:
        logger_info.info(f"выполняется {func} с аргументами {args} {kwargs}")
        start = timeit.default_timer()
        try:
            return await func(*args, **kwargs)
        finally:
            total = timeit.default_timer() - start
            logger_info.info(f"{func} завершилась за {total:.4f} с")

    return wrapped
