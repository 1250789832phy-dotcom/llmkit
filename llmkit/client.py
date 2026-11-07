"""Client 入口。

学习要点：业务代码永远只依赖 LLMClient 这一个类，provider 从外部注入。
这是"依赖注入"，让代码好测、好扩展、好组装。
"""

from __future__ import annotations

import logging
import time
from collections.abc import Iterator, Sequence

from .errors import LLMError
from .providers.base import Provider
from .types import ChatResponse, Message

logger = logging.getLogger(__name__)


class LLMClient:
    """一个支持重试退避的高层封装。"""

    def __init__(self, provider: Provider) -> None:
        self.provider = provider

    def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
        retries: int = 3,
        backoff_base: float = 1.0,
    ) -> ChatResponse:
        """带重试的同步调用。

        参数:
            retries: 最多重试几次（不含首次尝试）。
            backoff_base: 指数退避的基数，第 n 次重试等 backoff_base * 2^n 秒。
        """
        attempt = 0
        while True:
            try:
                return self.provider.complete(
                    messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except LLMError as exc:
                if not exc.retryable or attempt >= retries:
                    logger.error(
                        "请求失败(不可重试或已用尽重试): %s",
                        exc,
                        exc_info=True,
                    )
                    raise
                wait = backoff_base * (2**attempt)
                logger.warning("第%d次重试(%s)，等待%.1fs", attempt + 1, exc, wait)
                time.sleep(wait)
                attempt += 1

    def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """流式调用，把退避交给业务层做（否则用户要等半天才看到错误）。"""
        return self.provider.stream(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )