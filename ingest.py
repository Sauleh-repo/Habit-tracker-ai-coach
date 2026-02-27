import os
from typing import List
from dotenv import load_dotenv

from google import genai
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.embeddings import Embeddings

load_dotenv()

KNOWLEDGE_BASE_DIR = "knowledge_base"
CHROMA_DB_DIR = "chroma_db"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

class GeminiEmbeddingsWrapper(Embeddings):
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = "models/gemini-embedding-001"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        responses = self.client.models.embed_content(
            model=self.model_name,
            contents=texts,
            config={'task_type': 'retrieval_document'}
        )
        return [item.values for item in responses.embeddings]

    def embed_query(self, text: str) -> List[float]:
        response = self.client.models.embed_content(
            model=self.model_name,
            contents=text,
            config={'task_type': 'retrieval_query'}
        )
        return response.embeddings[0].values

def main():
    if not GOOGLE_API_KEY:
        return

    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
    texts = text_splitter.split_documents(documents)

    custom_embeddings = GeminiEmbeddingsWrapper(api_key=GOOGLE_API_KEY)

    try:
        Chroma.from_documents(
            documents=texts, 
            embedding=custom_embeddings, 
            persist_directory=CHROMA_DB_DIR
        )
    except Exception as e:
        pass

if __name__ == "__main__":
    main()