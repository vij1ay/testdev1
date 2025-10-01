from langchain_core.tools import tool
from langchain_core.runnables import ensure_config

from llm_utils import get_chroma_db, chroma_rag_retrieve
from app_logger import logger


# Ensure the Chroma DB is initialized
chroma_db = get_chroma_db("testimonials")


@tool
def testimonials_tool(thread_id: str, query, top_k=2):
    """Access Testimonials and provide detailed testimonial based on the context, return top k results in order as list[Document, score]. Lower the score the better the match."""
    config = ensure_config()
    thread_id = config.get("configurable", {}).get("thread_id", "unknown")
    logger.info(
        f"Tool call: testimonials_tool - thread: {thread_id}, query: {query}")
    retrieved_docs = chroma_rag_retrieve(chroma_db, query, top_k=top_k)
    return retrieved_docs
