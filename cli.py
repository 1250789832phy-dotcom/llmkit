"""命令行工具。

学习要点：这是一个完整的"前端"层，展示怎么串起 provider → client → UI。
"""

from __future__ import annotations

import sys
from collections.abc import Sequence

from llmkit import LLMClient, Message
from llmkit.providers import MockProvider, OpenAICompatProvider


def main(argv: Sequence[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if not argv or "--help" in argv:
        print(
            """用法:
  python cli.py --mock "你的问题"            # 用离线 mock 测试
  python cli.py --openai "你的问题"         # 真实调用(需要 LLM_API_KEY 环境变量)
  python cli.py --openai --stream "问题"    # 流式调用

环境变量:
  LLM_API_KEY        模型 API key
  LLM_BASE_URL       API 端点，默认 https://api.openai.com/v1
  LLM_MODEL          默认模型，默认 gpt-4o-mini
"""
        )
        return 0

    import os

    use_mock = "--mock" in argv
    use_stream = "--stream" in argv
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    prompt_start = 0
    for i, arg in enumerate(argv):
        if not arg.startswith("--"):
            prompt_start = i
            break
    if prompt_start == 0:
        print("错误：缺少提示词", file=sys.stderr)
        return 1

    prompt = " ".join(argv[prompt_start:])
    messages = [Message.user(prompt)]

    if use_mock:
        provider = MockProvider(
            scripted=[f"[离线模式] 你问的是：{prompt}\n这是确定性回复，方便测试。"]
        )
    else:
        try:
            provider = OpenAICompatProvider()
        except Exception as exc:
            print(f"配置错误: {exc}", file=sys.stderr)
            return 1

    client = LLMClient(provider)
    try:
        if use_stream:
            print(">>> 流式输出:\n", flush=True)
            for chunk in client.stream(messages, model=model):
                print(chunk, end="", flush=True)
            print("\n")
        else:
            print(">>> 一次性输出:\n", flush=True)
            response = client.complete(messages, model=model)
            print(response.text)
            print(
                f"\n[用量] prompt={response.usage.prompt_tokens} "
                f"completion={response.usage.completion_tokens} "
                f"total={response.usage.total_tokens} "
                f"耗时={response.latency_ms}ms"
            )
    except Exception as exc:
        print(f"调用失败: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())