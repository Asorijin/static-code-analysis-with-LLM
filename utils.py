from config import Config

def init_dashscope():
    """初始化DashScope API"""
    import dashscope
    dashscope.api_key = Config.DASHSCOPE_API_KEY
    
def get_openai_client():
    """获取OpenAI客户端（兼容DashScope）"""
    from openai import OpenAI
    return OpenAI(
        api_key=Config.DASHSCOPE_API_KEY,
        base_url=Config.LLM_BASE_URL
    )

def get_openai_response_content(system_prompt, user_prompt):
    """获取OpenAI响应内容"""
    client = get_openai_client()
    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
    )
    content = response.choices[0].message.content
    return content

def get_chroma_client(use_http=False):
    """获取ChromaDB客户端

    Args:
        use_http: 是否使用HTTP客户端（构建RAG时用），否则使用本地持久化
    """
    import chromadb
    if use_http:
        return chromadb.HttpClient(host=Config.CHROMA_HOST, port=Config.CHROMA_PORT)
    return chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)

def embed(texts):
    """文本向量化"""
    import dashscope
    from http import HTTPStatus
    resp = dashscope.TextEmbedding.call(
        model=Config.EMBEDDING_MODEL,
        input=texts
    )
    if resp['status_code'] == HTTPStatus.OK:
        return resp["output"]["embeddings"][0]["embedding"]
    else:
        print("Embedding error:", resp)
        return []

def get_embeddings_qwen(texts, batch_size=1):
    """批量文本向量化"""
    from tqdm import tqdm
    embedding_results = []
    for i in tqdm(range(0, len(texts), batch_size)):
        batch_texts = texts[i : i + batch_size]
        if batch_texts is None:
            batch_texts = ["None"]
        batch_texts = [(text or "").replace("\n", " ") for text in batch_texts]
        embeddings = embed(batch_texts)
        embedding_results.append(embeddings)
    return embedding_results


def inference_llm(system_prompt, user_prompt, cache_dir=None):
    """与LLM交互"""
    import os
    if cache_dir:
        if os.path.exists(cache_dir):
            print(f"Cache found at {cache_dir}")
            with open(cache_dir, "r") as f:
                return f.read()
    try:
        return get_openai_response_content(system_prompt, user_prompt)
    except Exception as ex:
        print(ex)
        return None

# 根据代码内容生成CCI信息
def generate_cci(patch):
    from prompts import SYSTEM_PROMPT_CCI, USER_PROMPT_CCI
    user_prompt = USER_PROMPT_CCI.substitute(patch_content=patch)
    system_prompt = SYSTEM_PROMPT_CCI
    cci = inference_llm(system_prompt, user_prompt)
    return cci