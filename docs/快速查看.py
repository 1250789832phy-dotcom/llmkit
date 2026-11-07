# 快速查看工具
# 用法：python 快速查看.py types

import sys
import os

# Windows控制台编码设置
if os.name == 'nt':
    os.system('chcp 65001 > nul')

files = {
    "types": "llmkit/types.py",
    "errors": "llmkit/errors.py",
    "base": "llmkit/providers/base.py",
    "mock": "llmkit/providers/mock.py",
    "openai": "llmkit/providers/openai_compat.py",
    "client": "llmkit/client.py",
}

if len(sys.argv) < 2:
    print("可用文件：")
    for name, path in files.items():
        with open(path, encoding="utf-8") as f:
            lines = len(f.readlines())
        print(f"  - {name:10s} -> {path:35s} ({lines} 行)")
    print("\n用法：python 快速查看.py types")
    sys.exit(0)

name = sys.argv[1]
if name not in files:
    print(f"找不到文件：{name}")
    print(f"可用：{', '.join(files.keys())}")
    sys.exit(1)

path = files[name]
print(f"\n文件：{path}")
print("=" * 70)

with open(path, encoding="utf-8") as f:
    lines = f.readlines()
    
print(f"总行数：{len(lines)}\n")

for i, line in enumerate(lines, 1):
    print(f"{i:3d} | {line}", end="")
