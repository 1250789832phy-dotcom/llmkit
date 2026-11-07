"""pytest 配置，定义可复用的 fixture。"""

import pytest

from llmkit.providers import MockProvider


@pytest.fixture
def mock_provider():
    """返回一个干净的 mock 实例，每个测试拿到的都是独立对象。"""
    return MockProvider()