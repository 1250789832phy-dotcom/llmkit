"""Provider 抽象基类。

学习要点：这就是"适配器模式"。上层只认 Provider 接口，
下面可以是 mock、OpenAI 兼容接口、甚至本地 Ollama。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator, Sequence

from ..types import ChatResponse, Message


class Provider(ABC):
    """一个模型服务的最小能力集合。"""

    name: str = "base"

    @abstractmethod
    def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        """一次性拿到完整回复。"""

    def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """流式输出增量文本。

        默认实现是"假流式"：先拿完整结果再一次吐出。
        子类如果支持 SSE，就覆盖这个方法换成真流式。
        """
        response = self.complete(
            messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        yield response.text


def estimate_tokens(text: str) -> int:
    """粗略估算 token 数。

    中文约 1 字 1 token，英文约 4 字符 1 token。
    真实项目要用 tiktoken；这里先建立"用量可观测"的习惯。
    """
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff")
    rest = len(text) - cjk
    return cjk + max(1, round(rest / 4)) if text else 0