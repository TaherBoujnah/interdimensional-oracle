import json
import os
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

DATA_DIR = "data"
DB_DIR = "chroma_db"

def load_and_format_data():
    """Reads JSON files and converts them into LangChain Documents."""
    documents = []
    
    with open(os.path.join(DATA_DIR, "characters.json"), "r", encoding="utf-8") as f:
        characters = json.load(f)
        for char in characters:
            content = f"Character Name: {char['name']}. Status: {char['status']}. Species: {char['species']}. Origin: {char['origin']['name']}. Location: {char['location']['name']}."
            metadata = {"source": f"Character: {char['name']}", "type": "character", "url": char['url']}
            documents.append(Document(page_content=content, metadata=metadata))
            
    print(f"Loaded {len(characters)} characters.")
    return documents

def main():
    print("Formatting data...")
    docs = load_and_format_data()
    
    print("Initializing Local HuggingFace Embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Building Vector Database ")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print(f" Database built successfully in the '{DB_DIR}' folder!")

if __name__ == "__main__":
    main()