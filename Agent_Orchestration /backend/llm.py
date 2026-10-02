from langchain_ollama import ChatOllama
import os

ollama_url = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)
llm = ChatOllama(
    model="qwen3:4b",
    temperature=0,
    base_url=ollama_url
)
eval_llm = ChatOllama(
    model="qwen3:1.7b",
    temperature=0,
    base_url=ollama_url
)