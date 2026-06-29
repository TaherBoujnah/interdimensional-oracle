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
    
    
    if os.path.exists(os.path.join(DATA_DIR, "characters.json")):
        with open(os.path.join(DATA_DIR, "characters.json"), "r", encoding="utf-8") as f:
            characters = json.load(f)
            for char in characters:
                content = f"Character Name: {char['name']}. Status: {char['status']}. Species: {char['species']}. Origin: {char['origin']['name']}. Location: {char['location']['name']}."
                metadata = {"source": f"Character: {char['name']}", "type": "character", "url": char['url']}
                documents.append(Document(page_content=content, metadata=metadata))
        print(f"Loaded {len(characters)} characters.")

    
    if os.path.exists(os.path.join(DATA_DIR, "episodes.json")):
        with open(os.path.join(DATA_DIR, "episodes.json"), "r", encoding="utf-8") as f:
            episodes = json.load(f)
            for ep in episodes:
                content = f"Episode Name: {ep['name']}. Air Date: {ep['air_date']}. Episode Code: {ep['episode']}."
                metadata = {"source": f"Episode: {ep['name']}", "type": "episode", "url": ep['url']}
                documents.append(Document(page_content=content, metadata=metadata))
        print(f"Loaded {len(episodes)} episodes.")

    
    if os.path.exists(os.path.join(DATA_DIR, "locations.json")):
        with open(os.path.join(DATA_DIR, "locations.json"), "r", encoding="utf-8") as f:
            locations = json.load(f)
            for loc in locations:
                content = f"Location Name: {loc['name']}. Type: {loc['type']}. Dimension: {loc['dimension']}."
                metadata = {"source": f"Location: {loc['name']}", "type": "location", "url": loc['url']}
                documents.append(Document(page_content=content, metadata=metadata))
        print(f"Loaded {len(locations)} locations.")

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