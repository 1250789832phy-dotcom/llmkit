"""示例 2：使用 OpenAI 兼容接口调用真实模型。

学习要点：
1. 支持所有 OpenAI 兼容的服务（DeepSeek、通义、Kimi 等）
2. 只需改 base_url 就能切换不同厂商
3. 自动重试 + 指数退避
4. 流式和非流式两种模式

使用前需要设置环境变量：
  Windows:  set LLM_API_KEY=sk-xxxxx
  Linux:    export LLM_API_KEY=sk-xxxxx
  
或者直接在代码中传入 api_key 参数（不推荐）
"""

import sys
from pathlib import Path

# 将 llmkit 加入路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from llmkit.client import LLMClient
from llmkit.providers.openai_compat import OpenAICompatProvider
from llmkit.types import Message
from llmkit.errors import ConfigError


def example_openai():
    """调用 OpenAI 官方接口"""
    print("=" * 70)
    print("示例 1: OpenAI 官方接口")
    print("=" * 70)
    
    try:
        # 默认 base_url 就是 OpenAI
        provider = OpenAICompatProvider()
        client = LLMClient(provider)
        
        messages = [
            Message(role="system", content="你是一个有帮助的助手"),
            Message(role="user", content="用一句话解释什么是 RESTful API"),
        ]
        
        response = client.complete(messages, model="gpt-3.5-turbo")
        
        print(f"模型: {response.model}")
        print(f"回复: {response.text}")
        print(f"用量: {response.usage.prompt_tokens} + {response.usage.completion_tokens} = {response.usage.total_tokens} tokens")
        print(f"延迟: {response.latency_ms}ms")
        print()
        
    except ConfigError as e:
        print(f"[配置错误] {e}")
        print("提示: 请先设置环境变量 LLM_API_KEY")
        print()


def example_deepseek():
    """调用 DeepSeek 接口"""
    print("=" * 70)
    print("示例 2: DeepSeek 接口")
    print("=" * 70)
    
    try:
        # 只需改 base_url
        provider = OpenAICompatProvider(
            base_url="https://api.deepseek.com/v1"
        )
        client = LLMClient(provider)
        
        messages = [Message(role="user", content="1+1=?")]
        response = client.complete(messages, model="deepseek-chat")
        
        print(f"模型: {response.model}")
        print(f"回复: {response.text}")
        print()
        
    except ConfigError as e:
        print(f"[配置错误] {e}")
        print()


def example_stream():
    """流式输出"""
    print("=" * 70)
    print("示例 3: 流式输出")
    print("=" * 70)
    
    try:
        provider = OpenAICompatProvider()
        client = LLMClient(provider)
        
        messages = [Message(role="user", content="数从1到5")]
        
        print("流式输出: ", end="", flush=True)
        for chunk in client.stream(messages, model="gpt-3.5-turbo"):
            print(chunk, end="", flush=True)
        print("\n")
        
    except ConfigError as e:
        print(f"[配置错误] {e}")
        print()


def example_custom_endpoint():
    """自定义端点（本地 vLLM / Ollama）"""
    print("=" * 70)
    print("示例 4: 自定义端点（本地模型）")
    print("=" * 70)
    
    # 假设你在本地运行了 vLLM 或 Ollama
    # vLLM: python -m vllm.entrypoints.openai.api_server --model xxx
    # Ollama: ollama serve
    
    print("本地模型示例（需要先启动服务）:")
    print()
    print("# vLLM")
    print("provider = OpenAICompatProvider(base_url='http://localhost:8000/v1')")
    print()
    print("# Ollama")
    print("provider = OpenAICompatProvider(base_url='http://localhost:11434/v1')")
    print()
    print("# LM Studio")
    print("provider = OpenAICompatProvider(base_url='http://localhost:1234/v1')")
    print()


def example_error_handling():
    """错误处理和重试"""
    print("=" * 70)
    print("示例 5: 错误处理")
    print("=" * 70)
    
    try:
        provider = OpenAICompatProvider()
        client = LLMClient(provider)
        
        messages = [Message(role="user", content="测试")]
        
        # 设置重试参数
        response = client.complete(
            messages, 
            model="gpt-3.5-turbo",
            retries=3,           # 最多重试 3 次
            backoff_base=0.5     # 退避基数 0.5s
        )
        print(f"成功: {response.text[:50]}...")
        print()
        
    except ConfigError as e:
        print(f"[配置错误] {e}")
        print()
    except Exception as e:
        print(f"[请求失败] {e}")
        print()


if __name__ == "__main__":
    print()
    print("=" * 70)
    print("OpenAI 兼容接口示例")
    print("=" * 70)
    print()
    print("支持的服务商（只需改 base_url）:")
    print("  - OpenAI:      https://api.openai.com/v1")
    print("  - DeepSeek:    https://api.deepseek.com/v1")
    print("  - 通义千问:     https://dashscope.aliyuncs.com/compatible-mode/v1")
    print("  - Kimi:        https://api.moonshot.cn/v1")
    print("  - 智谱:        https://open.bigmodel.cn/api/paas/v4")
    print("  - 本地 vLLM:   http://localhost:8000/v1")
    print("  - 本地 Ollama: http://localhost:11434/v1")
    print()
    
    example_openai()
    example_deepseek()
    example_stream()
    example_custom_endpoint()
    example_error_handling()
    
    print("=" * 70)
    print("总结：OpenAI 兼容接口的优势")
    print("=" * 70)
    print("[v] 一个适配器，横跨多个厂商")
    print("[v] 改 base_url 就能切换服务")
    print("[v] 支持流式和非流式")
    print("[v] 自动重试 + 指数退避")
    print("=" * 70)
