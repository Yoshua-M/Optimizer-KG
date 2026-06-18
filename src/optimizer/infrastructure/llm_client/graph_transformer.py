import os

from dotenv import load_dotenv
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
graph_transformer = LLMGraphTransformer(llm=llm)
