from prompts import SYSTEM_PROMPT_CAVFD, USER_PROMPT_CAVFD
import pandas as pd
from utils import init_dashscope, inference_llm, get_embeddings_qwen, get_chroma_client, generate_cci
from config import Config

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
def query_collection_lang(collection_name, query_embeddings, lang="Java"):
    client = get_chroma_client()
    collection = client.get_collection(collection_name)
    result = collection.query(
        query_embeddings=query_embeddings, n_results=1, where={"lang": lang}
    )
    return result


# 将输入CCI向量化，与数据库比对
def retrieve_from_rag(cci, lang="Java"):
    collection_name = Config.COLLECTION_NAME
    cci_embedding = get_embeddings_qwen([cci])
    cci_embedding = cci_embedding[0]
    exp_result = query_collection_lang(collection_name, cci_embedding, lang)
    # 三角度分析
    retrieved_3aspect = exp_result["documents"][0][0]
    # 检索CVE描述
    retrieved_cve_description = exp_result["metadatas"][0][0]["cve_info"]
    return retrieved_3aspect, retrieved_cve_description


# 进入处理输入流程
def process(row):
    patch = row['patch']
    cci = generate_cci(patch)
    history_cci, history_cve_description = retrieve_from_rag(cci)
    cavfd = generate_cavfd(patch, cci, history_cci, history_cve_description)
    print(cavfd)
    return cavfd


dataset_dir = Config.TEST_DATASET

df = pd.read_parquet(dataset_dir)
df['patch'] = df['patch'].fillna('').astype(str)
df['cavfd'] = df.apply(process, axis=1)

df.to_csv(Config.OUTPUT_CSV)
