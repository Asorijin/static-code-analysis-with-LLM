## 环境配置

### 使用 uv

```bash
# 安装 uv（如果没有）
pip install uv

# 创建虚拟环境并安装依赖
uv sync

# 运行python文件
uv run xxx.py
# 或者
.venv/Script/activate
python xxx.py

# 添加依赖
uv add package_name
```
