"""示例 3：实际应用场景 - 智能代码审查助手。

学习要点：
1. 多轮对话（保持上下文）
2. 流式输出（提升用户体验）
3. Token 统计（成本控制）
4. 错误处理（生产环境必备）
"""

import sys
from pathlib import Path

# 将 llmkit 加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message


def code_review_assistant():
    """代码审查助手"""
    print("=" * 70)
    print("智能代码审查助手")
    print("=" * 70)
    print()
    
    # 使用 MockProvider 演示（实际应用换成 OpenAICompatProvider）
    provider = MockProvider(scripted=[
        "这段代码有以下问题：\n1. 缺少错误处理\n2. 变量命名不规范\n3. 建议添加类型注解",
        "修改后的代码已经改进了：\n1. 添加了 try-except\n2. 使用了更清晰的命名\n3. 加入了类型提示",
        "这个实现很好！代码清晰、健壮，符合最佳实践。"
    ])
    client = LLMClient(provider)
    
    # 系统提示
    system_prompt = """你是一个专业的代码审查助手。
你的任务是：
1. 审查代码质量
2. 指出潜在问题
3. 提供改进建议
4. 保持专业和友好的语气"""
    
    # 初始化对话历史
    messages = [Message(role="system", content=system_prompt)]
    
    # 第一轮：提交代码
    code = """
def process(data):
    result = []
    for item in data:
        result.append(item * 2)
    return result
"""
    
    print("[用户] 请审查这段代码:")
    print(code)
    print()
    
    messages.append(Message(role="user", content=f"请审查这段代码:\n```python\n{code}\n```"))
    response = client.complete(messages, model="gpt-4")
    messages.append(Message(role="assistant", content=response.text))
    
    print("[助手]", response.text)
    print(f"[Token] 用量: {response.usage.total_tokens}")
    print()
    
    # 第二轮：提交修改后的代码
    improved_code = """
from typing import List

def process_items(data: List[int]) -> List[int]:
    '''处理数据，将每个元素乘以2'''
    try:
        result = [item * 2 for item in data]
        return result
    except TypeError as e:
        print(f"错误: 输入数据类型不正确 - {e}")
        return []
"""
    
    print("[用户] 我改进了代码，再看看:")
    print(improved_code)
    print()
    
    messages.append(Message(role="user", content=f"我改进了代码:\n```python\n{improved_code}\n```"))
    response = client.complete(messages, model="gpt-4")
    messages.append(Message(role="assistant", content=response.text))
    
    print("[助手]", response.text)
    print(f"[Token] 用量: {response.usage.total_tokens}")
    print()
    
    # 第三轮：询问最佳实践
    print("[用户] 还有其他最佳实践建议吗？")
    print()
    
    messages.append(Message(role="user", content="还有其他最佳实践建议吗？"))
    response = client.complete(messages, model="gpt-4")
    
    print("[助手]", response.text)
    print(f"[Token] 用量: {response.usage.total_tokens}")
    print()
    
    # 统计总用量
    total_messages = len(messages)
    print("=" * 70)
    print(f"对话统计:")
    print(f"  总消息数: {total_messages}")
    print(f"  最终 Token 用量: {response.usage.total_tokens}")
    print("=" * 70)


def streaming_chat():
    """流式聊天示例"""
    print()
    print("=" * 70)
    print("流式聊天（提升用户体验）")
    print("=" * 70)
    print()
    
    provider = MockProvider(scripted=[
        "Python 是一种高级编程语言，以其简洁的语法和强大的功能而闻名。它广泛应用于 Web 开发、数据科学、人工智能等领域。"
    ])
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="用一段话介绍 Python")]
    
    print("[用户] 用一段话介绍 Python")
    print()
    print("[助手] ", end="", flush=True)
    
    # 流式输出，字符逐个显示
    for chunk in client.stream(messages, model="gpt-4"):
        print(chunk, end="", flush=True)
    
    print("\n")
    print("[提示] 流式输出让用户感觉响应更快！")
    print()


def token_control():
    """Token 使用控制"""
    print("=" * 70)
    print("Token 使用控制（成本管理）")
    print("=" * 70)
    print()
    
    provider = MockProvider()
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="介绍一下机器学习")]
    
    # 限制输出长度
    print("[场景 1] 限制输出长度 max_tokens=50")
    response = client.complete(messages, model="gpt-4", max_tokens=50)
    print(f"回复: {response.text}")
    print(f"Token: {response.usage.completion_tokens}")
    print()
    
    print("[场景 2] 温度控制 temperature")
    print("  - temperature=0.0  → 确定性输出（适合代码生成）")
    print("  - temperature=0.7  → 平衡创造力（默认）")
    print("  - temperature=1.0  → 高创造力（适合创意写作）")
    print()


def error_handling_demo():
    """错误处理示例"""
    print("=" * 70)
    print("错误处理（生产环境必备）")
    print("=" * 70)
    print()
    
    from llmkit.errors import RateLimitError, ServerError, NetworkError
    
    # 模拟限流错误
    provider = MockProvider(fail_times=1, fail_with="rate_limit")
    client = LLMClient(provider)
    
    messages = [Message(role="user", content="测试")]
    
    try:
        print("[测试] 模拟限流错误...")
        response = client.complete(messages, model="mock", retries=2)
        print(f"[成功] 重试后成功: {response.text[:30]}...")
    except RateLimitError as e:
        print(f"[限流] {e}")
    except ServerError as e:
        print(f"[服务器错误] {e}")
    except NetworkError as e:
        print(f"[网络错误] {e}")
    
    print()


if __name__ == "__main__":
    print()
    print("=" * 70)
    print("实际应用场景演示")
    print("=" * 70)
    print()
    
    code_review_assistant()
    streaming_chat()
    token_control()
    error_handling_demo()
    
    print("=" * 70)
    print("总结：生产环境最佳实践")
    print("=" * 70)
    print("[v] 保持对话上下文 - 追加消息到列表")
    print("[v] 使用流式输出 - 提升用户体验")
    print("[v] 控制 Token 用量 - 管理成本")
    print("[v] 完善错误处理 - 提高稳定性")
    print("[v] 设置合理重试 - 应对网络波动")
    print("=" * 70)
