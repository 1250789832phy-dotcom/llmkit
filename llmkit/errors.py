"""错误分类。

学习要点：调用外部 API 时，"能不能重试"是最重要的信息。
把它放进异常类型里，重试逻辑就不用到处写 if status == 429。
"""

from __future__ import annotations


class LLMError(Exception):
    """所有 llmkit 异常的基类。"""

    retryable = False

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class ConfigError(LLMError):
    """配置缺失或非法，比如没设置 API key。"""


class AuthError(LLMError):
    """401/403，key 无效或没权限。重试没用。"""


class BadRequestError(LLMError):
    """400，请求体有问题，比如超出上下文长度。重试没用。"""


class RateLimitError(LLMError):
    """429，被限流。可以退避后重试。"""

    retryable = True

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = 429,
        retry_after: float | None = None,
    ) -> None:
        super().__init__(message, status_code=status_code)
        self.retry_after = retry_after


class ServerError(LLMError):
    """5xx，服务端抖动。可以退避后重试。"""

    retryable = True


class NetworkError(LLMError):
    """连接超时、DNS 失败等。可以退避后重试。"""

    retryable = True


def classify_http_error(status_code: int, body: str) -> LLMError:
    """把 HTTP 状态码映射成我们自己的异常类型。"""
    snippet = body.strip()[:500]
    if status_code in (401, 403):
        return AuthError(f"认证失败({status_code}): {snippet}", status_code=status_code)
    if status_code == 429:
        return RateLimitError(f"被限流(429): {snippet}")
    if 400 <= status_code < 500:
        return BadRequestError(f"请求错误({status_code}): {snippet}", status_code=status_code)
    return ServerError(f"服务端错误({status_code}): {snippet}", status_code=status_code)