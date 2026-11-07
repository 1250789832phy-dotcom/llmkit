"""重试策略测试。

学习要点：这就是 TDD（Test-Driven Development）的精髓：
先写测试定义"什么叫正确"，再写实现跑通它。
"""

import pytest

from llmkit import LLMClient, Message, RateLimitError
from llmkit.providers import MockProvider


def test_client_retry_until_success():
    """模拟前 2 次限流、第 3 次成功的场景。"""
    provider = MockProvider(
        fail_times=2,
        fail_with="rate_limit",
        scripted=["重试成功后的回复"],
    )
    client = LLMClient(provider)
    messages = [Message.user("测试重试")]

    response = client.complete(messages, model="test", retries=3, backoff_base=0.01)
    assert response.text == "重试成功后的回复"
    assert provider.call_count == 3


def test_client_exhaust_retries():
    """一直失败，直到耗尽重试次数。"""
    provider = MockProvider(fail_times=10, fail_with="rate_limit")
    client = LLMClient(provider)
    messages = [Message.user("测试重试")]

    with pytest.raises(RateLimitError):
        client.complete(messages, model="test", retries=2, backoff_base=0.01)
    assert provider.call_count == 3


def test_client_no_retry_on_bad_request():
    """4xx 错误不会重试。"""
    provider = MockProvider(fail_times=1, fail_with="bad_request")

    client = LLMClient(provider)
    messages = [Message.user("测试不可重试")]

    from llmkit.errors import BadRequestError

    provider.complete = lambda *args, **kw: (_ for _ in ()).throw(
        BadRequestError("输入非法")
    )

    with pytest.raises(BadRequestError):
        client.complete(messages, model="test", retries=3)