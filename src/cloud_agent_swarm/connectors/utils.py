import asyncio
import random
from typing import Callable, Coroutine, Any

async def with_retry(
    func: Callable[[], Coroutine[Any, Any, Any]],
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 4.0,
) -> Any:
    """Execute async function with exponential backoff and randomized jitter."""
    last_err = None
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_err = e
            if attempt == max_retries:
                raise last_err
            delay = min(max_delay, base_delay * (2 ** attempt)) + random.uniform(0, 0.1)
            await asyncio.sleep(delay)
