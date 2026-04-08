import time
import pandas as pd
import requests
from utils import init_dashscope, get_embeddings_qwen, get_chroma_client, generate_cci
from config import Config

# 初始化DashScope API
init_dashscope()

# 根据CVEID从nvd查询对应漏洞信息，返回CVE description
def search_nvd_vulnerabilities(keyword, limit=10):
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": limit
    }
    headers = {
        "apiKey": Config.NVD_API_KEY,
    }
    try:
        response = requests.get(Config.NVD_API_URL, headers=headers, params=params)
        response.raise_for_status()
        print(response.json())
        # 这个睡眠时间不要太低 nvd有访问频率限制
        time.sleep(Config.NVD_API_DELAY)
        return response.json()['vulnerabilities'][0]['cve']['descriptions'][0]['value']
    except requests.exceptions.RequestException as e:
        print(f"Error accessing NVD API: {e}")
        return None

# 将所需信息写入数据库
def add_vf_to_collection(df, collection):
    collection.add(
        documents=df["three_aspect_response"].tolist(),
        embeddings=df["3aspect_embedding"].tolist(),
        metadatas=df[["vuln_id", "lang", "patch"]].to_dict(
            orient="records"
        )
    )
    return collection

# 进入生成CCI信息过程
now_num = 0

def process(row):
    global now_num
    patch = row['patch']
    cci = generate_cci(patch)
    now_num += 1
    print(now_num)
    return cci

# 进入获取CVE description过程
def cve_process(row):
    cve_info = search_nvd_vulnerabilities(row['vuln_id'])
    return cve_info

# 进入向量化CCI信息过程
def embed_process(row):
    three_aspect_embedding = row['three_aspect_response']
    aspect_embed = get_embeddings_qwen([three_aspect_embedding])
    return aspect_embed

# ========== 主流程 ==========
df = pd.read_parquet(Config.RAG_INPUT_PARQUET)

df['three_aspect_response'] = df.apply(process, axis=1)
df['cve_info'] = df.apply(cve_process, axis=1)

# 到这一步是完成了原始历史漏洞信息收集
df.to_parquet('without_embedding_leak_new.parquet')

# 将三方面意见作为向量嵌入
df["3aspect_embedding"] = df.apply(embed_process, axis=1)

df.to_parquet(Config.RAG_OUTPUT_PARQUET)

# 创建ChromaDB集合并写入数据
chroma_client = get_chroma_client(use_http=True)
collection = chroma_client.create_collection(name=Config.COLLECTION_NAME)

add_vf_to_collection(df, collection)

df.to_parquet('fin_leak.parquet')
