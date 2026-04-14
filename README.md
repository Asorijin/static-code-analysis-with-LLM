## 系统概述

本项目是一个基于RAG（检索增强生成）和LLM的代码漏洞检测系统，通过历史漏洞模式匹配和多维度分析来识别代码中的潜在安全问题。

### 核心组件

1. **CCI (Code Change/Content Intent)**: 分析代码的三个维度
   - Code Change/Content Summary（代码变更/内容摘要）
   - Purpose of the Change（变更目的）
   - Implications of the Change（变更影响）

2. **HV (Historical Vulnerabilities)**: 历史漏洞向量数据库
   - 存储已知CVE漏洞及其CCI分析
   - 通过NVD API获取CVE描述信息
   - 支持向量相似度检索

3. **SA (Static Analysis)**: 静态代码分析
   - 检测语法错误、逻辑错误、安全漏洞
   - 结合RAG上下文进行模式匹配
   - 输出结构化的问题报告

4. **CAVFD (Code Analysis and Vulnerability Fix Detection)**: 漏洞修复判断
   - 对比当前代码与历史漏洞模式
   - 判断代码是否包含或修复漏洞
   - 提供详细分析依据

### 整体执行流程

#### 阶段一：构建历史漏洞数据库 (my_build_rag.py)

1. 读取包含历史漏洞的parquet文件
2. 通过NVD API查询CVE描述信息
3. 对每个漏洞patch生成CCI三维度分析
4. 将CCI分析结果向量化（使用Qwen Embedding）
5. 存储到ChromaDB向量数据库
6. 支持多线程并行处理以提高效率

#### 阶段二：代码漏洞检测 (my_main.py)

1. **代码提取**: 从diff/patch中提取纯代码内容
2. **CCI生成**: 对待检测代码生成三维度分析
3. **RAG检索**: 在向量数据库中查找最相似的历史漏洞
4. **静态分析 (SA)**: 
   - 结合历史漏洞模式进行全面静态分析
   - 检测代码质量问题和安全漏洞
5. **漏洞判断 (CAVFD)**:
   - 对比当前代码与历史漏洞的CCI分析
   - 判断是否存在或修复漏洞
6. **结果输出**: 合并SA和CAVFD结果为JSON格式

#### 阶段三：质量检查 (check_point)

- 基于真实标签评估检测准确性
- 输出性能指标

## 项目结构

- **my_main.py**: 主程序，执行完整的漏洞检测流程
  - 代码提取与预处理
  - CCI分析生成
  - RAG检索历史漏洞
  - 静态分析 (SA)
  - 漏洞修复判断 (CAVFD)
  - 多线程并行处理

- **my_build_rag.py**: 构建历史漏洞向量数据库
  - 从NVD API获取CVE信息
  - 生成漏洞patch的CCI分析
  - 向量化并存储到ChromaDB
  - 支持多线程加速

- **prompts.py**: LLM提示词模板
  - `SYSTEM_PROMPT_SA` / `USER_PROMPT_SA`: 静态分析提示词
  - `SYSTEM_PROMPT_CCI` / `USER_PROMPT_CCI`: CCI分析提示词（分析patch）
  - `SYSTEM_PROMPT_CCI_CODE` / `USER_PROMPT_CCI_CODE`: CCI分析提示词（分析代码）
  - `SYSTEM_PROMPT_CAVFD` / `USER_PROMPT_CAVFD`: 漏洞判断提示词（分析patch）
  - `SYSTEM_PROMPT_CAVFD_CODE` / `USER_PROMPT_CAVFD_CODE`: 漏洞判断提示词（分析代码）

- **utils.py**: 工具函数
  - DashScope API初始化
  - LLM推理接口
  - Qwen Embedding生成
  - ChromaDB客户端管理
  - CCI/SA/CAVFD生成函数

- **config.py**: 配置文件
  - API密钥和URL配置
  - 数据集路径配置
  - ChromaDB配置

- **check_point.py**: 质量检查与指标评估

### 语言支持

目前默认支持Java语言。如需更换识别语言，建议同步更换数据集语言以获得最佳效果。

---

## 数据格式要求

### my_build_rag.py 输入数据格式

输入parquet文件必需包含以下列：

| 列名        | 类型   | 是否必需 | 说明 |
|-------------|--------|--------|------|
| `vuln_id`   | str    | ✅ 是   | CVE 编号（如 CVE-2024-1234），用于从NVD API查询漏洞描述 |
| `patch`     | str    | ✅ 是   | 漏洞修复的补丁内容（diff/patch格式文本） |
| `lang`      | str    | ✅ 是   | 编程语言标识（如 "Java"），存储在metadata中 |

**输出文件**:
- `without_embedding_leak_new.parquet`: 包含CCI分析和CVE信息，未向量化
- `fin_leak.parquet` / `Config.RAG_OUTPUT_PARQUET`: 完整的向量化数据，包含 `3aspect_embedding` 列
- ChromaDB数据库: 存储在 `Config.CHROMA_DB_PATH`

**处理流程**:
1. 读取输入parquet → 2. 多线程生成CCI分析 → 3. 查询NVD获取CVE描述 → 4. 多线程向量化 → 5. 写入ChromaDB

---

### my_main.py 输入数据格式

输入Excel文件 (`Config.TEST_DATASET`) 必需包含以下列：

| 列名     | 类型   | 是否必需 | 说明 |
|--------|------|--------|------|
| `patch` | str  | ✅ 是   | 待检测的代码补丁（diff/patch格式）或代码片段 |

**输出文件**:
- `Config.OUTPUT_CSV`: CSV格式，新增 `cavfd` 列，包含JSON格式的检测结果
  ```json
  {
    "static_analysis": {
      "has_issues": true/false,
      "issues": [...],
      "summary": "..."
    },
    "vulnerability_fix": {
      "analysis": "...",
      "vulnerability_fix": "yes/no"
    }
  }
  ```

**处理流程**:
1. 读取Excel → 2. 提取代码 → 3. 生成CCI → 4. RAG检索 → 5. 静态分析 → 6. 漏洞判断 → 7. 输出CSV

---

### check_point.py 输入数据格式

输入数据必需包含以下列：

| 列名    | 类型       | 说明 |
|--------|-----------|------|
| `label` | int | 真实标签（ground truth）：<br> - `1` 表示该样本确实存在漏洞（正例）<br> - `0` 表示无漏洞（负例） |
| `cavfd` | str | my_main.py输出的检测结果（JSON格式） |

**输出**: 准确率、精确率、召回率、F1分数等评估指标