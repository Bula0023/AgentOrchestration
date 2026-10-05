from langchain_ollama import ChatOllama
import os
import openai
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv



load_dotenv()
ollama_url = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434"
)
openai.api_key = os.environ.get("OPENAI_API_KEY", "Api key not found")
# llm = ChatOllama(
#     model="qwen3:4b",
#     temperature=0,
#     base_url=ollama_url
# )
# eval_llm = ChatOllama(
#     model="qwen3:1.7b",
#     temperature=0,
#     base_url=ollama_url
# )
llm = ChatOpenAI(
    model="gpt-6-sol",
    # temperature=0,
    api_key=openai.api_key ,
)

eval_llm = ChatOpenAI(
    model="gpt-6-luna",
    # temperature=0,
    api_key=openai.api_key ,
)