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
    
    def clear_and_create_collection(self, collection_name):
        """Delete existing collection and create a new one."""
        try:
            # Try to delete existing collection
            self.client.delete_collection(collection_name)
        except (ValueError, Exception):
            # Collection doesn't exist, which is fine
            pass
        
        # Create new collection
        return self.client.create_collection(collection_name)
    
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
    
    def store_chunks_with_metadata(self, collection_name, chunks, source_file, headers):
        """Store text chunks with metadata about source file."""
        collection = self.create_collection(collection_name)
        
        # Prepare documents and unique IDs that include source file
        documents = chunks
        ids = [f"{source_file}_chunk_{i}" for i in range(len(chunks))]
        
        # Prepare metadata for each chunk
        metadatas = []
        for i in range(len(chunks)):
            metadata = {
                "source_file": source_file,
                "chunk_index": i,
                "title": headers.get('title', ''),
                "filetags": ','.join(headers.get('filetags', [])),
                "id": headers.get('id', '')
            }
            metadatas.append(metadata)
        
        # Add documents to collection with metadata
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
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
