import chromadb
import os
import sys

# Add the parent directory to the sys.path to allow imports from rag_model
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from rag_model.data_processor import process_raw_data, RAW_GAME_DATA
from rag_model.chromadb_client import ChromaDBClient  # Assuming ChromaDBClient handles collection creation/connection

# Configuration for ChromaDB
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "balatro_knowledge_base"

def build_knowledge_base():
    """
    Builds the ChromaDB knowledge base using processed entity chunks.
    """
    print(f"Starting to build knowledge base in {CHROMA_DB_PATH}...")

    # 1. Process raw game data into entity-based chunks
    print("Processing raw game data into chunks...")
    chunks = process_raw_data(RAW_GAME_DATA)
    print(f"Processed {len(chunks)} chunks.")

    if not chunks:
        print("No chunks to add to the knowledge base. Exiting.")
        return

    # 2. Initialize ChromaDB client
    chroma_client_instance = ChromaDBClient(path=CHROMA_DB_PATH, collection_name=COLLECTION_NAME)
    if not chroma_client_instance.collection:
        print("Failed to get ChromaDB collection. Exiting.")
        return
    collection = chroma_client_instance.collection
    print(f"ChromaDB collection '{COLLECTION_NAME}' ready.")

    # Prepare data for ChromaDB
    documents = [chunk["content"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]
    ids = [f"{m['entity_type']}_{m['name'].replace(' ', '_')}_{i}" for i, m in enumerate(metadatas)] # Unique ID generation

    # 3. Add chunks to ChromaDB (ChromaDB handles embedding internally with default Sentence Transformers)
    print(f"Adding {len(documents)} documents to ChromaDB collection '{COLLECTION_NAME}'...")
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    print("Knowledge base built successfully!")
    print(f"Total documents in collection: {collection.count()}")

if __name__ == "__main__":
    build_knowledge_base()
