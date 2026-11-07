"""OpenAI 兼容接口 provider。

学习要点：现在绝大多数模型服务（DeepSeek、通义、Kimi、智谱、
本地 vLLM / Ollama / LM Studio）都提供 /v1/chat/completions 兼容端点。
只要一个适配器 + 改 base_url，就能横跨大部分厂商。
"""

from __future__ import annotations

import json
import os
import time
from collections.abc import Iterator, Sequence

import httpx

from ..errors import ConfigError, NetworkError, classify_http_error
from ..types import ChatResponse, Message, Usage
from .base import Provider, estimate_tokens


class OpenAICompatProvider(Provider):
    """走 HTTP 的真实调用。直接用 httpx，不藏细节，方便理解协议本身。"""

    name = "openai_compat"

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        api_key_env: str = "LLM_API_KEY",
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key or os.getenv(api_key_env)
        if not self.api_key:
            raise ConfigError(
                f"缺少 API key。请设置环境变量 {api_key_env}，或传入 api_key 参数。"
            )
        self.base_url = (
            base_url or os.getenv("LLM_BASE_URL") or "https://api.openai.com/v1"
        ).rstrip("/")
        self.timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _payload(
        self,
        messages: Sequence[Message],
        model: str,
        temperature: float,
        max_tokens: int | None,
        stream: bool,
    ) -> dict:
        payload: dict = {
            "model": model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        return payload

    def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> ChatResponse:
        url = f"{self.base_url}/chat/completions"
        payload = self._payload(messages, model, temperature, max_tokens, False)
        started = time.perf_counter()
        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, headers=self._headers(), json=payload)
        except httpx.HTTPError as exc:
            raise NetworkError(f"网络请求失败: {exc}") from exc

        if resp.status_code >= 400:
            raise classify_http_error(resp.status_code, resp.text)

        data = resp.json()
        latency_ms = int((time.perf_counter() - started) * 1000)
        choice = (data.get("choices") or [{}])[0]
        text = (choice.get("message") or {}).get("content") or ""
        raw_usage = data.get("usage") or {}
        usage = Usage(
            prompt_tokens=raw_usage.get("prompt_tokens")
            or sum(estimate_tokens(m.content) for m in messages),
            completion_tokens=raw_usage.get("completion_tokens")
            or estimate_tokens(text),
        )
        return ChatResponse(
            text=text,
            model=data.get("model", model),
            provider=self.name,
            usage=usage,
            finish_reason=choice.get("finish_reason"),
            latency_ms=latency_ms,
            raw=data,
        )

    def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str,
        temperature: float = 0.7,
        max_tokens: int | None = None,
    ) -> Iterator[str]:
        """解析 SSE 流。

        协议本身很简单：每行 "data: {json}"，以 "data: [DONE]" 结束。
        """
        url = f"{self.base_url}/chat/completions"
        payload = self._payload(messages, model, temperature, max_tokens, True)
        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST", url, headers=self._headers(), json=payload
                ) as resp:
                    if resp.status_code >= 400:
                        raise classify_http_error(resp.status_code, resp.read().decode())
                    for line in resp.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                        except json.JSONDecodeError:
                            continue
                        delta = (chunk.get("choices") or [{}])[0].get("delta") or {}
                        piece = delta.get("content")
                        if piece:
                            yield piece
        except httpx.HTTPError as exc:
            raise NetworkError(f"流式请求失败: {exc}") from exc