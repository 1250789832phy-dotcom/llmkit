# 🚀 LLMKit 5分钟快速上手

## 第一步：验证安装

```bash
cd "D:\agent 学习\projects\01-llm-client"
python -c "from llmkit import LLMClient; print('✅ 安装成功！')"
```

## 第二步：运行第一个示例（无需 API key）

```bash
python examples/01_mock_provider.py
```

**预期输出：**
```
======================================================================
示例 1: 基础 MockProvider
======================================================================
输入: 你好
输出: [mock:670d9743] 收到你的问题：你好
Token 用量: 15
```

## 第三步：理解核心概念（3 分钟）

### 1. Message - 消息结构
```python
from llmkit.types import Message

# 创建一条消息
msg = Message(role="user", content="你好")
```

### 2. Provider - 服务提供者
```python
from llmkit.providers.mock import MockProvider

# 离线测试用 Mock
provider = MockProvider()

# 真实调用用 OpenAI 兼容
from llmkit.providers.openai_compat import OpenAICompatProvider
provider = OpenAICompatProvider()  # 需要 LLM_API_KEY
```

### 3. Client - 统一客户端
```python
from llmkit.client import LLMClient

# 创建客户端
client = LLMClient(provider)

# 发送请求
response = client.complete(messages, model="gpt-3.5-turbo")
print(response.text)
```

## 第四步：三个实用模式

### 模式 1: 单次对话
```python
from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message

provider = MockProvider()
client = LLMClient(provider)

messages = [Message(role="user", content="1+1=?")]
response = client.complete(messages, model="mock")
print(response.text)
```

### 模式 2: 多轮对话
```python
messages = [
    Message(role="system", content="你是一个助手"),
]

# 第一轮
messages.append(Message(role="user", content="你好"))
response = client.complete(messages, model="mock")
messages.append(Message(role="assistant", content=response.text))

# 第二轮
messages.append(Message(role="user", content="天气怎么样"))
response = client.complete(messages, model="mock")
```

### 模式 3: 流式输出
```python
for chunk in client.stream(messages, model="mock"):
    print(chunk, end="", flush=True)
```

## 第五步：调用真实 API

### 设置环境变量（Windows）
```bash
set LLM_API_KEY=sk-your-api-key-here
```

### 调用 OpenAI
```python
from llmkit.providers.openai_compat import OpenAICompatProvider

provider = OpenAICompatProvider()
client = LLMClient(provider)

messages = [Message(role="user", content="你好")]
response = client.complete(messages, model="gpt-3.5-turbo")
print(response.text)
```

### 切换到其他服务商
```python
# DeepSeek
provider = OpenAICompatProvider(
    base_url="https://api.deepseek.com/v1"
)

# 通义千问
provider = OpenAICompatProvider(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
```

## 常用参数

### 重试控制
```python
response = client.complete(
    messages,
    model="gpt-3.5-turbo",
    retries=3,           # 最多重试 3 次
    backoff_base=0.5     # 退避基数
)
```

### Token 控制
```python
response = client.complete(
    messages,
    model="gpt-3.5-turbo",
    max_tokens=100,      # 限制长度
    temperature=0.7      # 控制随机性
)

print(f"用了 {response.usage.total_tokens} 个 token")
```

## 下一步

- 📖 阅读 [README.md](README.md) 了解完整功能
- 💻 运行 [examples/03_real_world.py](examples/03_real_world.py) 查看实战场景
- 🧪 运行 `pytest tests/ -v` 查看测试用例
- 📚 阅读 [SUMMARY.md](SUMMARY.md) 理解架构设计

## 问题排查

**Q: ImportError: No module named 'llmkit'**
```bash
# 在项目根目录运行
cd "D:\agent 学习\projects\01-llm-client"
pip install -e .
```

**Q: Mock 输出总是一样的**
- 这是正常的！相同输入 → 相同输出（确定性）
- 使用 `scripted=[]` 参数可以预设不同回复

**Q: 真实 API 调用失败**
- 检查 LLM_API_KEY 是否设置
- 检查 base_url 是否正确
- 查看错误信息分类（RateLimitError、ServerError 等）

**Q: 如何查看更多示例**
```bash
# 示例 1: Mock 基础
python examples/01_mock_provider.py

# 示例 2: OpenAI 兼容
python examples/02_openai_compat.py

# 示例 3: 实战场景
python examples/03_real_world.py
```

---

**🎉 恭喜！你已经掌握了 LLMKit 的基本使用！**

继续探索：
- [完整文档](README.md)
- [架构详解](SUMMARY.md)
- [项目索引](INDEX.md)
