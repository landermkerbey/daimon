import chromadb
from pathlib import Path


class ChromaManager:
    """Manager for ChromaDB vector database operations."""
    
    def __init__(self, db_path):
        """Initialize ChromaManager with database path."""
        self.db_path = Path(db_path)
        # Create ChromaDB client with persistent storage
        self.client = chromadb.PersistentClient(path=str(self.db_path))
    
    def create_collection(self, collection_name):
        """Create a new collection in the database."""
        try:
            # Try to get existing collection first
            collection = self.client.get_collection(collection_name)
            return collection
        except (ValueError, Exception):
            # Collection doesn't exist, create it
            collection = self.client.create_collection(collection_name)
            return collection
    
    def store_chunks(self, collection_name, chunks):
        """Store text chunks in the specified collection."""
        collection = self.create_collection(collection_name)
        
        # Prepare documents and IDs
        documents = chunks
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        
        # Add documents to collection
        collection.add(
            documents=documents,
            ids=ids
        )
        
        return len(chunks)
    
    def query_collection(self, collection_name, query_text, n_results=5):
        """Query a collection for similar content."""
        try:
            collection = self.client.get_collection(collection_name)
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except (ValueError, Exception):
            # Collection doesn't exist or other error
            return {"documents": [], "metadatas": [], "distances": [], "ids": []}
