from string import Template

# ============================================================
# 静态代码分析 prompts
# ============================================================

SYSTEM_PROMPT_SA = """You are an expert static code analysis assistant. You analyze source code to identify bugs, security vulnerabilities, logic errors, syntax errors, and potential issues. Provide clear, actionable feedback."""

USER_PROMPT_SA = Template(
    """You are given the following code for comprehensive static analysis:
${code_content}

**Similar Historical Vulnerability Patterns (for reference):**
${rag_context}

**Task:**
Perform a comprehensive static analysis covering:

1. **General Code Quality Issues:**
   - Syntax errors
   - Logic errors
   - Null pointer / resource leak risks
   - Race conditions
   - Performance issues
   - Code smells and bad practices

2. **Security Vulnerabilities:**
   - Compare with historical vulnerability patterns above
   - SQL Injection, XSS, Path Traversal, Hardcoded Secrets
   - Any other security issues found

**Output Format:**
{
  "has_issues": <true/false>,
  "issues": [
    {
      "category": "<security|bug|logic|performance|style>",
      "type": "<specific issue type>",
      "location": "<file:line or function>",
      "description": "<what is wrong>",
      "explanation": "<why this is a problem and potential impact>",
      "related_pattern": "<matching historical vulnerability pattern if security issue>"
    }
  ],
  "summary": "<brief summary of all issues found>"
}
"""
)


# ============================================================
# 用于 generate_cci 的 prompts（分析 diff/patch）
# ============================================================
SYSTEM_PROMPT_CCI = """You are a helpful software developer assistant specializing in software development lifecycle to help other developers understand characteristics of software patches."""
USER_PROMPT_CCI = Template(
    """You are given the following software patch:
${patch_content}

Provide an analysis describing the following characteristics:
1. Code Change Summary
2. Purpose of the Change
3. Implications of the Change

When analyzing the patch, focus on the ChangeCode (the actual code that was changed) rather than just the diff metadata. Identify what code was added, removed, or modified and explain its purpose and impact.

Provide the analysis in bullet point format for each characteristic. Each bullet point should start with a key point and then briefly describe a main idea or fact from the text. Ensure each point is concise and captures the essence of the main idea it's summarizing.

Here is an example of the desired format:
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
"""
)


# ============================================================
# 用于 generate_cci_code 的 prompts（直接分析代码）
# ============================================================
SYSTEM_PROMPT_CCI_CODE = """You are a helpful software developer assistant specializing in software development lifecycle to help other developers understand characteristics of source code."""
USER_PROMPT_CCI_CODE = Template(
    """You are given the following source code for analysis:
${code_content}

Provide an analysis describing the following characteristics:
1. Code Change Summary
2. Purpose of the Change
3. Implications of the Change

Provide the analysis in bullet point format for each characteristic. Each bullet point should start with a key point and then briefly describe a main idea or fact from the text. Ensure each point is concise and captures the essence of the main idea it's summarizing.

Here is an example of the desired format:
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
"""
)


# ============================================================
# 原有漏洞修复识别 prompts
# ============================================================
# SYSTEM_PROMPT_CAVFD = """You are a helpful software developer assistant specializing in vulnerability detection to help other developers understand characteristics of software patches and discover potential vulnerabilities."""
# USER_PROMPT_CAVFD = Template(
#     """You are given the following details for analysis:
# 1. **Patch Content:**
# \"\"\"
# ${patch_content}
# \"\"\"
#
# 2. **Three Aspect Analysis of the Patch:**
# \"\"\"
# ${three_aspect_content}
# \"\"\"
#
# 3. **Similar Historical Vulnerability Fix Information:**
# \"\"\"
# ${history_vuln_content}
# \"\"\"
#
# 4. **Three Aspect Analysis of the Historical Vulnerability Fix:**
# \"\"\"
# ${history_three_aspect_content}
# \"\"\"
#
# **Task:**
#
# 1. **Comparison:**
# - Carefully compare the current patch with the historical vulnerability fix to avoid bias.
# - Ensure that you consider the similarities and differences highlighted in the three aspect analyses.
#
# 2. **Analysis:**
# - Determine whether the current patch is intended to fix a vulnerability. You must provide evidence if you think its a vulnerability fix.
#
# Your output should follow below syntax:
# {
#  "analysis": "<Detailed analysis of whether the patch is to fix a vulnerability>",
#  "vulnerability_fix": "<yes or no>"
# }
# """)
#
# SYSTEM_PROMPT_CCI = """You are a helpful software developer assistant specializing in software development lifecycle to help other developers understand characteristics of software patches."""
# USER_PROMPT_CCI = Template(
#     """You are given the following software patch:
# \"\"\"
# ${patch_content}
# \"\"\"
#
# Provide an analysis describing the following characteristics:
# 1. Code Change Summary
# 2. Purpose of the Change
# 3. Implications of the Change
#
# Provide the analysis in bullet point format for each characteristic. Each bullet point should start with a key point and then briefly describe a main idea or fact from the text. Ensure each point is concise and captures the essence of the main idea it's summarizing.
#
# Here is an example of the desired format:
# \"\"\"
# 1. Code Change Summary
# - [Key Point]: <description>
# - [Optional Key Point]: <description>
# - [Optional Key Point]: <description>
#
# 2. Purpose of the Change
# - [Key Point]: <description>
# - [Optional Key Point]: <description>
# - [Optional Key Point]: <description>
#
# 3. Implications of the Change
# - [Key Point]: <description>
# - [Optional Key Point]: <description>
# - [Optional Key Point]: <description>
# \"\"\"
# """
# )
