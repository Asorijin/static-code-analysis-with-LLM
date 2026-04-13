import os
from pathlib import Path


class Config:
    """项目配置类"""

    # ========== API Keys ==========
    # 从环境变量读取，默认使用占位符
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "needed")
    NVD_API_KEY = os.getenv("NVD_API_KEY", "needed")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", DASHSCOPE_API_KEY)

    # ========== LLM Configuration ==========
    LLM_MODEL = "qwen-turbo-1101"
    LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # ========== Embedding Configuration ==========
    EMBEDDING_MODEL = "text-embedding-v4"
    EMBEDDING_BATCH_SIZE = 1

    # ========== ChromaDB Configuration ==========
    # 本地持久化存储
    CHROMA_DB_PATH = "./chroma_db"
    # HTTP客户端
    CHROMA_HOST = "localhost"
    CHROMA_PORT = 8000

    # ========== Vector Collection ==========
    COLLECTION_NAME = "three_aspect_summary_collection_gte-Qwen2-7B-instruct"

    # ========== Detection Parameters ==========
    DEFAULT_LANG = "Java"
    TOP_K_RESULTS = 1

    # ========== Data Files ==========
    # RAG构建
    RAG_INPUT_PARQUET = "without_embedding_leak.parquet"
    RAG_OUTPUT_PARQUET = "with_embedding_leak.parquet"

    # 漏洞检测
    TEST_DATASET = "testing_codebase.parquet"
    OUTPUT_CSV = "fin.csv"
    GROUND_TRUTH_XLSX = "leak.xlsx"

    # ========== NVD API ==========
    NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    NVD_API_LIMIT = 10
    NVD_API_DELAY = 0.8  # 秒，NVD有访问频率限制

    # ========== 路径配置 ==========
    PROJECT_ROOT = Path(__file__).parent
