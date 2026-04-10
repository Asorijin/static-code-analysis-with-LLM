"""
tool.py - 交互式静态漏洞分析工具
支持直接输入代码或从文件读取，基于 RAG 向量检索辅助分析
静态检测 + 漏洞修复判断
"""

from utils import init_dashscope, generate_cci_code, retrieve_from_rag, generate_sa, generate_cavfd_code
import os
import json

init_dashscope()

# 命令常量
FILE_SEPARATOR = ","
BACK_CMD = "/back"
HELP_CMD = "/help"
QUIT_CMD = "/quit"


def static_analyze(code):
    """对代码进行静态漏洞分析 + 漏洞修复判断，结合 RAG 检索结果"""
    # 1. CCI 分析（针对代码）
    print("正在生成代码分析...")
    cci = generate_cci_code(code)
    if not cci:
        print("错误: 无法生成代码分析，API调用失败")
        return None
    print(f"代码分析完成: {cci[:100]}...")

    # 2. RAG 检索
    print("正在检索相似漏洞案例...")
    history_cci, history_cve_description = retrieve_from_rag(cci)
    print(f"检索到 {history_cve_description}")

    # 3. 静态分析 (SA)
    print("正在进行静态分析...")
    rag_context = f"历史漏洞模式:\n{history_cve_description}\n\nCCI分析:\n{history_cci}"
    sa_result = generate_sa(code, rag_context)

    # 4. 漏洞修复判断 (CAVFD)
    print("正在进行漏洞修复判断...")
    cavfd_result = generate_cavfd_code(code, cci, history_cci, history_cve_description)

    # 5. 合并输出
    try:
        combined = {
            "static_analysis": json.loads(sa_result) if sa_result else None,
            "vulnerability_fix": json.loads(cavfd_result) if cavfd_result else None
        }
        return json.dumps(combined, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, AttributeError):
        return f"SA Result:\n{sa_result}\n\nCAVFD Result:\n{cavfd_result}"


def show_help():
    """显示帮助信息"""
    print("\n" + "=" * 50)
    print("命令说明")
    print("=" * 50)
    print(f"  {HELP_CMD}  - 显示此帮助信息")
    print(f"  {BACK_CMD}  - 返回主菜单")
    print(f"  {QUIT_CMD}  - 退出程序")
    print("-" * 50)
    print("主菜单选项:")
    print("  1 - 直接输入代码")
    print("  2 - 从文件读取（多个文件用逗号分隔）")
    print("=" * 50)


def select_input_mode():
    """让用户选择输入模式"""
    print("\n" + "=" * 50)
    print("静态漏洞分析工具")
    print("=" * 50)
    print("1. 直接输入代码")
    print("2. 从文件读取")
    print(f"输入 {BACK_CMD} 返回此菜单，输入 {HELP_CMD} 查看所有命令")
    choice = input("请选择: ").strip()
    return choice


def input_code_mode():
    """直接输入代码模式"""
    print("\n请输入代码，输入完成后按Ctrl+Z+回车(Windows)结束输入")
    print("-" * 40)
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    code = "\n".join(lines)
    if code.strip():
        print(f"\n检测到代码长度: {len(code)} 字符")
        result = static_analyze(code)
        print(f"\n分析结果:\n{result}")
    else:
        print("未输入任何代码")


def input_files_mode():
    """从文件读取模式，文件路径用逗号分隔"""
    while True:
        print(f"\n请输入文件路径（多个文件用逗号分隔）")
        print(f"输入 {BACK_CMD} 返回主菜单，输入 {HELP_CMD} 查看所有命令")
        paths_input = input("文件路径: ").strip()

        if paths_input == BACK_CMD:
            return

        parts = paths_input.split(FILE_SEPARATOR)
        contents = []
        all_ok = True

        for path in parts:
            path = path.strip()
            if not path:
                continue
            if not os.path.isabs(path):
                path = os.path.join(os.getcwd(), path)
            if not os.path.exists(path):
                print(f"文件不存在: {path}，请重新输入")
                all_ok = False
                break
            try:
                with open(path, "r", encoding="utf-8") as f:
                    contents.append(f.read())
            except Exception as e:
                print(f"读取文件失败 {path}: {e}，请重新输入")
                all_ok = False
                break

        if all_ok and contents:
            for i, content in enumerate(contents, 1):
                print(f"\n{'='*50}")
                print(f"分析第 {i} 个文件")
                print(f"{'='*50}")
                result = static_analyze(content)
                print(f"\n分析结果:\n{result}")
            break


def main():
    while True:
        choice = select_input_mode()

        if choice == "1":
            input_code_mode()
        elif choice == "2":
            input_files_mode()
        elif choice == BACK_CMD:
            print("已是主菜单")
        elif choice == HELP_CMD:
            show_help()
        elif choice == QUIT_CMD:
            print("退出程序")
            break
        else:
            print("无效选择，请输入 1 或 2")


if __name__ == "__main__":
    main()
