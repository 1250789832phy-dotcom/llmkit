# 🚀 LLMKit 5分钟快速上手

## 第一步：安装并验证

需要 Python 3.11 或更高版本。在克隆得到的 `llmkit` 仓库根目录、
选定的 Python 环境中执行以下命令，不要切换到原始学习项目目录：

```bash
python -m pip install -e . "httpx>=0.27"
python -c "from llmkit import LLMClient; print('✅ 安装成功！')"
```

Mock 不需要 API key，但当前 Provider 模块在导入时仍需要 `httpx`。
若要运行测试和覆盖率检查，改用 `python -m pip install -e ".[dev]"`。
后续命令也均在仓库根目录、同一个 Python 环境中执行。

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

先使用离线 Provider；真实 Provider 的配置留到第五步。

```python
from llmkit.providers.mock import MockProvider

# 离线测试用 Mock
provider = MockProvider()
```

### 3. Client - 统一客户端

下面是可独立运行的离线例子，不依赖前面代码块中的变量：

```python
from llmkit.client import LLMClient
from llmkit.providers.mock import MockProvider
from llmkit.types import Message

# 创建客户端
client = LLMClient(MockProvider())
messages = [Message(role="user", content="你好")]

# 发送请求
response = client.complete(messages, model="mock")
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

### 设置环境变量

在运行真实调用代码的同一个终端设置，不要提交真实密钥。

Windows PowerShell：

```powershell
$env:LLM_API_KEY = "replace-with-your-api-key"
```

Windows cmd：

```cmd
set "LLM_API_KEY=replace-with-your-api-key"
```

Linux / macOS：

```bash
export LLM_API_KEY="replace-with-your-api-key"
```

### 调用 OpenAI

以下代码会发起真实请求，可能产生费用。先确认 `LLM_API_KEY` 属于所选服务，
并检查当前终端的 `LLM_BASE_URL`：未显式传入 `base_url` 时，会优先采用
该变量的非空值，未设置时才使用默认地址。切换服务商时应同时核对地址、模型和密钥，
不要跨服务复用密钥。

```python
from llmkit.client import LLMClient
from llmkit.providers.openai_compat import OpenAICompatProvider
from llmkit.types import Message

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

- 📖 阅读 [README.md](../README.md) 了解完整功能
- 💻 运行 [examples/03_real_world.py](../examples/03_real_world.py) 查看实战场景
- 🧪 安装 `.[dev]` 后运行 `python -m pytest tests/ -v` 查看测试用例
- 📚 阅读 [SUMMARY.md](SUMMARY.md) 理解架构设计

## 问题排查

**Q: ModuleNotFoundError: No module named 'llmkit' 或 'httpx'**
```bash
# 在克隆的 llmkit 仓库根目录、运行代码的同一个 Python 环境中执行
python -m pip install -e . "httpx>=0.27"
```

**Q: Mock 输出总是一样的**
- 这是正常的！相同输入 → 相同输出（确定性）
- 使用非空队列，例如 `scripted=["第一次回复", "第二次回复"]`，可按调用顺序返回预设文本。
  空队列或队列耗尽后会回到默认的确定性回复，不会循环预设队列。

**Q: 真实 API 调用失败**
- 检查 LLM_API_KEY 是否设置
- 检查 base_url 是否正确
- 查看错误信息分类（RateLimitError、ServerError 等）

**Q: 如何查看更多示例**
```bash
# 示例 1: Mock 基础
python examples/01_mock_provider.py

# 示例 3: 实战场景
python examples/03_real_world.py
```

示例 2 会访问真实端点。不要设置真实密钥后直接运行整个
`examples/02_openai_compat.py`：它会依次执行多个示例，默认端点和显式指定的
DeepSeek 端点会复用 `LLM_API_KEY`。先按
[示例目录的安全运行说明](../examples/README.md) 核对配置并选择单个示例。

---

**🎉 恭喜！你已经掌握了 LLMKit 的基本使用！**

继续探索：
- [完整文档](../README.md)
- [架构详解](SUMMARY.md)
- [项目索引](INDEX.md)
