"""示例 1：使用 MockProvider 进行离线测试。

学习要点：
1. 无需 API key，无需网络
2. 输出确定性，适合写单元测试
3. 可以注入失败，验证重试逻辑
"""

import sys
from pathlib import Path

# 将 llmkit 加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message


def example_basic():
    """基础用法：确定性输出"""
    print("=" * 70)
    print("示例 1: 基础 MockProvider")
    print("=" * 70)
    
    provider = MockProvider()
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="你好")]
    response = client.complete(messages, model="mock-model")
    
    print(f"输入: {messages[0].content}")
    print(f"输出: {response.text}")
    print(f"Token 用量: {response.usage.total_tokens}")
    print()


def example_scripted():
    """脚本模式：预设回复队列"""
    print("=" * 70)
    print("示例 2: 脚本模式 - 预设回复")
    print("=" * 70)
    
    # 预设 3 个回复
    provider = MockProvider(scripted=[
        "第一次调用的回复",
        "第二次调用的回复",
        "第三次调用的回复",
    ])
    client = LLMClient(provider)
    
    for i in range(4):  # 调用 4 次，超出预设
        messages = [Message(role="user", content=f"问题 {i+1}")]
        response = client.complete(messages, model="mock")
        print(f"{i+1}. {response.text}")
    print()


def example_failure_injection():
    """失败注入：测试重试逻辑"""
    print("=" * 70)
    print("示例 3: 失败注入 - 验证重试")
    print("=" * 70)
    
    # 前 2 次失败，第 3 次成功
    provider = MockProvider(
        fail_times=2,
        fail_with="server",
        scripted=["重试成功！"]
    )
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="测试重试")]
    
    try:
        # retries 参数在 complete 方法中
        response = client.complete(messages, model="mock", retries=3)
        print(f"[成功] 最终成功: {response.text}")
        print(f"[成功] 总共调用了 {provider.call_count} 次")
    except Exception as e:
        print(f"[失败] 失败: {e}")
    print()


def example_deterministic():
    """确定性输出：相同输入 → 相同输出"""
    print("=" * 70)
    print("示例 4: 确定性输出")
    print("=" * 70)
    
    provider = MockProvider()
    client = LLMClient(provider)
    
    # 相同输入调用两次
    test_input = "计算 1+1"
    for i in range(2):
        messages = [Message(role="user", content=test_input)]
        response = client.complete(messages, model="mock")
        print(f"第 {i+1} 次: {response.text}")
    
    print("\n关键：两次输出完全相同！适合写单元测试断言。")
    print()


def example_stream():
    """流式输出"""
    print("=" * 70)
    print("示例 5: 流式输出")
    print("=" * 70)
    
    provider = MockProvider(scripted=["这是一段较长的流式输出内容，会被分块返回"])
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="给我讲个故事")]
    
    print("流式输出: ", end="", flush=True)
    for chunk in client.stream(messages, model="mock"):
        print(chunk, end="", flush=True)
    print("\n")


if __name__ == "__main__":
    example_basic()
    example_scripted()
    example_failure_injection()
    example_deterministic()
    example_stream()
    
    print("=" * 70)
    print("总结：MockProvider 的核心价值")
    print("=" * 70)
    print("[v] 离线测试 - 无需 API key")
    print("[v] 确定性 - 相同输入 -> 相同输出")
    print("[v] 可控失败 - 验证错误处理")
    print("[v] 快速执行 - 无网络延迟")
    print("=" * 70)
