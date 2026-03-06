import time
from http import HTTPStatus
import chromadb
from prompts import SYSTEM_PROMPT_CCI, USER_PROMPT_CCI
import os
import pandas as pd
from tqdm import tqdm
from utils import process_patch
import dashscope
from openai import OpenAI
import requests


dashscope.api_key='needed'
NVD_API_KEY='needed'
# 根据CVEID从nvd查询对应漏洞信息，返回CVE description
def search_nvd_vulnerabilities(keyword, limit=10):
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "keywordSearch": keyword,
        "resultsPerPage": limit
    }
    headers={
        "apiKey": NVD_API_KEY,
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print(response.json())
        # 这个睡眠时间不要太低 nvd有访问频率限制
        time.sleep(1)
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
# 与LLM交互
def inference_llm(system_prompt, user_prompt, cache_dir=None):
    if cache_dir:
        if os.path.exists(cache_dir):
            print(f"Cache found at {cache_dir}")
            with open(cache_dir, "r") as f:
                return f.read()
    try:
        client = OpenAI(
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
            api_key='needed',
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        response = client.chat.completions.create(
            model='qwen-turbo-1101',
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        content = response.choices[0].message.content
        print(content)
        return content
    except Exception as ex:
        print(ex)
        return None
#根据代码内容生成CCI信息
def generate_cci(patch):
    user_prompt = USER_PROMPT_CCI.substitute(patch_content = patch)
    system_prompt = SYSTEM_PROMPT_CCI
    cci = inference_llm(system_prompt, user_prompt)
    return cci

#进入生成CCI信息过程
now_num=0
def process(row):

    global now_num

    patch = row['patch']
    # TODO：修改正则式
    processed_patch = process_patch(patch)
    cci = generate_cci(processed_patch)
    now_num += 1

    print(now_num)
    return cci
#进入获取CVE description过程
def cve_process(row):
    cve_info = search_nvd_vulnerabilities(row['vuln_id'])
    return cve_info

#进入向量化CCI信息过程
def embed_process(row):
    three_aspect_embedding = row['three_aspect_response']
    aspect_embed = get_embeddings_qwen([three_aspect_embedding])
    return aspect_embed

def embed(texts):
    inputs = texts
    resp = dashscope.TextEmbedding.call(
        model="text-embedding-v4",
        input=inputs
    )
    if resp['status_code'] == HTTPStatus.OK:
        embeddings = resp["output"]["embeddings"][0]["embedding"]
        return embeddings
    else:
        print("err!")
        print(resp)
        return []


def get_embeddings_qwen(texts, batch_size=1):
    embedding_results = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i : i + batch_size]
        # Process the text to replace newlines with spaces and create batched requests
        # API call with batched input
        if batch_texts is None:
            batch_texts = ["None"]

        batch_texts = [(text or "").replace("\n", " ") for text in batch_texts]
        embeddings = embed(batch_texts)
        embedding_results.append(embeddings)

    return embedding_results

dataset_dir="without_embedding_leak.parquet"

df = pd.read_parquet(dataset_dir)

df['three_aspect_response'] = df.apply(process, axis=1)
df['cve_info']=df.apply(cve_process, axis=1)
# df['lang'] = df.apply(lang_process, axis=1)

#到这一步是完成了原始历史漏洞信息收集
df.to_parquet('without_embedding_leak_new.parquet')

#将三方面意见作为向量嵌入
df["3aspect_embedding"] = df.apply(embed_process,axis=1)

df.to_parquet('with_embedding_leak.parquet')

chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.create_collection(
    name=f"three_aspect_summary_collection_gte-Qwen2-7B-instruct"
)

add_vf_to_collection(df, collection)

df.to_parquet('fin_leak.parquet')
