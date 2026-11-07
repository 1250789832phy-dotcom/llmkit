# 实验1：理解 Message 类
from llmkit import Message

# 创建三种消息
sys_msg = Message.system("你是一个Python导师")
user_msg = Message.user("什么是装饰器？")
ai_msg = Message.assistant("装饰器是一种高阶函数...")

print("=== 实验1：Message 对象 ===")
print(f"系统消息: {sys_msg}")
print(f"用户消息: {user_msg}")
print(f"AI消息: {ai_msg}")
print(f"\n转成字典: {user_msg.to_dict()}")

# 实验2：理解 Usage
from llmkit import Usage

usage1 = Usage(prompt_tokens=100, completion_tokens=50)
usage2 = Usage(prompt_tokens=200, completion_tokens=80)

print("\n=== 实验2：Token 统计 ===")
print(f"第一次调用: {usage1.total_tokens} tokens")
print(f"第二次调用: {usage2.total_tokens} tokens")
print(f"总计: {(usage1 + usage2).total_tokens} tokens")

# 实验3：理解错误分类
from llmkit.errors import RateLimitError, AuthError, classify_http_error

print("\n=== 实验3：错误类型 ===")
rate_err = RateLimitError("请求过快")
auth_err = AuthError("API key 无效")

print(f"限流错误可重试？ {rate_err.retryable}")  # True
print(f"认证错误可重试？ {auth_err.retryable}")  # False

# 自动分类HTTP错误
err = classify_http_error(429, "Too many requests")
print(f"\n429错误类型: {type(err).__name__}")
print(f"是否可重试: {err.retryable}")
