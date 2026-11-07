"""与具体厂商无关的核心数据结构。

学习要点：先定义自己的领域模型，再去适配各家 API。
这样换模型/换厂商时，上层业务代码一行都不用改。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True)
class Message:
    """一条对话消息。frozen=True 让它不可变，避免历史被意外改写。"""

    role: Role
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls("system", content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls("user", content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls("assistant", content)


@dataclass(frozen=True)
class Usage:
    """token 用量。成本核算、限流、计费都依赖它。"""

    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
        )


@dataclass(frozen=True)
class ChatResponse:
    """一次补全的结果。raw 保留原始返回，方便排查线上问题。"""

    text: str
    model: str
    provider: str
    usage: Usage = field(default_factory=Usage)
    finish_reason: str | None = None
    latency_ms: int = 0
    raw: dict[str, Any] | None = None