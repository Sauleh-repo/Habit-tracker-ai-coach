import os
from dotenv import load_dotenv

# LangChain components
from langchain_community.document_loaders import DirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# --- THIS IMPORT PATH IS NOW CORRECT ---
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# --- Configuration ---
load_dotenv()
KNOWLEDGE_BASE_DIR = "knowledge_base"
CHROMA_DB_DIR = "chroma_db"

def main():
    print("Starting data ingestion process...")

    print(f"Loading documents from '{KNOWLEDGE_BASE_DIR}'...")
    loader = DirectoryLoader(KNOWLEDGE_BASE_DIR, glob="**/*.txt", show_progress=True)
    documents = loader.load()
    if not documents:
        print("No documents found. Please add text files to the 'knowledge_base' folder.")
        return
    print(f"Loaded {len(documents)} documents.")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks.")

    print("Initializing embedding model...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    print(f"Creating and persisting vector database to '{CHROMA_DB_DIR}'...")
    db = Chroma.from_documents(
        texts, 
        embeddings, 
        persist_directory=CHROMA_DB_DIR
    )
    
    print("Data ingestion complete!")
    print(f"Vector database created with {db._collection.count()} entries.")

if __name__ == "__main__":
    main()