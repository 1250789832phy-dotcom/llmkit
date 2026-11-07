"""Mock provider 测试。

学习要点：mock 本身也需要测试，确保它的行为像真实服务。
"""

from llmkit import Message, Usage
from llmkit.providers import MockProvider


def test_mock_scripted_responses():
    """预设回复按顺序返回，用尽后走 synthesize。"""
    provider = MockProvider(scripted=["第一条", "第二条"])
    messages = [Message.user("你好")]

    r1 = provider.complete(messages, model="mock")
    assert r1.text == "第一条"
    assert r1.provider == "mock"
    assert r1.usage.total_tokens > 0

    r2 = provider.complete(messages, model="mock")
    assert r2.text == "第二条"

    r3 = provider.complete(messages, model="mock")
    assert r3.text.startswith("[mock:")


def test_mock_stable_synthesize():
    """同样的输入产生同样的哈希回复，保证可复现。"""
    provider = MockProvider()
    m1 = [Message.user("测试稳定性")]
    m2 = [Message.user("测试稳定性")]

    assert provider.complete(m1, model="x").text == provider.complete(m2, model="x").text


def test_mock_stream():
    """流式返回会分块。"""
    provider = MockProvider(scripted=["12345678901234"])
    messages = [Message.user("流式测试")]
    chunks = list(provider.stream(messages, model="mock"))
    assert len(chunks) > 1
    assert "".join(chunks) == "12345678901234"