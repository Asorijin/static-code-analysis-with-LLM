# Assignment 1

截止 4月20日 12:00 | 满分 40 分

---

## 要求

本作业要求学生使用AI方法（如LLM）设计并实现（或改进）一种测试技术。学生可选择以下三种测试技术之一：

- **静态测试**
- **黑盒动态测试**
- **白盒动态测试**

> 注：静态代码分析工具列表请参阅 [[链接](https://en.wikipedia.org/wiki/List_of_tools_for_static_code_analysis)]。黑盒测试技术包括：等价划分（EP）、边界值分析（BVA）、输入组合测试、状态转换测试模型生成器、决策表测试。白盒测试可测量语句覆盖、分支覆盖、条件覆盖、路径覆盖、D-U覆盖等。

### 工具输入形式

作业要求实现为一个工具，支持两种输入形式之一：

1. 系统的需求（requirements）
2. 待测代码库（testing codebase）

动态测试工具应能分析以下内容之一来生成测试用例：

- 系统需求
- 待测代码库（或部分模块）

---

## 提交物

| 内容 | 说明 |
|------|------|
| **输入** | 需求文档 / 项目代码库 |
| **工具产物** | 使用的提示词、使用的模型、模型生成的代码 |
| **生成输出** | 静态分析的报警信息；黑盒/白盒分析的测试用例 |
| **实验分析** | 准确性、覆盖率、可泛化性等 |
| **项目报告** | 与传统非AI技术的对比、优缺点分析 |
| **分析报告** | 实践中遇到的AI局限性及改进方法 |
| **总结** | 项目总结 |

---

## 评估标准

| 维度 | 比例 |
|------|------|
| 概念理解 | 10% |
| 设计与实现的一致性 | 20% |
| 覆盖率和有效性/实用性 | 40% |
| 深入分析（可泛化性论证、推理等） | 20% |
| 演示汇报 | 10% |

---

## 演示要求

每组有 **15分钟** 进行项目演示（英文），需涵盖上述所有内容，随后进行问答环节。评审老师将根据提交的文档、演示内容及软件测试基础知识进行提问。

组成员贡献默认均分，如有特殊情况需单独申请并由所有成员签字确认。

### 提交方式

各组需在演示日期前一天通过邮件向助教提交以下材料：

a) **提交物压缩包**：包含上述所有要求内容（封面需包含团队ID、所有成员姓名及学号）
b) **最终演示PPT**：第一页需包含团队ID、所有成员姓名及学号

**格式要求**：
- 报告和PPT需提交PDF格式
- 测试脚本需提交压缩文件

### 时间安排

- **提交截止**：第八周周一 17:00前
- **演示日期**：第八至九周 周二/周四 10:00-11:35

---

## 示例提交 1

**标题**：LLM-based Dynamic Black-box Testing for Multi-Item Smart Vending Machine

### 输入

**系统概述**：待测系统是一台部署在公共场所（如地铁站）的智能售货机。测试者无法看到内部软件、硬件控制逻辑和数据库，仅根据提供的需求从外部可观察行为进行测试。

**功能需求**：

- **商品选择**：售货机提供三类产品——饮料（价格：$1.50, $3.00）；零食（价格：$2.00, $4.50）；热食（价格：$5.00, $10.00）
- **支付方式**：硬币（$0.10, $0.25, $0.50, $1.00）；纸币（$5.00, $10.00）
- **支付约束**：投入金额必须大于等于商品价格；找零上限$5.00；超过$5.00找零的交易将被拒绝
- **库存约束**：支付过程中商品可能售罄

### 工具产物

**使用的LLM**：GPT-4o

**使用的提示词**：

```
You are a software testing assistant. Given the following system overview and requirement, identify:
1) Input variables 2) Equivalence partitions (valid and invalid) 3) Boundary values 4) Concrete test cases

Requirement: {requirement_text}
```

### 生成输出

**等价划分**：

| ID | 描述 | 结果 |
|----|------|------|
| EP1 | 投入金额 < 商品价格 | valid |
| EP2 | 投入金额 > 商品价格 | invalid |
| ... | ... | ... |

**边界值分析**：

| 边界 | 值 |
|------|-----|
| 商品价格 | $1.4, $1.5, $1.6 |
| 支付总额 | $0, $1.4, $15.1 |
| ... | ... |

**测试用例示例**：

| 测试用例 | 场景 | 预期结果 |
|---------|------|---------|
| TC1 | 零食$3.00，支付$8.50 | 拒绝（找零>$5） |
| TC2 | 零食$3.00，支付$3.50 | 支付成功，找零$0.50 |
| ... | ... | ... |

### 实验分析

4.1 EP/BVA及测试用例覆盖率

4.2 商品售罄分析

4.3 优化提示词以提高覆盖率、准确性和可泛化性

### 项目报告

- 与传统非AI技术的对比、优缺点
- 分析报告：AI的局限性及改进方法
- 总结

---

## 示例提交 2

**标题**：LLM-based Static Analysis

### 输入

**系统概述**：

Axios是一个基于Promise的网络请求库，可运行于Node.js和浏览器。该库改编自原始Axios v1.3.4版本，以兼容OpenHarmony，同时保留其现有使用模式和功能。

- HTTP请求
- Promise API
- 请求和响应拦截器
- 请求和响应数据转换
- 自动转换JSON数据

源代码获取地址：https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios

### 工具产物

**提示词示例**：

```
You are a static code analyzer. Analyze the following {language} code and detect potential issues.
Identify the following:
- Syntax errors
- Security vulnerabilities
- Deprecated or incompatible API usage
- Potential runtime errors
- Code quality issues
Return the results in structured JSON format:
{
  "issues": [
    {
      "line": <line_number>,
      "type": "<issue_type>",
      "description": "<detailed description>",
      "severity": "<low/medium/high>"
    }
  ]
}
Code: {source_code}
```

### 生成输出

**问题1**：
```json
{
  "line": 4,
  "type": "Resource Management",
  "description": "File opened using 'open' but not managed with a context manager. If an exception occurs, the file may remain open.",
  "severity": "medium",
  "recommendation": "Use 'with open(filename, 'r') as f:' to automatically close the file.",
  "category": "Code Quality",
  "reference": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files"
}
```

**测试用例（概念验证）**：...

### 实验分析

4.1 误报分析

4.2 优化提示词以提高准确性

4.3 尝试更多项目以提高可泛化性

4.4 向开发者报告并验证Bug

### 项目报告

- 与传统非AI技术的对比、优缺点
- 分析报告：AI的局限性及改进方法
- 总结

---

## 示例提交 3

**标题**：LLM-based White-box Testing

### 输入

**系统概述**：

Axios是一个基于Promise的网络请求库，可运行于Node.js和浏览器。该库改编自原始Axios v1.3.4版本，以兼容OpenHarmony，同时保留其现有使用模式和功能。

- HTTP请求
- Promise API
- 请求和响应拦截器
- 请求和响应数据转换
- 自动转换JSON数据

源代码获取地址：https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Faxios

### 工具产物

**提示词**：

```
You are an expert software tester and white-box testing assistant.
Your task is to analyze the following {language} function/module and generate a set of test cases that achieve **full statement coverage**.

Please do the following:
1. Identify all executable statements in the code.
2. For each statement, generate test input values that will execute it at least once.
3. Output the test cases in a **structured JSON format** suitable for automated testing.

Structured JSON format:
{
  "function": "<function_name>",
  "test_cases": [
    {
      "input": { "<parameter_name>": <value>, ... },
      "expected_output": "<expected output or behavior>",
      "covered_statements": [<line_numbers>],
      "notes": "<optional explanation>"
    }
  ]
}

Code to analyze: {code_snippet}

Notes:
- Include edge cases if necessary to cover all branches of conditional statements.
- If a statement is unreachable due to a logic error, mark it as "unreachable".
- Provide explanations for how each test case achieves statement coverage.
```

### 生成输出

**测试函数**：...

**测试用例**：

- TestCase1: 删除指定文件
- TestCase2: 异常处理

### 实验分析

4.1 误报分析

4.2 优化提示词以提高准确性

4.3 尝试更多项目以提高可泛化性

4.4 向开发者报告并验证Bug

### 项目报告

- 与传统非AI技术的对比、优缺点
- 分析报告：AI的局限性及改进方法
- 总结
