from string import Template

SYSTEM_PROMPT_CAVFD = """You are a helpful software developer assistant specializing in vulnerability detection to help other developers understand characteristics of software patches and discover potential vulnerabilities."""
#你是一位专业的软件开发助手，专注于漏洞检测，帮助其他开发者理解软件补丁的特性并发现潜在的漏洞。
USER_PROMPT_CAVFD = Template(
    """You are given the following details for analysis:
1. **Patch Content:**
\"\"\"
${patch_content}
\"\"\" 

2. **Related Issue Report / Pull Request Summary:**
\"\"\"
${IRPR_content}
\"\"\"

3. **Three Aspect Analysis of the Patch:**
\"\"\"
${three_aspect_content}
\"\"\"

4. **Similar Historical Vulnerability Fix Information:**
\"\"\"
${history_vuln_content}
\"\"\"

5. **Three Aspect Analysis of the Historical Vulnerability Fix:**
\"\"\"
${history_three_aspect_content}
\"\"\"

**Task:**

1. **Comparison:** 
- Carefully compare the current patch with the historical vulnerability fix to avoid bias.
- Ensure that you consider the similarities and differences highlighted in the three aspect analyses.

2. **Analysis:**
- Use the information from the Related Issue Report / Pull Request Summary to understand the context and motivation behind the patch.
- Determine whether the current patch is intended to fix a vulnerability. You must provide evidence if you think its a vulnerability fix.

Your output should follow below syntax:
{
 "analysis": "<Detailed analysis of whether the patch is to fix a vulnerability>",
 "vulnerability_fix": "<yes or no>"
}
""")
# """  你被提供以下分析内容：
# 1. **补丁内容：**  ${patch_content}
# 2. **相关问题报告/拉取请求摘要：**  ${IRPR_content}
# 3. **补丁的三方面分析：**   ${three_aspect_content}
# 4. **类似历史漏洞修复信息：**   ${history_vuln_content}
# 5. **历史漏洞修复的三方面分析：**   ${history_three_aspect_content}
# **任务：**
# 1. **对比分析：**
# - 仔细比较当前补丁与历史漏洞修复，避免偏见。
# - 确保考虑三方面分析中强调的相似点和差异点。
# 2. **综合分析：**
# - 利用相关问题报告/拉取请求摘要中的信息，理解补丁的背景和动机。
# - 判断当前补丁是否旨在修复漏洞。若认为是漏洞修复，必须提供证据支持。
#
# 你的输出应遵循以下格式：
# {"analysis": "<详细分析该补丁是否用于修复漏洞>","vulnerability_fix": "<是或否>"}
SYSTEM_PROMPT_CCI = """You are a helpful software developer assistant specializing in software development lifecycle to help other developers understand characteristics of software patches."""
#你是一位专业的软件开发助手，专注于软件开发生命周期（SDLC），旨在帮助其他开发者理解软件补丁的特性。
USER_PROMPT_CCI = Template(
    """You are given the following software patch:
\"\"\"
${patch_content}
\"\"\"

Provide an analysis describing the following characteristics:
1. Code Change Summary
2. Purpose of the Change
3. Implications of the Change

Provide the analysis in bullet point format for each characteristic. Each bullet point should start with a key point and then briefly describe a main idea or fact from the text. Ensure each point is concise and captures the essence of the main idea it's summarizing.

Here is an example of the desired format:
\"\"\"
1. Code Change Summary
- [Key Point]: <description>
- [Optional Key Point]: <description>
- [Optional Key Point]: <description>

2. Purpose of the Change
- [Key Point]: <description>
- [Optional Key Point]: <description>
- [Optional Key Point]: <description>

3. Implications of the Change
- [Key Point]: <description>
- [Optional Key Point]: <description>
- [Optional Key Point]: <description>
\"\"\"
"""
)
# 给定以下软件补丁内容：${patch_content}
# 请按以下特性进行分析描述：代码变更摘要 变更目的 变更影响
# 采用分项列表格式呈现分析结果，每个要点需以核心观点开头并简要说明。保持表述简洁，突出核心内容。
#示例格式要求：
# 代码变更摘要
# [核心点]：<说明>
# [可选补充点]：<说明>
# 变更目的
# [核心点]：<说明>
# [可选补充点]：<说明>
# 变更影响
# [核心点]：<说明>
# [可选补充点]：<说明>