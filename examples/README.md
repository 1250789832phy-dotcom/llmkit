# 实战演示示例

本目录包含了 `llmkit` 的实际使用示例，从基础到实战应用。

## 📁 示例列表

### 1. MockProvider 基础演示 (`01_mock_provider.py`)

**学习内容：**
- 离线测试，无需 API key
- 确定性输出，适合单元测试
- 失败注入，验证重试逻辑
- 流式输出模拟

**运行：**
```bash
python examples/01_mock_provider.py
```

**适用场景：**
- 开发阶段的本地测试
- 编写单元测试
- 验证错误处理逻辑
- CI/CD 流水线

---

### 2. OpenAI 兼容接口 (`02_openai_compat.py`)

**学习内容：**
- 调用真实的 LLM 服务
- 支持多个厂商（OpenAI、DeepSeek、通义等）
- 自动重试 + 指数退避
- 流式和非流式两种模式

**配置：**
```bash
# Windows
set LLM_API_KEY=sk-xxxxx

# Linux/Mac
export LLM_API_KEY=sk-xxxxx
```

**运行：**
```bash
python examples/02_openai_compat.py
```

**支持的服务商：**
- OpenAI: `https://api.openai.com/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- 通义千问: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- Kimi: `https://api.moonshot.cn/v1`
- 智谱: `https://open.bigmodel.cn/api/paas/v4`
- 本地 vLLM: `http://localhost:8000/v1`
- 本地 Ollama: `http://localhost:11434/v1`

---

### 3. 实际应用场景 (`03_real_world.py`)

**学习内容：**
- 多轮对话（代码审查助手）
- 流式输出提升用户体验
- Token 统计和成本控制
- 生产环境错误处理

**运行：**
```bash
python examples/03_real_world.py
```

**应用场景：**
- 智能客服系统
- 代码审查工具
- 内容生成平台
- 教育辅助系统

---

## 🎯 快速开始

### 1. 离线测试（无需 API key）

```python
from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message

provider = MockProvider()
client = LLMClient(provider)

messages = [Message(role="user", content="你好")]
response = client.complete(messages, model="mock")

print(response.text)
```

### 2. 调用真实 API

```python
from llmkit.client import LLMClient
from llmkit.providers.openai_compat import OpenAICompatProvider
from llmkit.types import Message

# 方式 1: 使用环境变量 LLM_API_KEY
provider = OpenAICompatProvider()

# 方式 2: 直接传入（不推荐）
# provider = OpenAICompatProvider(api_key="sk-xxxxx")

client = LLMClient(provider)

messages = [Message(role="user", content="1+1=?")]
response = client.complete(messages, model="gpt-3.5-turbo")

print(response.text)
```

### 3. 切换服务商（只需改 base_url）

```python
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

### 4. 流式输出

```python
messages = [Message(role="user", content="讲个故事")]

for chunk in client.stream(messages, model="gpt-3.5-turbo"):
    print(chunk, end="", flush=True)
```

### 5. 多轮对话

```python
messages = [
    Message(role="system", content="你是一个助手"),
    Message(role="user", content="你好"),
]

response = client.complete(messages, model="gpt-3.5-turbo")

# 追加助手回复
messages.append(Message(role="assistant", content=response.text))

# 继续对话
messages.append(Message(role="user", content="天气怎么样？"))
response = client.complete(messages, model="gpt-3.5-turbo")
```

---

## 🔧 高级用法

### 重试和退避

```python
response = client.complete(
    messages, 
    model="gpt-3.5-turbo",
    retries=3,           # 最多重试 3 次
    backoff_base=0.5     # 退避基数 0.5 秒
)
```

### Token 控制

```python
response = client.complete(
    messages,
    model="gpt-3.5-turbo",
    max_tokens=100,      # 限制输出长度
    temperature=0.7      # 控制随机性
)

print(f"输入: {response.usage.prompt_tokens}")
print(f"输出: {response.usage.completion_tokens}")
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

---

## 💡 最佳实践

1. **开发环境使用 MockProvider**
   - 快速迭代，无需消耗 API 额度
   - 确定性输出，便于调试

2. **生产环境配置重试**
   - 设置合理的 retries 和 backoff_base
   - 应对网络波动和服务端限流

3. **使用流式输出**
   - 提升用户体验，降低等待感
   - 适合长文本生成场景

4. **监控 Token 用量**
   - 定期统计，控制成本
   - 对超长对话进行截断或总结

5. **完善错误处理**
   - 区分不同错误类型
   - 提供友好的错误提示

---

## 📚 相关文档

- [项目主 README](../README.md)
- [API 文档](../docs/api.md)
- [架构设计](../docs/architecture.md)

---

## 🤝 贡献

欢迎提交更多实用示例！请确保：
- 代码清晰，注释充分
- 包含实际运行结果
- 遵循项目代码规范
