class ChunkingEngine:
    """Engine for splitting content into chunks for vector embedding."""
    
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        """Initialize chunking engine with size and overlap parameters."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def chunk_content(self, content):
        """Split content into chunks and return as list."""
        if len(content) <= self.chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            # Calculate end position for this chunk
            end = start + self.chunk_size
            
            # Extract the chunk
            chunk = content[start:end]
            chunks.append(chunk)
            
            # If this is the last chunk, we're done
            if end >= len(content):
                break
            
            # Move start position forward, accounting for overlap
            # Ensure we always make progress to avoid infinite loops
            step = max(1, self.chunk_size - self.chunk_overlap)
            start = start + step
        
        return chunks
