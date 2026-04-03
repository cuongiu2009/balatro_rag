import chromadb
import logging

class ChromaDBClient:
    def __init__(self, path="./chroma_db", collection_name="balatro_knowledge_base"):
        try:
            self.client = chromadb.PersistentClient(path=path)
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logging.info(f"ChromaDB client initialized and collection '{collection_name}' is ready.")
        except Exception as e:
            logging.error(f"Failed to initialize ChromaDB client: {e}")
            self.client = None
            self.collection = None

    def get_or_create_collection(self, name: str):
        # This method is now redundant if collection_name is passed to init
        # but keep it in case it's used elsewhere for dynamic collection creation
        try:
            return self.client.get_or_create_collection(name=name)
        except Exception as e:
            logging.error(f"Failed to get or create collection '{name}': {e}")
            return None

    def add_documents(self, documents, metadatas, ids):
        if not self.collection:
            logging.error("ChromaDB collection is not available.")
            return False
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logging.info(f"Added {len(documents)} documents to the collection.")
            return True
        except Exception as e:
            logging.error(f"Failed to add documents to ChromaDB: {e}")
            return False

    def query(self, query_texts, n_results=5):
        if not self.collection:
            logging.error("ChromaDB collection is not available.")
            return None
        try:
            results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results
            )
            logging.info(f"ChromaDB query successful.")
            return results
        except Exception as e:
            logging.error(f"Failed to query ChromaDB: {e}")
            return None

# Example usage:
if __name__ == '__main__':
    # This is for demonstration and testing purposes.
    logging.basicConfig(level=logging.INFO)
    chroma_client = ChromaDBClient()
    if chroma_client.collection:
        chroma_client.add_documents(
            documents=["This is a test document about the 'Joker' card.", "This is a test document about 'Straights'."],
            metadatas=[{"source": "test"}, {"source": "test"}],
            ids=["test_id1", "test_id2"]
        )
        results = chroma_client.query(query_texts=["What is a Joker?"], n_results=1)
        print("Query results:", results)
