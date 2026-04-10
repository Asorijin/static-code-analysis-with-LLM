from prompts import SYSTEM_PROMPT_CAVFD, USER_PROMPT_CAVFD
import pandas as pd
from utils import init_dashscope, inference_llm, get_embeddings_qwen, get_chroma_client, generate_cci, generate_cci_code, generate_sa, generate_cavfd_code
from config import Config
import json


def extract_code_from_patch(patch):
    """从diff格式的patch中提取代码部分（+/-行和上下文代码）"""
    lines = patch.split('\n')
    code_lines = []
    for line in lines:
        # 跳过 diff 元数据行（---, +++, @@, File:, Class:, Method:, Signature:）
        if line.startswith('---') or line.startswith('+++') or line.startswith('@@') \
                or line.startswith('File:') or line.startswith('Class:') \
                or line.startswith('Method:') or line.startswith('Signature:'):
            continue
        code_lines.append(line)
    return '\n'.join(code_lines)

# 初始化DashScope API
init_dashscope()

# 生成最终cavfd信息
def generate_cavfd(patch, cci, history_cci, history_cve_description):
    user_prompt = USER_PROMPT_CAVFD.substitute(
        patch_content=patch,
        three_aspect_content=cci,
        history_three_aspect_content=history_cci,
        history_vuln_content=history_cve_description
    )
    system_prompt = SYSTEM_PROMPT_CAVFD
    cavfd = inference_llm(system_prompt, user_prompt)
    return cavfd


# 在向量数据库中查询相似漏洞
def query_collection_lang(collection_name, query_embeddings):
    client = get_chroma_client()
    collection = client.get_collection(collection_name)
    result = collection.query(
        query_embeddings=query_embeddings, n_results=1
    )
    return result


# 将输入CCI向量化，与数据库比对
def retrieve_from_rag(cci, lang="Java"):
    collection_name = Config.COLLECTION_NAME
    cci_embedding = get_embeddings_qwen([cci])
    cci_embedding = cci_embedding[0]
    exp_result = query_collection_lang(collection_name, cci_embedding)
    # 三角度分析
    retrieved_3aspect = exp_result["documents"][0][0]
    # 检索CVE描述（使用vuln_id作为回退，因为cve_info未存储）
    retrieved_cve_description = exp_result["metadatas"][0][0].get("cve_info", exp_result["metadatas"][0][0].get("vuln_id", ""))
    return retrieved_3aspect, retrieved_cve_description


# 进入处理输入流程（基于diff/patch的CCI分析）
def process(row):
    patch = row['patch']
    cci = generate_cci(patch)
    history_cci, history_cve_description = retrieve_from_rag(cci)
    cavfd = generate_cavfd(patch, cci, history_cci, history_cve_description)
    print(cavfd)
    return cavfd


# 进入直接分析代码的流程（从diff中提取代码后分析）
def process_code_direct(row):
    patch = row['patch']
    code = extract_code_from_patch(patch)
    cci = generate_cci_code(code)
    history_cci, history_cve_description = retrieve_from_rag(cci)

    # 静态分析 (SA)
    rag_context = f"历史漏洞模式:\n{history_cve_description}\n\nCCI分析:\n{history_cci}"
    sa_result = generate_sa(code, rag_context)

    # 漏洞修复判断 (CAVFD)
    cavfd_result = generate_cavfd_code(code, cci, history_cci, history_cve_description)

    # 合并输出
    try:
        combined = {
            "static_analysis": json.loads(sa_result) if sa_result else None,
            "vulnerability_fix": json.loads(cavfd_result) if cavfd_result else None
        }
        result = json.dumps(combined, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, AttributeError):
        result = f"SA Result:\n{sa_result}\n\nCAVFD Result:\n{cavfd_result}"

    print(result)
    return result


dataset_dir = Config.TEST_DATASET

df = pd.read_parquet(dataset_dir)
df['patch'] = df['patch'].fillna('').astype(str)
df['cavfd'] = df.apply(process_code_direct, axis=1)

df.to_csv(Config.OUTPUT_CSV)
