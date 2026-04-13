import sys
import time
from concurrent.futures import ThreadPoolExecutor

import uuid
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
def add_vf_to_collection(df, collection, batch_size=5000):
    ids = [str(uuid.uuid4()) for _ in range(len(df))]

    documents = [
        "" if pd.isna(doc) else str(doc)
        for doc in df["three_aspect_response"].tolist()
    ]

    embeddings = [
        emb[0].tolist()
        for emb in df["3aspect_embedding"].tolist()
    ]

    metadatas = df[["vuln_id", "patch"]].to_dict(orient="records")

    for start in range(0, len(df), batch_size):
        end = start + batch_size
        collection.add(
            documents=documents[start:end],
            embeddings=embeddings[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end]
        )

    return collection

# 进入生成CCI信息过程
now_num = 0
now_num_embed = 0

def process(row):
    global now_num
    patch = row['patch']
    cci = generate_cci(patch)
    now_num += 1
    print(f"nowCCInum:{now_num}")
    print(f"nowCCInum:{now_num}\n`process` returns:{cci}", file=sys.stderr)
    return cci

# 进入获取CVE description过程
def cve_process(row):
    cve_info = search_nvd_vulnerabilities(row['vuln_id'])
    return cve_info

# 进入向量化CCI信息过程
def embed_process(row):
    global now_num_embed
    three_aspect_embedding = row['three_aspect_response']
    aspect_embed = get_embeddings_qwen([three_aspect_embedding])
    now_num_embed+=1
    print(f"now_num_embed:{now_num_embed}")
    print(f"now_num_embed:{now_num_embed}\n`embed_process` returns:{aspect_embed}", file=sys.stderr)
    return aspect_embed

def parallel_apply_thread(df, func, column_name, max_workers=2):
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(func, [row for _, row in df.iterrows()]))
    df[column_name] = results
    return df

# ========== 主流程 ==========
df = pd.read_parquet(Config.RAG_INPUT_PARQUET)
print(df['patch'].size)
df = parallel_apply_thread(df, process, 'three_aspect_response', max_workers=2)

# 临时文件导出
df.to_parquet('without_embedding_leak_tmp.parquet')

df['cve_info'] = df.apply(cve_process, axis=1)

# # 到这一步是完成了原始历史漏洞信息收集
# df.to_parquet('without_embedding_leak_new.parquet')

# 将三方面意见作为向量嵌入
df = parallel_apply_thread(df, embed_process, "3aspect_embedding", max_workers=2)

df.to_parquet(Config.RAG_OUTPUT_PARQUET)

# 创建ChromaDB集合并写入数据
chroma_client = get_chroma_client(use_http=False)
collection = chroma_client.create_collection(name=Config.COLLECTION_NAME)

add_vf_to_collection(df, collection)

df.to_parquet('fin_leak.parquet')
