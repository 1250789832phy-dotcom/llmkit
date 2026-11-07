"""离线 mock provider。

学习要点：AI 应用最难测的就是"模型输出不稳定"。
做法是把模型调用藏在 Provider 接口后面，测试时换成确定性实现。
这样 CI 不需要 API key、不花钱、不受网络影响。
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Iterator, Sequence

from ..errors import RateLimitError, ServerError
from ..types import ChatResponse, Message, Usage
from .base import Provider, estimate_tokens


class MockProvider(Provider):
    """确定性的假模型。

    参数:
        scripted: 预设回复队列，按调用顺序返回，适合写测试断言。
        fail_times: 前 N 次调用抛可重试异常，用来验证退避逻辑。
        fail_with: 抛出的异常类型，"rate_limit" 或 "server"。
        latency_ms: 模拟网络延迟。
    """

    name = "mock"

    def __init__(
        self,
        *,
        scripted: Sequence[str] | None = None,
        fail_times: int = 0,
        fail_with: str = "server",
        latency_ms: int = 0,
    ) -> None:
        self._scripted = list(scripted or [])
        self._cursor = 0
        self._fail_times = fail_times
        self._fail_with = fail_with
        self._latency_ms = latency_ms
        self.call_count = 0
        self.last_messages: list[Message] = []

    def _next_text(self, messages: Sequence[Message]) -> str:
        if self._cursor < len(self._scripted):
            text = self._scripted[self._cursor]
            self._cursor += 1
            return text
        return self._synthesize(messages)

    @staticmethod
    def _synthesize(messages: Sequence[Message]) -> str:
        """没有预设脚本时，根据输入生成稳定可复现的回复。"""
        last_user = next(
            (m.content for m in reversed(messages) if m.role == "user"), ""
        )
        digest = hashlib.sha256(last_user.encode("utf-8")).hexdigest()[:8]
        return f"[mock:{digest}] 收到你的问题：{last_user[:80]}"

    def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        self.call_count += 1
        self.last_messages = list(messages)

        if self.call_count <= self._fail_times:
            if self._fail_with == "rate_limit":
                raise RateLimitError("mock 限流", retry_after=0.01)
            raise ServerError("mock 服务端错误", status_code=503)

        if self._latency_ms:
            time.sleep(self._latency_ms / 1000)

        text = self._next_text(messages)
        if max_tokens is not None and max_tokens > 0:
            text = text[: max_tokens * 4]

        prompt_tokens = sum(estimate_tokens(m.content) for m in messages)
        return ChatResponse(
            text=text,
            model=model,
            provider=self.name,
            usage=Usage(prompt_tokens, estimate_tokens(text)),
            finish_reason="stop",
            latency_ms=self._latency_ms,
            raw={"mock": True, "call": self.call_count},
        )

    def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """按字符切块，模拟真实流式的分片节奏。"""
        response = self.complete(
            messages, model=model, temperature=temperature, max_tokens=max_tokens
        )
        chunk = 6
        for i in range(0, len(response.text), chunk):
            yield response.text[i : i + chunk]