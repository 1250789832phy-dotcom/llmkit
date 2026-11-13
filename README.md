# LLMKit - 简洁统一的 LLM 客户端库
[![CI](https://github.com/1250789832phy-dotcom/llmkit/actions/workflows/ci.yml/badge.svg)](https://github.com/1250789832phy-dotcom/llmkit/actions/workflows/ci.yml)


一个轻量级、可扩展的 Python LLM 客户端库，提供统一接口调用不同的大语言模型服务。

## ✨ 核心特性

- **统一接口** - 一套 API，适配多个厂商（OpenAI、DeepSeek、通义千问等）
- **离线测试** - 内置 MockProvider，无需 API key 即可开发和测试
- **自动重试** - 指数退避重试机制，应对网络波动和限流
- **流式支持** - 支持流式和非流式两种输出模式
- **类型安全** - 完整的类型注解，IDE 友好
- **轻量依赖** - HTTP 请求使用 `httpx`；离线 Mock 无需 API key

## 🚀 快速开始

### 安装

```bash
# 克隆仓库
git clone https://github.com/1250789832phy-dotcom/llmkit.git
cd llmkit

# 安装库及当前代码需要的 HTTP 依赖
python -m pip install -e . "httpx>=0.27"

# 开发与测试（包含 pytest 和 httpx）
python -m pip install -e ".[dev]"
```

当前打包配置未声明运行时依赖，但 Provider 模块会在导入时加载 `httpx`，
因此仅执行 `pip install -e .` 不足以正常使用库，使用 MockProvider 也需要安装 `httpx`。
Python 版本要求为 3.11 或更高。

### 基础使用

```python
from llmkit.client import LLMClient
from llmkit.providers.openai_compat import OpenAICompatProvider
from llmkit.types import Message

# 1. 创建 Provider
provider = OpenAICompatProvider()  # 读取环境变量 LLM_API_KEY

# 2. 创建 Client
client = LLMClient(provider)

# 3. 发送请求
messages = [Message(role="user", content="1+1=?")]
response = client.complete(messages, model="gpt-3.5-turbo")

print(response.text)
print(f"Token 用量: {response.usage.total_tokens}")
```

### 离线测试（无需 API key）

```python
from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message

# 使用 MockProvider 进行离线开发
provider = MockProvider()
client = LLMClient(provider)

messages = [Message(role="user", content="你好")]
response = client.complete(messages, model="mock")

print(response.text)  # [mock:xxxxx] 收到你的问题：你好
```

## 📖 详细示例

查看 [`examples/`](./examples/) 目录获取完整示例：

1. **[01_mock_provider.py](./examples/01_mock_provider.py)** - MockProvider 基础演示
2. **[02_openai_compat.py](./examples/02_openai_compat.py)** - OpenAI 兼容接口
3. **[03_real_world.py](./examples/03_real_world.py)** - 实际应用场景

## 🎯 核心概念

### 架构设计

```
┌─────────────┐
│   Client    │  高层封装：重试、错误处理、流式支持
└──────┬──────┘
       │
┌──────┴───────┐
│   Provider   │  适配器接口：统一不同厂商的 API
└──────┬───────┘
       │
  ┌────┴────┬──────────┐
  │         │          │
┌─┴──┐  ┌──┴───┐  ┌───┴────┐
│Mock│  │OpenAI│  │Custom  │  具体实现
└────┘  └──────┘  └────────┘
```

### 三层设计

1. **Client 层** - 业务逻辑
   - 自动重试 + 指数退避
   - 流式/非流式统一接口
   - 错误分类和处理

2. **Provider 层** - 适配器
   - 统一接口定义
   - 厂商特定实现
   - 请求/响应转换

3. **Types 层** - 数据类型
   - 强类型消息结构
   - 响应对象封装
   - 错误类型定义

## 🔌 支持的服务

### OpenAI 兼容接口

只需改 `base_url` 即可切换不同厂商：

```python
# OpenAI 官方
provider = OpenAICompatProvider()

# DeepSeek
provider = OpenAICompatProvider(
    base_url="https://api.deepseek.com/v1"
)

# 通义千问
provider = OpenAICompatProvider(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# 本地 Ollama
provider = OpenAICompatProvider(
    base_url="http://localhost:11434/v1"
)
```

### 支持列表

| 服务商 | base_url | 模型示例 |
|--------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | `gpt-3.5-turbo`, `gpt-4` |
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-turbo` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 智谱 | `https://open.bigmodel.cn/api/paas/v4` | `glm-4` |
| vLLM | `http://localhost:8000/v1` | 自定义 |
| Ollama | `http://localhost:11434/v1` | `llama2`, `mistral` |

## 🛠️ 高级功能

### 重试和退避

```python
response = client.complete(
    messages,
    model="gpt-3.5-turbo",
    retries=3,           # 最多重试 3 次
    backoff_base=0.5     # 退避基数 0.5 秒
)
# 退避间隔: 0.5s, 1.0s, 2.0s
```

`retries` 表示首次调用之后允许的重试次数。自动重试仅适用于
`complete()`；`stream()` 直接返回 Provider 的流，不会自动重试，
流式连接失败时请由业务层决定是否重新建立连接。

### 流式输出

```python
for chunk in client.stream(messages, model="gpt-3.5-turbo"):
    print(chunk, end="", flush=True)
```

### 多轮对话

```python
messages = [
    Message(role="system", content="你是一个助手"),
]

# 第一轮
messages.append(Message(role="user", content="你好"))
response = client.complete(messages, model="gpt-3.5-turbo")
messages.append(Message(role="assistant", content=response.text))

# 第二轮
messages.append(Message(role="user", content="天气怎么样？"))
response = client.complete(messages, model="gpt-3.5-turbo")
```

### Token 控制

```python
response = client.complete(
    messages,
    model="gpt-3.5-turbo",
    max_tokens=100,      # 限制输出长度
    temperature=0.7      # 控制随机性 (0.0-2.0)
)

print(f"输入 Token: {response.usage.prompt_tokens}")
print(f"输出 Token: {response.usage.completion_tokens}")
print(f"总计: {response.usage.total_tokens}")
```

### 错误处理

```python
from llmkit.errors import RateLimitError, ServerError, NetworkError

try:
    response = client.complete(messages, model="gpt-3.5-turbo")
except RateLimitError:
    print("限流了，稍后重试")
except ServerError:
    print("服务器错误")
except NetworkError:
    print("网络问题")
```

## 📚 项目结构

```
llmkit/
├── llmkit/              # 核心库
│   ├── __init__.py
│   ├── client.py        # Client 实现
│   ├── types.py         # 数据类型定义
│   ├── errors.py        # 错误类型
│   └── providers/       # Provider 实现
│       ├── __init__.py
│       ├── base.py      # Provider 接口
│       ├── mock.py      # Mock 实现
│       └── openai_compat.py  # OpenAI 兼容实现
├── tests/               # 测试用例
│   ├── conftest.py
│   ├── test_client_retry.py
│   └── test_mock_provider.py
├── examples/            # 示例代码
│   ├── README.md
│   ├── 01_mock_provider.py
│   ├── 02_openai_compat.py
│   └── 03_real_world.py
├── cli.py                # 命令行入口
├── docs/                # 过程文档
├── LICENSE
├── pyproject.toml
└── README.md           # 本文件
```

## 🧪 测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_mock_provider.py -v

# 查看覆盖率（`.[dev]` 已包含 pytest-cov）
python -m pytest --cov=llmkit tests/
```

## 💡 设计理念

1. **简洁优于复杂**
   - 最小化依赖
   - 清晰的 API 设计
   - 易于理解和扩展

2. **实用优于完美**
   - 优先支持常见场景
   - 保持灵活性
   - 逐步迭代改进

3. **可测试性**
   - MockProvider 支持离线测试
   - 确定性输出
   - 完整的单元测试

4. **可扩展性**
   - Provider 接口易于实现
   - 支持自定义 Provider
   - 插件式架构

## 🔮 未来计划

- [ ] 异步支持 (async/await)
- [ ] 更多 Provider 实现（Claude、Gemini 等）
- [ ] 内置对话管理（自动截断、总结）
- [ ] 函数调用 (Function Calling) 支持
- [ ] 批量请求优化
- [ ] 缓存机制

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 提交 Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

本项目参考了以下优秀项目的设计：
- OpenAI Python SDK
- LangChain
- LiteLLM

---

**Made with ❤️ for AI developers**
